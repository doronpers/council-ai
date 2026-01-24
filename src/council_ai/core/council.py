# src/council_ai/core/council.py
"""
Council - The Core Advisory Council Engine

The Council class orchestrates multiple personas to provide
comprehensive advice, reviews, and decision support.
"""

from __future__ import annotations

import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from enum import Enum
from typing import Any, AsyncIterator, Callable, Dict, List, Optional, Tuple, Union
from uuid import uuid4

from pydantic import BaseModel

from ..providers import (
    LLMManager,
    LLMProvider,
    get_llm_manager,
    get_provider,
    normalize_model_params,
    validate_model_params,
)
from .config import get_api_key
from .persona import Persona, PersonaManager, get_persona_manager
from .reasoning import ReasoningMode, get_reasoning_prompt, get_reasoning_suffix
from .schemas import SynthesisSchema
from .session import ConsultationResult, MemberResponse, Session
from .strategies import get_strategy

logger = logging.getLogger(__name__)

ALL_MEMBERS_FAILED_MESSAGE = "All council members failed to respond; see individual error messages."


class ConsultationMode(str, Enum):
    """How the council responds to queries."""

    INDIVIDUAL = "individual"  # Each member responds separately
    SEQUENTIAL = "sequential"  # Members respond in order, seeing previous responses
    SYNTHESIS = "synthesis"  # Individual responses + synthesized summary
    DEBATE = "debate"  # Members can respond to each other
    VOTE = "vote"  # Members vote on a decision


class CouncilConfig(BaseModel):
    """Configuration for a Council instance."""

    name: str = "Advisory Council"
    description: str = ""
    mode: ConsultationMode = ConsultationMode.SYNTHESIS
    max_tokens_per_response: int = 1000
    temperature: float = 0.7
    include_reasoning: bool = True
    include_confidence: bool = True
    synthesis_prompt: Optional[str] = None
    synthesis_provider: Optional[str] = None
    synthesis_model: Optional[str] = None
    synthesis_max_tokens: Optional[int] = None
    context_window: int = 10  # Number of previous exchanges to include
    # Optional structured-output flag; if True, attempt structured then fallback
    use_structured_output: bool = False
    # When exporting, include enabled flags for members
    export_enabled_state: bool = False
    # Enable separate consensus analysis pass
    enable_analysis: bool = True
    # Web search and reasoning capabilities
    enable_web_search: bool = False  # Enable web search for consultations
    web_search_provider: Optional[str] = None  # "tavily", "serper", "google"
    reasoning_mode: Optional[str] = (
        "chain_of_thought"  # Default to chain_of_thought to show thinking process
    )
    # Progressive synthesis: start synthesis as responses arrive (streaming mode only, optional)
    progressive_synthesis: bool = False  # If True, start synthesis with partial responses

    # Timeout configurations (in seconds)
    member_timeout: float = 120.0  # Timeout for individual member responses (adjusted per provider)
    synthesis_timeout: float = 180.0  # Timeout for synthesis generation
    total_consultation_timeout: Optional[float] = None  # Overall consultation timeout (optional)

    # Retry configurations
    max_retries: int = 3  # Maximum retry attempts for transient failures
    retry_base_delay: float = 1.0  # Initial delay between retries in seconds
    retry_max_delay: float = 60.0  # Maximum delay between retries in seconds
    retry_exponential_factor: float = 2.0  # Backoff multiplier


class Council:
    """
    An advisory council composed of multiple AI personas.

    The Council orchestrates conversations with multiple personas,
    synthesizes their perspectives, and provides comprehensive advice.

    Key Features:
    - Personas can use various LLM providers simultaneously
    - Each persona can have unique model/provider settings
    - Automatic fallback to available LLM providers
    - Heterogeneous councils: different personas use different providers

    Example:
        council = Council(api_key="your-key", provider="anthropic")
        council.add_member("DR")  # Uses Claude Opus (if available)
        council.add_member("DK")  # Uses GPT-4 Turbo (if available)
        council.add_member("AG")  # Uses council default provider

        result = council.consult("Should we redesign our API?")
        print(result.synthesis)
        for response in result.responses:
            print(f"{response.persona.emoji} {response.persona.name}: {response.content}")
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        provider: str = "anthropic",
        config: Optional[CouncilConfig] = None,
        persona_manager: Optional[PersonaManager] = None,
        model: Optional[str] = None,
        base_url: Optional[str] = None,
        endpoint: Optional[str] = None,
        history: Optional[Any] = None,
    ):
        """
        Initialize a Council.

        Args:
            api_key: API key for the default LLM provider (or set via environment)
            provider: Default LLM provider name ("anthropic", "openai", etc.)
                     Individual personas can override this with their own providers
            config: Council configuration
            persona_manager: Custom persona manager (uses global if None)
            model: Model name override
            base_url: Base URL override
            endpoint: Backward-compatible alias for base_url
            history: ConsultationHistory instance for auto-saving (optional)
        """
        self.config = config or CouncilConfig()
        if base_url is None and endpoint is not None:
            base_url = endpoint
        self._persona_manager = persona_manager or get_persona_manager()
        self._members: Dict[str, Persona] = {}
        self._provider: Optional[LLMProvider] = None
        self._llm_manager: Optional[LLMManager] = None
        self._provider_name = provider
        self._api_key = api_key
        self._model = model
        self._base_url = base_url
        self._provider_cache: Dict[tuple[str, Optional[str], Optional[str]], LLMProvider] = {}
        self._sessions: List[Session] = []
        self._current_session: Optional[Session] = None
        self._history = history
        self._domain_id: Optional[str] = None

        # Web search tool (initialized lazily)
        self._web_search_tool: Optional[Any] = None
        # Web search cache: query -> enhanced context (per consultation)
        self._web_search_cache: Dict[str, Optional[str]] = {}

        # Callbacks for extensibility
        # Pre-consult hooks receive (query, context) and must return (query, context)
        self._pre_consult_hooks: List[Callable[[str, Optional[str]], Tuple[str, Optional[str]]]] = (
            []
        )
        # Post-consult hooks receive and return ConsultationResult
        self._post_consult_hooks: List[Callable[[ConsultationResult], ConsultationResult]] = []
        # Response hooks process each member's raw content string
        self._response_hooks: List[Callable[[Persona, str], str]] = []

        # Add default members: MD (Martin Dempsey), DK (Daniel Kahneman), JT (Julian Treasure), PH (Pablos Holman)
        default_members = ["MD", "DK", "JT", "PH"]
        for persona_id in default_members:
            try:
                self.add_member(persona_id)
            except ValueError:
                # Skip if persona not found (shouldn't happen for built-in personas)
                logger.warning(f"Default persona '{persona_id}' not found, skipping")

        # Warm up providers for default members (lazy, happens on first consult)
        self._providers_warmed = False

    @classmethod
    def for_domain(
        cls, domain: str, api_key: Optional[str] = None, provider: str = "anthropic", **kwargs
    ) -> "Council":
        """
        Create a council pre-configured for a specific domain.

        Args:
            domain: Domain name ("coding", "business", "creative", etc.)
            api_key: API key for the LLM provider
            provider: LLM provider name

        Returns:
            Configured Council instance
        """
        from ..domains import get_domain

        domain_config = get_domain(domain)
        council = cls(api_key=api_key, provider=provider, **kwargs)
        council._domain_id = domain
        council.config.name = domain_config.name
        council.config.description = domain_config.description

        for persona_id in domain_config.default_personas:
            try:
                council.add_member(persona_id)
            except ValueError:
                # Skip if persona not found
                continue

        return council

    def _get_llm_manager(self) -> LLMManager:
        """Get or create the LLMManager."""
        if self._llm_manager is None:
            self._llm_manager = get_llm_manager(
                preferred_provider=self._provider_name,
                api_key=self._api_key,
                model=self._model,
                base_url=self._base_url,
            )
        return self._llm_manager

    def _get_provider(self, fallback: bool = True) -> LLMProvider:
        """
        Get or create the default LLM provider with robust fallback mechanism.

        This is the default provider used by personas that don't specify their own.
        Individual personas can override this via their provider/model settings.

        Args:
            fallback: If True, will try all available LLM providers if primary fails

        Returns:
            LLMProvider instance
        """
        if self._provider is None:
            manager = self._get_llm_manager()
            self._provider = manager.get_provider(self._provider_name)

            # For LM Studio, try creating provider directly with configured base_url if manager didn't return one
            if self._provider is None and self._provider_name == "lmstudio":
                try:
                    from ..providers import get_provider

                    self._provider = get_provider(
                        "lmstudio",
                        api_key=self._api_key or "lm-studio",
                        model=self._model,
                        base_url=self._base_url,
                    )
                    if self._provider:
                        logger.debug(f"Created LM Studio provider with base_url: {self._base_url}")
                except Exception as e:
                    logger.debug(f"Failed to create LM Studio provider directly: {e}")

            # Don't fall back if LM Studio was explicitly configured (has custom base_url or provider is lmstudio)
            is_lmstudio_configured = self._provider_name == "lmstudio" and (
                self._base_url is not None or self._model is not None
            )

            if self._provider is None and fallback and not is_lmstudio_configured:
                # Try LLMManager's preferred provider first
                preferred_provider = manager.preferred_provider
                if preferred_provider != self._provider_name:
                    self._provider = manager.get_provider(preferred_provider)
                    if self._provider is not None:
                        logger.warning(
                            "Provider '%s' unavailable; falling back to '%s'.",
                            self._provider_name,
                            preferred_provider,
                        )
                        self._provider_name = preferred_provider

                # If still no provider, try all available providers in priority order
                if self._provider is None:
                    from .config import get_available_providers

                    available = get_available_providers()
                    # Priority order: anthropic > openai > gemini > vercel > generic
                    priority = ["anthropic", "openai", "gemini", "vercel", "generic"]

                    for preferred in priority:
                        for provider_name, api_key in available:
                            if (
                                provider_name == preferred
                                and api_key
                                and provider_name != self._provider_name
                            ):
                                try:
                                    from ..providers import get_provider

                                    test_provider = get_provider(
                                        provider_name,
                                        api_key=api_key,
                                        model=self._model,
                                        base_url=self._base_url,
                                    )
                                    if test_provider:
                                        self._provider = test_provider
                                        logger.warning(
                                            "Provider '%s' unavailable; falling back to '%s'.",
                                            self._provider_name,
                                            provider_name,
                                        )
                                        self._provider_name = provider_name
                                        self._api_key = api_key
                                        break
                                except Exception as e:
                                    logger.debug(
                                        f"Failed to initialize fallback provider {provider_name}: {e}"
                                    )
                                    continue
                        if self._provider is not None:
                            break

            if self._provider is None:
                from .config import get_available_providers

                available_names = [p for p, k in get_available_providers() if k]
                if available_names:
                    available_str = ", ".join(available_names)
                    raise ValueError(
                        f"Provider '{self._provider_name}' unavailable. "
                        f"Available providers: {available_str}. "
                        "Please check your API keys or run 'council providers --diagnose'."
                    )
                else:
                    raise ValueError(
                        f"Provider '{self._provider_name}' unavailable and no fallback providers found. "
                        "Please set at least one API key (ANTHROPIC_API_KEY, OPENAI_API_KEY, GEMINI_API_KEY, etc.) "
                        "or run 'council providers --diagnose' for help."
                    )
        return self._provider

    def _get_member_provider(self, member: Persona, default_provider: LLMProvider) -> LLMProvider:
        """
        Get or create an LLM provider for a specific member's model/provider override.

        Council AI supports personas using various LLM providers simultaneously.
        Each persona can have unique model/provider settings. If the persona's
        specified provider is unavailable, falls back to the default provider.

        This enables heterogeneous councils where different personas use different
        LLM providers (e.g., rams uses Claude, kahneman uses GPT-4) simultaneously.
        """
        provider_name = member.provider or self._provider_name
        model_name = member.model or self._model

        # When using LM Studio, force all personas to use the default provider/model
        # LM Studio only supports OpenAI-compatible models, so persona-specific providers/models won't work
        if self._provider_name == "lmstudio":
            if provider_name != "lmstudio" or model_name != self._model:
                logger.debug(
                    f"Persona '{member.id}' requested provider '{provider_name}' model '{model_name}' "
                    f"but using LM Studio; forcing default provider 'lmstudio' with model '{self._model}'"
                )
                return default_provider
            else:
                # Same provider and model, reuse default
                return default_provider

        # If persona uses same provider/model as default, reuse it
        if provider_name == self._provider_name and model_name == self._model:
            return default_provider

        cache_key = (provider_name, model_name, self._base_url)
        if cache_key not in self._provider_cache:
            api_key = (
                get_api_key(provider_name)
                if provider_name != self._provider_name
                else self._api_key
            )

            # Try to create provider for persona's specific model/provider
            try:
                self._provider_cache[cache_key] = get_provider(
                    provider_name,
                    api_key=api_key,
                    model=model_name,
                    base_url=self._base_url,
                )
            except ImportError:
                # If persona's provider requires missing module, fall back to default
                logger.warning(
                    f"Persona '{member.id}' requested provider '{provider_name}' unavailable (missing module); "
                    f"using default provider '{self._provider_name}' instead."
                )
                return default_provider
            except Exception:
                # If persona's provider is unavailable, fall back to default
                logger.warning(
                    f"Persona '{member.id}' requested provider '{provider_name}' unavailable; "
                    f"using default provider '{self._provider_name}' instead."
                )
                return default_provider

        return self._provider_cache[cache_key]

    def _get_synthesis_provider(self, default_provider: LLMProvider) -> LLMProvider:
        """Get or create a provider for synthesis-specific overrides."""
        if not self._has_synthesis_overrides():
            return default_provider

        provider_name = self.config.synthesis_provider or self._provider_name
        model_name = self.config.synthesis_model or self._model

        cache_key = (provider_name, model_name, self._base_url)
        if cache_key not in self._provider_cache:
            api_key = get_api_key(provider_name)
            if api_key is None and provider_name == self._provider_name:
                api_key = self._api_key
            try:
                self._provider_cache[cache_key] = get_provider(
                    provider_name,
                    api_key=api_key,
                    model=model_name,
                    base_url=self._base_url,
                )
            except Exception as e:
                logger.warning(
                    f"Synthesis provider '{provider_name}' unavailable; "
                    f"using default provider '{self._provider_name}' instead: {e}"
                )
                # Cache the fallback decision to avoid repeated failed instantiation attempts.
                self._provider_cache[cache_key] = default_provider
                return default_provider
        return self._provider_cache[cache_key]

    def _has_synthesis_overrides(self) -> bool:
        """Return True when synthesis-specific provider/model overrides are set."""
        return bool(self.config.synthesis_provider or self.config.synthesis_model)

    async def _warmup_providers(self) -> None:
        """Pre-initialize providers for all active members to reduce first-response latency."""
        try:
            provider = self._get_provider(fallback=False)
            if not provider:
                return

            # Warm up providers for all active members
            for member in self._members.values():
                if member.enabled:
                    try:
                        # This will initialize and cache the provider if needed
                        self._get_member_provider(member, provider)
                    except Exception as e:
                        logger.debug(f"Failed to warmup provider for {member.id}: {e}")
        except Exception as e:
            logger.debug(f"Provider warmup failed: {e}")

    def _resolve_member_generation_params(self, member: Persona) -> Dict[str, Any]:
        """Resolve per-member generation parameters."""
        overrides = normalize_model_params(member.model_params)
        params = {
            "temperature": overrides.get("temperature", self.config.temperature),
            "max_tokens": overrides.get("max_tokens", self.config.max_tokens_per_response),
        }
        # Add optional LM Studio/OpenAI-compatible parameters if present
        for key in [
            "top_p",
            "top_k",
            "repetition_penalty",
            "frequency_penalty",
            "presence_penalty",
        ]:
            if key in overrides:
                params[key] = overrides[key]
        validate_model_params(params)
        return params

    def _get_web_search_tool(self):
        """Get or create web search tool."""
        if self._web_search_tool is None and self.config.enable_web_search:
            try:
                from ..tools.web_search import WebSearchTool

                self._web_search_tool = WebSearchTool()
            except (ValueError, ImportError) as e:
                logger.warning(f"Web search not available: {e}")
                self._web_search_tool = None
        return self._web_search_tool

    async def _enhance_context_with_web_search(
        self, query: str, context: Optional[str], member: Persona
    ) -> Optional[str]:
        """Enhance context with web search if enabled (uses cache to avoid duplicate searches)."""
        # Check if web search is enabled (council-level or persona-level)
        if not self.config.enable_web_search and not member.enable_web_search:
            return None

        # Check cache first (same query = same search results)
        cache_key = query.lower().strip()
        if cache_key in self._web_search_cache:
            cached_result = self._web_search_cache[cache_key]
            if cached_result is not None:
                return f"{context or ''}\n\n{cached_result}".strip()
            return None

        web_search = self._get_web_search_tool()
        if not web_search:
            # Cache None to avoid repeated tool checks
            self._web_search_cache[cache_key] = None
            return None

        try:
            # Perform web search
            search_response = await web_search.search(query, max_results=3)
            search_context = web_search.format_search_results(search_response)
            # Cache the search context (without base context)
            self._web_search_cache[cache_key] = search_context
            return f"{context or ''}\n\n{search_context}".strip()
        except Exception as e:
            logger.warning(f"Web search failed: {e}")
            # Cache None to avoid retrying failed searches
            self._web_search_cache[cache_key] = None
            return None

    # ═══════════════════════════════════════════════════════════════════════════
    # Member Management
    # ═══════════════════════════════════════════════════════════════════════════

    def add_member(self, persona: Union[str, Persona], weight: Optional[float] = None) -> None:
        """
        Add a persona to the council.

        Args:
            persona: Persona instance or persona ID string
            weight: Override the persona's default weight
        """
        if isinstance(persona, str):
            persona = self._persona_manager.get_or_raise(persona)

        if weight is not None:
            persona = persona.clone(weight=weight)

        self._members[persona.id] = persona

    def _find_member_key(self, persona_id: str) -> Optional[str]:
        """Find the actual key for a persona ID (case-insensitive lookup)."""
        persona_id_lower = persona_id.lower()
        for key in self._members.keys():
            if key.lower() == persona_id_lower:
                return key
        return None

    def remove_member(self, persona_id: str) -> None:
        """Remove a member from the council (case-insensitive)."""
        key = self._find_member_key(persona_id)
        if key:
            del self._members[key]

    def get_member(self, persona_id: str) -> Optional[Persona]:
        """Get a council member by ID (case-insensitive)."""
        key = self._find_member_key(persona_id)
        return self._members.get(key) if key else None

    def list_members(self) -> List[Persona]:
        """List all council members."""
        return list(self._members.values())

    def clear_members(self) -> None:
        """Remove all members from the council."""
        self._members.clear()

    def set_member_weight(self, persona_id: str, weight: float) -> None:
        """Update a member's influence weight (case-insensitive)."""
        key = self._find_member_key(persona_id)
        if not key:
            raise ValueError(f"Member '{persona_id}' not in council")
        self._members[key].weight = weight

    def enable_member(self, persona_id: str) -> None:
        """Enable a member (case-insensitive)."""
        key = self._find_member_key(persona_id)
        if key:
            self._members[key].enabled = True

    def disable_member(self, persona_id: str) -> None:
        """Disable a member (they won't respond but stay in council) (case-insensitive)."""
        key = self._find_member_key(persona_id)
        if key:
            self._members[key].enabled = False

    def _get_active_members(self, member_ids: Optional[List[str]] = None) -> List[Persona]:
        """
        Get the list of active members to consult.

        Args:
            member_ids: Specific member IDs to consult (None = all enabled members)

        Returns:
            List of Persona objects that are enabled and should be consulted
        """
        if member_ids:
            # Return specific members if requested
            active = []
            for member_id in member_ids:
                if member_id in self._members:
                    member = self._members[member_id]
                    if member.enabled:
                        active.append(member)
                else:
                    raise ValueError(f"Member '{member_id}' not found in council")
            return active
        else:
            # Return all enabled members
            return [m for m in self._members.values() if m.enabled]

    def _start_session(
        self, query: str, context: Optional[str] = None, session_id: Optional[str] = None
    ) -> Session:
        """
        Start or resume a consultation session.

        Args:
            query: The consultation query
            context: Optional context
            session_id: Existing session ID to resume

        Returns:
            Session object
        """
        if session_id:
            if self._history:
                session = self._history.load_session(session_id)
                if session:
                    # Update members if council has loaded specific ones
                    if self._members:
                        session.members = list(self._members.keys())
                    self._current_session = session
                    return session

        member_ids = [m.id for m in self._members.values() if m.enabled]
        session = Session(
            council_name=self.config.name,
            members=member_ids,
            session_id=session_id or str(uuid4()),
        )
        self._sessions.append(session)
        self._current_session = session
        return session

    # ═══════════════════════════════════════════════════════════════════════════
    # Consultation
    # ═══════════════════════════════════════════════════════════════════════════

    def consult(
        self,
        query: str,
        context: Optional[str] = None,
        mode: Optional[ConsultationMode] = None,
        members: Optional[List[str]] = None,
        session_id: Optional[str] = None,
    ) -> ConsultationResult:
        """
        Consult the council on a query.

        Uses streaming internally for better perceived performance while maintaining
        backward compatibility by collecting streamed responses.

        Args:
            query: The question or topic to discuss
            context: Additional context for the consultation
            mode: Override the default consultation mode
            members: Specific member IDs to consult (None = all enabled)
            session_id: Optional session ID to resume or continue a session

        Returns:
            ConsultationResult with individual responses and synthesis
        """
        try:
            asyncio.get_running_loop()
            # If we're in an async context, we need to run in a thread
            with ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(
                    lambda: asyncio.run(
                        self.consult_async(query, context, mode, members, session_id)
                    )
                )
                return future.result()
        except RuntimeError:
            # No running event loop, we can create one
            return asyncio.run(self.consult_async(query, context, mode, members, session_id))

    async def consult_async(
        self,
        query: str,
        context: Optional[str] = None,
        mode: Optional[Union[ConsultationMode, str]] = None,
        members: Optional[List[str]] = None,
        session_id: Optional[str] = None,
        auto_recall: bool = True,
    ) -> ConsultationResult:
        """Async version of consult."""
        # Convert string mode to enum if needed
        if isinstance(mode, str):
            mode = ConsultationMode(mode)
        mode = mode or self.config.mode
        provider = self._get_provider(fallback=True)

        # Start/Resume session first to potentially get recall context
        session = self._start_session(query, context, session_id=session_id)

        # Auto-recall context from history and MemU if not explicitly provided
        if auto_recall and self._history and not context:
            context_parts = []

            # Get recent conversation context
            recent_context = self._history.get_recent_context(session.session_id)
            if recent_context:
                context_parts.append(f"PREVIOUS CONVERSATION CONTEXT:\n{recent_context}")

            # Get MemU memory context
            memu_context = self._history.get_memu_context(query, session.session_id)
            if memu_context:
                context_parts.append(f"MEMORY CONTEXT:\n{memu_context}")

            # Combine contexts if we have any
            if context_parts:
                context = "\n\n".join(context_parts)

        # Get active members
        active_members = self._get_active_members(members)
        if not active_members:
            raise ValueError("No active council members")

        # Run pre-consult hooks
        for hook in self._pre_consult_hooks:
            query, context = hook(query, context)

        # Get responses based on mode using Strategy pattern
        strategy = get_strategy(mode.value)
        strategy_result = None
        result_or_responses = await strategy.execute(
            council=self,
            query=query,
            context=context,
            members=members,
            session_id=session_id,
            auto_recall=auto_recall,
        )

        # Backwards-compatible handling: strategies may return either a
        # ConsultationResult (new behavior) or a List[MemberResponse] (legacy).

        if isinstance(result_or_responses, ConsultationResult):
            strategy_result = result_or_responses
            responses = strategy_result.responses
        elif isinstance(result_or_responses, list):
            # Runtime type validation instead of cast for type safety
            responses = result_or_responses
        else:
            # This should never happen if strategies follow the contract
            raise TypeError(
                f"Strategy returned unexpected type: {type(result_or_responses)}. "
                "Expected ConsultationResult or List[MemberResponse]."
            )

        # Generate synthesis if needed
        synthesis = None
        structured_synthesis = None

        # Check if strategy already provided synthesis to avoid redundant generation
        strategy_has_synthesis = strategy_result is not None and (
            strategy_result.synthesis is not None
            or strategy_result.structured_synthesis is not None
        )

        if (
            mode in (ConsultationMode.SYNTHESIS, ConsultationMode.DEBATE)
            and not strategy_has_synthesis
        ):
            synthesis_provider = self._get_synthesis_provider(provider)
            # Try structured synthesis if enabled in config
            if getattr(self.config, "use_structured_output", False):
                try:
                    structured_synthesis = await self._generate_structured_synthesis(
                        synthesis_provider, query, context, responses
                    )
                    if structured_synthesis is None:
                        synthesis = await self._generate_synthesis(
                            synthesis_provider, query, context, responses
                        )
                    else:
                        # Convert structured to text for backward compatibility
                        synthesis = self._format_structured_synthesis(structured_synthesis)
                except Exception as e:
                    # Fallback to free-form synthesis
                    logger.debug(f"Structured synthesis failed, falling back to free-form: {e}")
                    synthesis = await self._generate_synthesis(
                        synthesis_provider, query, context, responses
                    )
            else:
                synthesis = await self._generate_synthesis(
                    synthesis_provider, query, context, responses
                )

        # Run Analysis Phase (Phase 2 Enhancement) - start in parallel with synthesis if possible
        analysis_task = None
        if (
            self.config.enable_analysis
            and len(responses) > 1
            and mode
            in (ConsultationMode.SYNTHESIS, ConsultationMode.DEBATE, ConsultationMode.INDIVIDUAL)
        ):
            # Start analysis in parallel (don't wait for synthesis to complete)
            async def run_analysis():
                try:
                    from .analysis import AnalysisEngine

                    # Use synthesis provider (usually strongest model) for analysis
                    analysis_provider = self._get_synthesis_provider(provider)
                    engine = AnalysisEngine(analysis_provider)

                    # Convert MemberResponse objects to dicts for the engine
                    resp_dicts = [r.to_dict() for r in responses]
                    await engine.analyze(query, context, resp_dicts)
                    logger.debug("Consultation analysis matched.")
                except Exception as e:
                    logger.warning(f"Analysis phase failed: {e}")

            analysis_task = asyncio.create_task(run_analysis())

        # Wait for analysis to complete (if started)
        if analysis_task:
            try:
                await analysis_task
            except Exception as e:
                logger.debug(f"Analysis task error: {e}")

        # Create result. If the strategy returned a ConsultationResult, update it
        # with any synthesis/structured synthesis we computed; otherwise build a new one.
        if strategy_result is None:
            result = ConsultationResult(
                query=query,
                context=context,
                responses=responses,
                synthesis=synthesis,
                mode=mode.value,  # Convert enum to string
                timestamp=datetime.now(),
                structured_synthesis=structured_synthesis,
            )
        else:
            # Merge computed synthesis back into strategy-provided result when missing
            if strategy_result.synthesis is None and synthesis is not None:
                strategy_result.synthesis = synthesis
            if strategy_result.structured_synthesis is None and structured_synthesis is not None:
                strategy_result.structured_synthesis = structured_synthesis
            # Ensure context/mode/timestamp are set
            if strategy_result.context is None:
                strategy_result.context = context
            if strategy_result.mode is None:
                strategy_result.mode = mode.value  # Convert enum to string
            if strategy_result.timestamp is None:
                strategy_result.timestamp = datetime.now()

            result = strategy_result

        # Update session
        session.add_consultation(result)

        # Run post-consult hooks
        for post_hook in self._post_consult_hooks:
            result = post_hook(result)

        # Auto-save to history if enabled
        if self._history:
            history = self._history
            try:
                metadata = {"domain": self._domain_id} if self._domain_id else None
                consultation_id = history.save(result, metadata=metadata)
                history.save_session(session)

                # Save cost records
                if consultation_id:
                    from .cost_tracker import get_cost_tracker

                    cost_tracker = get_cost_tracker()
                    for cost_record in cost_tracker.get_records():
                        history.save_cost(
                            consultation_id=consultation_id,
                            provider=cost_record.provider,
                            model=cost_record.model,
                            input_tokens=cost_record.input_tokens,
                            output_tokens=cost_record.output_tokens,
                            cost_usd=cost_record.cost_usd,
                            session_id=session.session_id if session else None,
                        )
                    # Clear tracker for next consultation
                    cost_tracker.clear()
            except Exception as e:
                # Don't fail consultation if history save fails
                logger.warning(f"Failed to save consultation to history: {e}")

        # Record in user memory for personalization (optional, non-blocking)
        try:
            from .user_memory import get_user_memory

            user_memory = get_user_memory()
            user_memory.record_consultation(result)
            if result.session_id:
                user_memory.record_session(result.session_id, self._domain_id)
        except Exception as e:
            # User memory is optional - don't log as warning, just debug
            logger.debug(f"Failed to record in user memory: {e}")

        return result

    async def _save_history_async(self, result: ConsultationResult, session: Session) -> None:
        """Save consultation history asynchronously (non-blocking)."""
        if not self._history:
            return
        history = self._history
        try:
            metadata = {"domain": self._domain_id} if self._domain_id else None
            # Run blocking save in thread pool to avoid blocking event loop
            consultation_id = await asyncio.to_thread(history.save, result, metadata=metadata)
            await asyncio.to_thread(history.save_session, session)

            # Save cost records
            if consultation_id:
                from .cost_tracker import get_cost_tracker

                cost_tracker = get_cost_tracker()
                for cost_record in cost_tracker.get_records():
                    await asyncio.to_thread(
                        history.save_cost,
                        consultation_id=consultation_id,
                        provider=cost_record.provider,
                        model=cost_record.model,
                        input_tokens=cost_record.input_tokens,
                        output_tokens=cost_record.output_tokens,
                        cost_usd=cost_record.cost_usd,
                        session_id=session.session_id if session else None,
                    )
                # Clear tracker for next consultation
                cost_tracker.clear()
        except Exception as e:
            # Don't fail consultation if history save fails
            logger.warning(f"Failed to save consultation to history: {e}")

    async def consult_stream(
        self,
        query: str,
        context: Optional[str] = None,
        mode: Optional[ConsultationMode] = None,
        members: Optional[List[str]] = None,
        session_id: Optional[str] = None,
        auto_recall: bool = True,
    ) -> AsyncIterator[Dict[str, Any]]:
        """
        Stream consultation results as they're generated.
        ...
        """
        mode = mode or self.config.mode
        provider = self._get_provider(fallback=True)

        # Start/Resume session first
        session = self._start_session(query, context, session_id=session_id)

        # Auto-recall context from history and MemU if not explicitly provided
        if auto_recall and self._history and not context:
            context_parts = []

            # Get recent conversation context
            recent_context = self._history.get_recent_context(session.session_id)
            if recent_context:
                context_parts.append(f"PREVIOUS CONVERSATION CONTEXT:\n{recent_context}")

            # Get MemU memory context
            memu_context = self._history.get_memu_context(query, session.session_id)
            if memu_context:
                context_parts.append(f"MEMORY CONTEXT:\n{memu_context}")

            # Combine contexts if we have any
            if context_parts:
                context = "\n\n".join(context_parts)

        # Get active members
        active_members = self._get_active_members(members)
        if not active_members:
            raise ValueError("No active council members")

        # Run pre-consult hooks
        for hook in self._pre_consult_hooks:
            query, context = hook(query, context)

        # Clear web search cache for new consultation
        self._web_search_cache.clear()

        # Warm up providers on first consultation (non-blocking)
        if not self._providers_warmed:
            self._providers_warmed = True
            asyncio.create_task(self._warmup_providers())

        # Batch enhance contexts for all members needing web search (parallel)
        # This pre-populates the cache so individual member calls are instant
        await self._batch_enhance_contexts(query, context, active_members)

        # Get responses based on mode using Strategy pattern
        responses: List[MemberResponse] = []
        strategy = get_strategy(mode.value)

        # Progressive synthesis: start synthesis as responses arrive (if enabled)
        # Note: Full progressive synthesis requires complex coordination, so this is
        # a simplified version that starts synthesis after first response completes
        synthesis_started = False

        async for update in strategy.stream(
            council=self,
            query=query,
            context=context,
            members=members,
            session_id=session_id,
            auto_recall=auto_recall,
        ):
            yield update
            if update.get("type") == "response_complete":
                responses.append(update["response"])

                # Progressive synthesis: start synthesis early if enabled
                if (
                    mode in (ConsultationMode.SYNTHESIS, ConsultationMode.DEBATE)
                    and self.config.progressive_synthesis
                    and not synthesis_started
                    and len(responses) >= 1
                ):
                    # Start synthesis with partial responses (will complete after all responses)
                    synthesis_started = True
                    # Note: Full progressive synthesis would update as more responses arrive
                    # For now, we start early but wait for all responses for accuracy

        # Generate synthesis if needed (streaming)
        synthesis = None
        structured_synthesis = None
        if mode in (ConsultationMode.SYNTHESIS, ConsultationMode.DEBATE):
            # For streaming, use free-form synthesis (structured would require buffering)
            synthesis_provider = self._get_synthesis_provider(provider)
            yield {"type": "synthesis_start"}
            synthesis_parts: List[str] = []
            async for chunk in self._generate_synthesis_stream(
                synthesis_provider, query, context, responses
            ):
                yield {"type": "synthesis_chunk", "content": chunk}
                synthesis_parts.append(chunk)
            synthesis = "".join(synthesis_parts)
            yield {"type": "synthesis_complete", "synthesis": synthesis}

        # Run Analysis Phase (Phase 2 Enhancement) - Streaming
        analysis = None
        if (
            self.config.enable_analysis
            and len(responses) > 1
            and mode
            in (ConsultationMode.SYNTHESIS, ConsultationMode.DEBATE, ConsultationMode.INDIVIDUAL)
        ):
            try:
                from .analysis import AnalysisEngine

                # Use synthesis provider
                analysis_provider = self._get_synthesis_provider(provider)
                engine = AnalysisEngine(analysis_provider)

                # Convert MemberResponse objects to dicts
                resp_dicts = [r.to_dict() for r in responses]

                # Yield progress
                yield {"type": "progress", "message": "Analyzing consensus..."}

                # Run analysis
                analysis = await engine.analyze(query, context, resp_dicts)

                # Yield analysis result event for UI
                if analysis:
                    yield {"type": "analysis", "data": analysis.model_dump()}
                    logger.debug("Consultation analysis matched.")
            except Exception as e:
                logger.warning(f"Analysis phase failed: {e}")

        # Create result
        result = ConsultationResult(
            query=query,
            context=context,
            responses=responses,
            synthesis=synthesis,
            mode=mode.value,
            timestamp=datetime.now(),
            structured_synthesis=structured_synthesis,
        )

        # Update session
        session.add_consultation(result)

        # Attach session_id for persistence
        result.session_id = session.session_id

        # Run post-consult hooks
        for post_hook in self._post_consult_hooks:
            result = post_hook(result)

        # Auto-save to history if enabled (non-blocking for streaming)
        if self._history:
            # Save history in background to avoid blocking stream
            asyncio.create_task(self._save_history_async(result, session))

        # Clear web search cache after consultation
        self._web_search_cache.clear()

        # Record in user memory for personalization (optional, non-blocking)
        try:
            from .user_memory import get_user_memory

            user_memory = get_user_memory()
            user_memory.record_consultation(result)
            if result.session_id:
                user_memory.record_session(result.session_id, self._domain_id)
        except Exception as e:
            # User memory is optional - don't log as warning, just debug
            logger.debug(f"Failed to record in user memory: {e}")

        yield {"type": "complete", "result": result}

    async def _batch_enhance_contexts(
        self, query: str, base_context: Optional[str], members: List[Persona]
    ) -> Dict[str, Optional[str]]:
        """
        Batch enhance contexts for all members needing web search (performed in parallel).

        Returns a dict mapping member.id -> enhanced_context (or None if no enhancement needed).
        """
        # Identify members that need web search
        members_needing_search = [
            m
            for m in members
            if (self.config.enable_web_search or m.enable_web_search)
            and self._get_web_search_tool() is not None
        ]

        if not members_needing_search:
            return {}

        # Perform all web searches in parallel
        async def enhance_for_member(member: Persona) -> tuple[str, Optional[str]]:
            enhanced = await self._enhance_context_with_web_search(query, base_context, member)
            return (member.id, enhanced)

        # Run all web searches concurrently
        results: List[Union[tuple[str, Optional[str]], BaseException]] = await asyncio.gather(
            *[enhance_for_member(member) for member in members_needing_search],
            return_exceptions=True,
        )

        # Build result dict, handling any exceptions
        enhanced_contexts: Dict[str, Optional[str]] = {}
        for result in results:
            if isinstance(result, (asyncio.CancelledError, KeyboardInterrupt)):
                # Propagate cancellation/interruption so higher-level tasks can terminate correctly
                raise result
            if isinstance(result, Exception):
                logger.warning(f"Web search enhancement failed: {result}")
                continue
            # Type guard: at this point, result must be a tuple
            if isinstance(result, tuple):
                member_id, enhanced = result
                enhanced_contexts[member_id] = enhanced

        return enhanced_contexts

    async def _get_member_response(
        self,
        provider: LLMProvider,
        member: Persona,
        query: str,
        context: Optional[str],
    ) -> MemberResponse:
        """
        Get a single member's response using their preferred LLM provider.

        Each persona can use a different LLM provider if configured.
        This enables heterogeneous councils with personas using various providers.
        """
        # Enhance context with web search if enabled (uses cache if available)
        enhanced_context = await self._enhance_context_with_web_search(query, context, member)
        if enhanced_context:
            context = enhanced_context

        # Apply reasoning mode
        reasoning_mode_str = member.reasoning_mode or self.config.reasoning_mode
        reasoning_mode = None
        if reasoning_mode_str:
            try:
                # Normalize to lowercase with underscores to match enum values
                normalized = str(reasoning_mode_str).lower().replace("-", "_")
                reasoning_mode = ReasoningMode(normalized)
            except ValueError:
                logger.warning(
                    f"Invalid reasoning mode: {reasoning_mode_str}. "
                    f"Valid modes: {[m.value for m in ReasoningMode]}"
                )

        system_prompt = member.get_system_prompt()
        if reasoning_mode:
            system_prompt = get_reasoning_prompt(reasoning_mode, system_prompt)

        user_prompt = member.format_response_prompt(query, context)
        if reasoning_mode:
            suffix = get_reasoning_suffix(reasoning_mode)
            if suffix:
                user_prompt = f"{user_prompt}{suffix}"

        try:
            member_provider = self._get_member_provider(member, provider)
            params = self._resolve_member_generation_params(member)
            # Special handling for LM Studio: bypass LLMManager to avoid strict API key validation.
            # LLMManager.generate() enforces API key checks that fail for local providers,
            # whereas using the provider instance directly (fallback path) works because
            # we've already injected a dummy key in _get_provider().
            use_manager = member_provider is provider and self._provider_name != "lmstudio"

            if use_manager:
                manager = self._get_llm_manager()
                # Use configurable timeout (default 120s, lower for local providers)
                timeout = self.config.member_timeout
                if self._provider_name == "lmstudio":
                    # LM Studio is local, faster response expected
                    timeout = min(timeout, 60.0)

                response = await asyncio.wait_for(
                    manager.generate(
                        system_prompt=system_prompt,
                        user_prompt=user_prompt,
                        provider=self._provider_name,
                        fallback=True,
                        max_tokens=params["max_tokens"],
                        temperature=params["temperature"],
                    ),
                    timeout=timeout,
                )
            else:
                # Extract optional parameters for complete() call
                complete_kwargs = {
                    "system_prompt": system_prompt,
                    "user_prompt": user_prompt,
                    "max_tokens": params["max_tokens"],
                    "temperature": params["temperature"],
                }
                # Add optional parameters if present (for OpenAIProvider/LM Studio)
                for key in [
                    "top_p",
                    "top_k",
                    "repetition_penalty",
                    "frequency_penalty",
                    "presence_penalty",
                ]:
                    if key in params:
                        complete_kwargs[key] = params[key]

                # Use configurable timeout (default 120s, lower for local providers)
                timeout = self.config.member_timeout
                if self._provider_name == "lmstudio" or (
                    hasattr(member_provider, "base_url")
                    and member_provider.base_url
                    and "localhost" in str(member_provider.base_url)
                ):
                    # LM Studio or local providers, faster response expected
                    timeout = min(timeout, 60.0)

                response = await asyncio.wait_for(
                    member_provider.complete(**complete_kwargs),
                    timeout=timeout,
                )
            content = response.text

            # Track cost if history is available
            if (
                self._history
                and hasattr(response, "input_tokens")
                and hasattr(response, "output_tokens")
            ):
                try:
                    from .cost_tracker import get_cost_tracker

                    cost_tracker = get_cost_tracker()

                    # Get provider and model info
                    provider_name = self._provider_name
                    model_name = member.model or self._model or "unknown"

                    # Calculate and record cost
                    cost_tracker.record_cost(
                        provider=provider_name,
                        model=model_name,
                        input_tokens=getattr(response, "input_tokens", 0),
                        output_tokens=getattr(response, "output_tokens", 0),
                    )

                    # Store cost in history if we have a consultation ID
                    # (We'll need to pass this through or store it temporarily)
                    # For now, we'll store it when the consultation is saved
                except Exception as e:
                    logger.warning(f"Failed to track cost: {e}")

            # Run response hooks
            for hook in self._response_hooks:
                content = hook(member, content)

            return MemberResponse(
                persona=member,
                content=content,
                timestamp=datetime.now(),
            )
        except ImportError as e:
            # Extract module name from error message (e.g., "No module named 'openai'")
            module_name = str(e).replace("No module named ", "").strip("'\"")
            error_msg = (
                f"Missing required package '{module_name}'. "
                f"Install with: pip install {module_name} or pip install -e '.[{self._provider_name}]'"
            )
            return MemberResponse(
                persona=member,
                content=f"[Error getting response: {error_msg}]",
                timestamp=datetime.now(),
                error=error_msg,
            )
        except Exception as e:
            error_msg = str(e)
            # Provide more helpful error messages
            if "API key" in error_msg or "authentication" in error_msg.lower():
                error_msg = (
                    f"API authentication failed: {error_msg}. "
                    f"Please check your API key for provider '{self._provider_name}'. "
                    f"Council AI will try fallback providers if available."
                )
            elif "rate limit" in error_msg.lower():
                error_msg = f"Rate limit exceeded: {error_msg}. Please try again later."

            return MemberResponse(
                persona=member,
                content=f"[Error getting response: {error_msg}]",
                timestamp=datetime.now(),
                error=error_msg,
            )

    def _parse_thinking_chunk(
        self, text: str, accumulated: str
    ) -> tuple[Optional[str], Optional[str]]:
        """
        Parse text to detect thinking/reasoning sections vs final answer.

        This helps display the thought process in real-time, making the wait
        feel shorter and more engaging by showing how personas are reasoning.

        Strategy: Show everything as thinking initially, then switch to response
        when we detect clear conclusion markers or the response is getting long.

        Returns:
            (thinking_chunk, response_chunk) - one may be None, or both if ambiguous
        """
        if not text.strip():
            return (None, None)

        text_lower = text.lower()
        accumulated_lower = accumulated.lower()

        # Clear conclusion/final answer markers - switch to response mode
        conclusion_markers = [
            "in conclusion",
            "to summarize",
            "therefore",
            "thus",
            "final answer:",
            "final recommendation:",
            "my recommendation is",
            "my advice is",
            "i recommend",
            "i suggest",
            "summary:",
            "answer:",
            "recommendation:",
        ]

        # Check if we've hit a conclusion marker
        has_conclusion = any(marker in text_lower for marker in conclusion_markers)
        accumulated_has_conclusion = any(
            marker in accumulated_lower[-300:] for marker in conclusion_markers
        )

        # If we see conclusion markers, everything after is response
        if has_conclusion or accumulated_has_conclusion:
            return (None, text)

        # If accumulated text is very long (>2000 chars) and no conclusion yet,
        # assume we're past thinking and into response
        if len(accumulated) > 2000 and not accumulated_has_conclusion:
            return (None, text)

        # Default strategy: Show first ~1500 chars as thinking, then switch to response
        # This ensures users see the reasoning process even if models don't use markers
        if len(accumulated) <= 1500:
            return (text, None)

        # After 1500 chars, show as response unless we see explicit thinking markers
        thinking_markers = [
            "step",
            "thinking:",
            "reasoning:",
            "analysis:",
            "considering:",
            "let me think",
            "i need to",
            "to analyze",
            "examining",
            "evaluating",
        ]
        has_thinking_marker = any(marker in text_lower for marker in thinking_markers)
        if has_thinking_marker:
            return (text, None)

        # Default: show as response after initial thinking period
        return (None, text)

    async def _get_member_response_stream(
        self,
        provider: LLMProvider,
        member: Persona,
        query: str,
        context: Optional[str],
    ) -> AsyncIterator[Dict[str, Any]]:
        """Stream a single member's response with thinking process display."""
        yield {
            "type": "response_start",
            "persona_id": member.id,
            "persona_name": member.name,
            "persona_emoji": member.emoji,
        }

        # Enhance context with web search if enabled (uses cache if available)
        enhanced_context = await self._enhance_context_with_web_search(query, context, member)
        if enhanced_context:
            context = enhanced_context

        # Apply reasoning mode to enable thinking display
        reasoning_mode_str = member.reasoning_mode or self.config.reasoning_mode
        reasoning_mode = None
        if reasoning_mode_str:
            try:
                normalized = str(reasoning_mode_str).lower().replace("-", "_")
                reasoning_mode = ReasoningMode(normalized)
            except ValueError:
                logger.debug(f"Invalid reasoning mode: {reasoning_mode_str}")

        system_prompt = member.get_system_prompt()
        if reasoning_mode:
            system_prompt = get_reasoning_prompt(reasoning_mode, system_prompt)

        user_prompt = member.format_response_prompt(query, context)
        if reasoning_mode:
            suffix = get_reasoning_suffix(reasoning_mode)
            if suffix:
                user_prompt = f"{user_prompt}{suffix}"

        try:
            member_provider = self._get_member_provider(member, provider)
            params = self._resolve_member_generation_params(member)
            content_parts: List[str] = []
            stream_kwargs = {
                "system_prompt": system_prompt,
                "user_prompt": user_prompt,
                "max_tokens": params["max_tokens"],
                "temperature": params["temperature"],
            }
            # Add optional parameters if present
            for key in [
                "top_p",
                "top_k",
                "repetition_penalty",
                "frequency_penalty",
                "presence_penalty",
            ]:
                if key in params:
                    stream_kwargs[key] = params[key]
            # Accumulate content for thinking detection
            accumulated_content = ""
            thinking_parts: List[str] = []
            response_parts: List[str] = []

            async for chunk in member_provider.stream_complete(**stream_kwargs):
                content_parts.append(chunk)
                accumulated_content += chunk

                # Parse chunk to detect thinking vs response
                thinking_chunk, response_chunk = self._parse_thinking_chunk(
                    chunk, accumulated_content
                )

                if thinking_chunk:
                    thinking_parts.append(thinking_chunk)
                    yield {
                        "type": "thinking_chunk",
                        "persona_id": member.id,
                        "content": thinking_chunk,
                        "accumulated_thinking": "".join(thinking_parts),
                    }

                if response_chunk:
                    response_parts.append(response_chunk)
                    yield {
                        "type": "response_chunk",
                        "persona_id": member.id,
                        "content": response_chunk,
                        "accumulated_response": "".join(response_parts),
                    }

                # If we can't determine, show as response (default)
                if not thinking_chunk and not response_chunk:
                    response_parts.append(chunk)
                    yield {
                        "type": "response_chunk",
                        "persona_id": member.id,
                        "content": chunk,
                        "accumulated_response": "".join(response_parts),
                    }

            content = "".join(content_parts)

            # Run response hooks
            for hook in self._response_hooks:
                content = hook(member, content)

            response = MemberResponse(
                persona=member,
                content=content,
                timestamp=datetime.now(),
            )

            yield {
                "type": "response_complete",
                "persona_id": member.id,
                "response": response,
            }
        except ImportError as e:
            # Extract module name from error message (e.g., "No module named 'openai'")
            module_name = str(e).replace("No module named ", "").strip("'\"")
            error_msg = (
                f"Missing required package '{module_name}'. "
                f"Install with: pip install {module_name} or pip install -e '.[{self._provider_name}]'"
            )
            response = MemberResponse(
                persona=member,
                content=f"[Error getting response: {error_msg}]",
                timestamp=datetime.now(),
                error=error_msg,
            )
            yield {
                "type": "response_complete",
                "persona_id": member.id,
                "response": response,
            }
            return
        except Exception as e:
            # Get detailed error information
            error_type = type(e).__name__
            error_msg = str(e) if str(e) else repr(e)

            # Log the full exception for debugging
            logger.error(
                f"Error in stream for {member.name} ({member.id}): {error_type}: {error_msg}",
                exc_info=True,
            )

            # Provide helpful error messages
            if not error_msg or error_msg == "":
                error_msg = f"{error_type}: An unexpected error occurred"

            if "API key" in error_msg or "authentication" in error_msg.lower():
                error_msg = (
                    f"API authentication failed: {error_msg}. "
                    f"Please check your API key for provider '{self._provider_name}'. "
                    f"Council AI will try fallback providers if available."
                )
            elif "rate limit" in error_msg.lower():
                error_msg = f"Rate limit exceeded: {error_msg}. Please try again later."
            elif "timeout" in error_msg.lower():
                error_msg = f"Request timeout: {error_msg}. The model may be slow or unavailable."
            elif "connection" in error_msg.lower() or "network" in error_msg.lower():
                error_msg = f"Connection error: {error_msg}. Check your network connection and LM Studio server."

            response = MemberResponse(
                persona=member,
                content=f"[Error getting response: {error_msg}]",
                timestamp=datetime.now(),
                error=error_msg,
            )

            yield {
                "type": "response_complete",
                "persona_id": member.id,
                "response": response,
            }

    # ═══════════════════════════════════════════════════════════════════════════
    # Synthesis Generation
    # ═══════════════════════════════════════════════════════════════════════════

    async def _generate_synthesis(
        self,
        provider: LLMProvider,
        query: str,
        context: Optional[str],
        responses: List[MemberResponse],
    ) -> str:
        """Generate a text synthesis from member responses."""
        if not responses:
            return "No responses to synthesize."

        # Build synthesis prompt
        responses_text = "\n\n".join(
            f"{r.persona.emoji} **{r.persona.name}** ({r.persona.title}):\n{r.content}"
            for r in responses
        )

        synthesis_prompt = self.config.synthesis_prompt or (
            "You are synthesizing perspectives from an advisory council. "
            "Review the following responses and provide a balanced, comprehensive synthesis "
            "that highlights key points of agreement, important differences, "
            "and actionable insights."
        )

        system_prompt = (
            f"{synthesis_prompt}\n\nYour synthesis should be clear, balanced, and actionable."
        )

        context_line = f"Context: {context}\n" if context else ""
        user_prompt = f"""Original Query: {query}
{context_line}

Council Responses:
{responses_text}

Please provide a comprehensive synthesis that:
1. Summarizes the key perspectives
2. Highlights areas of agreement and disagreement
3. Provides actionable insights or recommendations
4. Is concise but comprehensive (2-4 paragraphs)"""

        try:
            max_tokens = (
                self.config.synthesis_max_tokens
                if self.config.synthesis_max_tokens is not None
                else self.config.max_tokens_per_response * 2
            )
            if provider is self._provider and not self._has_synthesis_overrides():
                manager = self._get_llm_manager()
                response = await manager.generate(
                    system_prompt=system_prompt,
                    user_prompt=user_prompt,
                    provider=self._provider_name,
                    fallback=True,
                    max_tokens=max_tokens,
                    temperature=self.config.temperature,
                )
            else:
                response = await provider.complete(
                    system_prompt=system_prompt,
                    user_prompt=user_prompt,
                    max_tokens=max_tokens,  # Synthesis can be longer
                    temperature=self.config.temperature,
                )
            synthesis_text = response.text

            # Track synthesis cost
            if (
                self._history
                and hasattr(response, "input_tokens")
                and hasattr(response, "output_tokens")
            ):
                try:
                    from .cost_tracker import get_cost_tracker

                    cost_tracker = get_cost_tracker()

                    # Get synthesis provider name
                    if hasattr(provider, "__class__"):
                        # Try to get provider name from class
                        provider_class_name = provider.__class__.__name__.lower()
                        if "anthropic" in provider_class_name:
                            synthesis_provider_name = "anthropic"
                        elif "openai" in provider_class_name:
                            synthesis_provider_name = "openai"
                        elif "gemini" in provider_class_name:
                            synthesis_provider_name = "gemini"
                        else:
                            synthesis_provider_name = self._provider_name
                    else:
                        synthesis_provider_name = self._provider_name

                    synthesis_model = self.config.synthesis_model or self._model or "unknown"

                    cost_tracker.record_cost(
                        provider=synthesis_provider_name,
                        model=synthesis_model,
                        input_tokens=getattr(response, "input_tokens", 0),
                        output_tokens=getattr(response, "output_tokens", 0),
                    )
                except Exception as e:
                    logger.warning(f"Failed to track synthesis cost: {e}")

            return synthesis_text
        except Exception as e:
            logger.error(f"Failed to generate synthesis: {e}")
            # Fallback: simple concatenation
            return "\n\n".join(
                (
                    f"**{r.persona.name}**: {r.content[:200]}..."
                    if len(r.content) > 200
                    else f"**{r.persona.name}**: {r.content}"
                )
                for r in responses
            )

    async def _generate_structured_synthesis(
        self,
        provider: LLMProvider,
        query: str,
        context: Optional[str],
        responses: List[MemberResponse],
    ) -> Optional[SynthesisSchema]:
        """Generate structured synthesis using JSON schema."""
        if not responses:
            return None

        try:
            responses_text = "\n\n".join(
                f"{r.persona.emoji} **{r.persona.name}** ({r.persona.title}):\n{r.content}"
                for r in responses
            )

            system_prompt = (
                "You are synthesizing perspectives from an advisory council. "
                "Provide a structured analysis in JSON format."
            )

            context_line = f"Context: {context}\n" if context else ""
            user_prompt = f"""Original Query: {query}
{context_line}

Council Responses:
{responses_text}

Analyze these responses and provide a structured synthesis in JSON format \
matching the SynthesisSchema."""

            # Try to get structured output from provider
            max_tokens = (
                self.config.synthesis_max_tokens
                if self.config.synthesis_max_tokens is not None
                else self.config.max_tokens_per_response * 3
            )
            schema = SynthesisSchema.model_json_schema()
            data = await provider.complete_structured(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                json_schema=schema,
                max_tokens=max_tokens,
                temperature=self.config.temperature,
            )
            return SynthesisSchema(**data)
        except Exception as e:
            logger.error(f"Failed to generate structured synthesis: {e}")
            return None

    def _format_structured_synthesis(self, structured: SynthesisSchema) -> str:
        """Convert structured synthesis to readable text."""
        parts = []

        if structured.key_points_of_agreement:
            parts.append("**Key Points of Agreement:**")
            for point in structured.key_points_of_agreement:
                parts.append(f"• {point}")

        if structured.key_points_of_tension:
            parts.append("\n**Key Points of Tension:**")
            for point in structured.key_points_of_tension:
                parts.append(f"• {point}")

        if structured.synthesized_recommendation:
            parts.append(
                f"\n**Synthesized Recommendation:**\n{structured.synthesized_recommendation}"
            )

        if structured.action_items:
            parts.append("\n**Action Items:**")
            for item in structured.action_items:
                parts.append(f"• {item.description} (Priority: {item.priority})")

        if structured.recommendations:
            parts.append("\n**Recommendations:**")
            for rec in structured.recommendations:
                parts.append(f"• **{rec.title}**: {rec.description} (Confidence: {rec.confidence})")

        if structured.pros_cons:
            parts.append("\n**Pros and Cons:**")
            if structured.pros_cons.pros:
                parts.append("**Pros:**")
                for pro in structured.pros_cons.pros:
                    parts.append(f"• {pro}")
            if structured.pros_cons.cons:
                parts.append("**Cons:**")
                for con in structured.pros_cons.cons:
                    parts.append(f"• {con}")
            parts.append(f"\n**Net Assessment:** {structured.pros_cons.net_assessment}")

        return "\n".join(parts)

    async def _generate_synthesis_stream(
        self,
        provider: LLMProvider,
        query: str,
        context: Optional[str],
        responses: List[MemberResponse],
    ) -> AsyncIterator[str]:
        """Stream synthesis generation."""
        if not responses:
            yield "No responses to synthesize."
            return

        responses_text = "\n\n".join(
            f"{r.persona.emoji} **{r.persona.name}** ({r.persona.title}):\n{r.content}"
            for r in responses
        )

        synthesis_prompt = self.config.synthesis_prompt or (
            "You are synthesizing perspectives from an advisory council. "
            "Review the following responses and provide a balanced, comprehensive synthesis."
        )

        system_prompt = (
            f"{synthesis_prompt}\n\nYour synthesis should be clear, balanced, and actionable."
        )

        context_line = f"Context: {context}\n" if context else ""
        user_prompt = f"""Original Query: {query}
{context_line}

Council Responses:
{responses_text}

Please provide a comprehensive synthesis."""

        try:
            max_tokens = (
                self.config.synthesis_max_tokens
                if self.config.synthesis_max_tokens is not None
                else self.config.max_tokens_per_response * 2
            )
            stream_kwargs = {
                "system_prompt": system_prompt,
                "user_prompt": user_prompt,
                "max_tokens": max_tokens,
                "temperature": self.config.temperature,
            }
            async for chunk in provider.stream_complete(**stream_kwargs):
                yield chunk
        except Exception as e:
            logger.error(f"Failed to stream synthesis: {e}")
            # Fallback
            yield f"Error generating synthesis: {str(e)}"
