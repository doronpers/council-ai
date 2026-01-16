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
from .schemas import SynthesisSchema
from .session import ConsultationResult, MemberResponse, Session

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


class Council:
    """
    An advisory council composed of multiple AI personas.

    The Council orchestrates conversations with multiple personas,
    synthesizes their perspectives, and provides comprehensive advice.

    Example:
        council = Council(api_key="your-key", provider="anthropic")
        council.add_member("rams")
        council.add_member("grove")

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
            api_key: API key for the LLM provider (or set via environment)
            provider: LLM provider name ("anthropic", "openai", etc.)
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

        # Callbacks for extensibility
        # Pre-consult hooks receive (query, context) and must return (query, context)
        self._pre_consult_hooks: List[
            Callable[[str, Optional[str]], Tuple[str, Optional[str]]]
        ] = []
        # Post-consult hooks receive and return ConsultationResult
        self._post_consult_hooks: List[Callable[[ConsultationResult], ConsultationResult]] = []
        # Response hooks process each member's raw content string
        self._response_hooks: List[Callable[[Persona, str], str]] = []

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
        Get or create the LLM provider.

        Args:
            fallback: If True, will try fallback providers if primary fails

        Returns:
            LLMProvider instance
        """
        if self._provider is None:
            manager = self._get_llm_manager()
            self._provider = manager.get_provider(self._provider_name)

            if self._provider is None and fallback:
                preferred_provider = manager.preferred_provider
                self._provider = manager.get_provider(preferred_provider)
                if self._provider is not None and preferred_provider != self._provider_name:
                    logger.warning(
                        "Provider '%s' unavailable; falling back to '%s'.",
                        self._provider_name,
                        preferred_provider,
                    )
                    self._provider_name = preferred_provider

            if self._provider is None:
                raise ValueError(
                    f"Provider '{self._provider_name}' unavailable. "
                    "Please check your API keys or run 'council providers --diagnose'."
                )
        return self._provider

    def _get_member_provider(self, member: Persona, default_provider: LLMProvider) -> LLMProvider:
        """Get or create a provider for a specific member's model/provider override."""
        provider_name = member.provider or self._provider_name
        model_name = member.model or self._model

        if provider_name == self._provider_name and model_name == self._model:
            return default_provider

        cache_key = (provider_name, model_name, self._base_url)
        if cache_key not in self._provider_cache:
            api_key = (
                get_api_key(provider_name)
                if provider_name != self._provider_name
                else self._api_key
            )
            self._provider_cache[cache_key] = get_provider(
                provider_name,
                api_key=api_key,
                model=model_name,
                base_url=self._base_url,
            )
        return self._provider_cache[cache_key]

    def _get_synthesis_provider(self, default_provider: LLMProvider) -> LLMProvider:
        """Get or create a provider for synthesis-specific overrides."""
        provider_name = self.config.synthesis_provider or self._provider_name
        model_name = self.config.synthesis_model or self._model

        if (
            provider_name == self._provider_name
            and model_name == self._model
            and not self.config.synthesis_provider
            and not self.config.synthesis_model
        ):
            return default_provider

        cache_key = (provider_name, model_name, self._base_url)
        if cache_key not in self._provider_cache:
            api_key = get_api_key(provider_name)
            if api_key is None and provider_name == self._provider_name:
                api_key = self._api_key
            self._provider_cache[cache_key] = get_provider(
                provider_name,
                api_key=api_key,
                model=model_name,
                base_url=self._base_url,
            )
        return self._provider_cache[cache_key]

    def _resolve_member_generation_params(self, member: Persona) -> Dict[str, Any]:
        """Resolve per-member generation parameters."""
        overrides = normalize_model_params(member.model_params)
        params = {
            "temperature": overrides.get("temperature", self.config.temperature),
            "max_tokens": overrides.get("max_tokens", self.config.max_tokens_per_response),
        }
        validate_model_params(params)
        return params

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

    def remove_member(self, persona_id: str) -> None:
        """Remove a member from the council."""
        if persona_id in self._members:
            del self._members[persona_id]

    def get_member(self, persona_id: str) -> Optional[Persona]:
        """Get a council member by ID."""
        return self._members.get(persona_id)

    def list_members(self) -> List[Persona]:
        """List all council members."""
        return list(self._members.values())

    def clear_members(self) -> None:
        """Remove all members from the council."""
        self._members.clear()

    def set_member_weight(self, persona_id: str, weight: float) -> None:
        """Update a member's influence weight."""
        if persona_id not in self._members:
            raise ValueError(f"Member '{persona_id}' not in council")
        self._members[persona_id].weight = weight

    def enable_member(self, persona_id: str) -> None:
        """Enable a member."""
        if persona_id in self._members:
            self._members[persona_id].enabled = True

    def disable_member(self, persona_id: str) -> None:
        """Disable a member (they won't respond but stay in council)."""
        if persona_id in self._members:
            self._members[persona_id].enabled = False

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
    ) -> ConsultationResult:
        """
        Consult the council on a query.

        Args:
            query: The question or topic to discuss
            context: Additional context for the consultation
            mode: Override the default consultation mode
            members: Specific member IDs to consult (None = all enabled)

        Returns:
            ConsultationResult with individual responses and synthesis
        """
        try:
            asyncio.get_running_loop()
            # If we're in an async context, we need to run in a thread
            with ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(
                    lambda: asyncio.run(self.consult_async(query, context, mode, members))
                )
                return future.result()
        except RuntimeError:
            # No running event loop, we can create one
            return asyncio.run(self.consult_async(query, context, mode, members))

    async def consult_async(
        self,
        query: str,
        context: Optional[str] = None,
        mode: Optional[ConsultationMode] = None,
        members: Optional[List[str]] = None,
        session_id: Optional[str] = None,
        auto_recall: bool = True,
    ) -> ConsultationResult:
        """Async version of consult."""
        mode = mode or self.config.mode
        provider = self._get_provider(fallback=True)

        # Start/Resume session first to potentially get recall context
        session = self._start_session(query, context, session_id=session_id)

        # Auto-recall context from history if not explicitly provided
        if auto_recall and self._history and not context:
            recall_context = self._history.get_recent_context(session.session_id)
            if recall_context:
                context = f"PREVIOUS CONVERSATION CONTEXT:\n{recall_context}"

        # Get active members
        active_members = self._get_active_members(members)
        if not active_members:
            raise ValueError("No active council members")

        # Run pre-consult hooks
        for hook in self._pre_consult_hooks:
            query, context = hook(query, context)

        # Get responses based on mode
        if mode == ConsultationMode.INDIVIDUAL:
            responses = await self._consult_individual(provider, active_members, query, context)
        elif mode == ConsultationMode.SEQUENTIAL:
            responses = await self._consult_sequential(provider, active_members, query, context)
        elif mode == ConsultationMode.SYNTHESIS:
            responses = await self._consult_individual(provider, active_members, query, context)
        elif mode == ConsultationMode.DEBATE:
            responses = await self._consult_debate(provider, active_members, query, context)
        elif mode == ConsultationMode.VOTE:
            responses = await self._consult_vote(provider, active_members, query, context)
        else:
            responses = await self._consult_individual(provider, active_members, query, context)

        # Generate synthesis if needed
        synthesis = None
        structured_synthesis = None
        if mode in (ConsultationMode.SYNTHESIS, ConsultationMode.DEBATE):
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

        # Run Analysis Phase (Phase 2 Enhancement)
        if (
            self.config.enable_analysis
            and len(responses) > 1
            and mode
            in (ConsultationMode.SYNTHESIS, ConsultationMode.DEBATE, ConsultationMode.INDIVIDUAL)
        ):
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

        # Create result
        result = ConsultationResult(
            query=query,
            context=context,
            responses=responses,
            synthesis=synthesis,
            mode=mode,
            timestamp=datetime.now(),
            structured_synthesis=structured_synthesis,
        )

        # Update session
        session.add_consultation(result)

        # Run post-consult hooks
        for hook in self._post_consult_hooks:
            result = hook(result)

        # Auto-save to history if enabled
        if self._history:
            try:
                self._history.save(result)
                self._history.save_session(session)
            except Exception as e:
                # Don't fail consultation if history save fails
                logger.warning(f"Failed to save consultation to history: {e}")

        return result

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

        # Auto-recall context
        if auto_recall and self._history and not context:
            recall_context = self._history.get_recent_context(session.session_id)
            if recall_context:
                context = f"PREVIOUS CONVERSATION CONTEXT:\n{recall_context}"

        # Get active members
        active_members = self._get_active_members(members)
        if not active_members:
            raise ValueError("No active council members")

        # Run pre-consult hooks
        for hook in self._pre_consult_hooks:
            query, context = hook(query, context)

        # Get responses based on mode (streaming)
        responses: List[MemberResponse] = []
        if mode == ConsultationMode.INDIVIDUAL:
            async for update in self._consult_individual_stream(
                provider, active_members, query, context
            ):
                yield update
                if update.get("type") == "response_complete":
                    responses.append(update["response"])
        elif mode == ConsultationMode.SEQUENTIAL:
            async for update in self._consult_sequential_stream(
                provider, active_members, query, context
            ):
                yield update
                if update.get("type") == "response_complete":
                    responses.append(update["response"])
        elif mode == ConsultationMode.SYNTHESIS:
            async for update in self._consult_individual_stream(
                provider, active_members, query, context
            ):
                yield update
                if update.get("type") == "response_complete":
                    responses.append(update["response"])
        elif mode == ConsultationMode.DEBATE:
            async for update in self._consult_debate_stream(
                provider, active_members, query, context
            ):
                yield update
                if update.get("type") == "response_complete":
                    responses.append(update["response"])
        elif mode == ConsultationMode.VOTE:
            async for update in self._consult_vote_stream(provider, active_members, query, context):
                yield update
                if update.get("type") == "response_complete":
                    responses.append(update["response"])
        else:
            async for update in self._consult_individual_stream(
                provider, active_members, query, context
            ):
                yield update
                if update.get("type") == "response_complete":
                    responses.append(update["response"])

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
            mode=mode,
            timestamp=datetime.now(),
            structured_synthesis=structured_synthesis,
        )

        # Update session
        session.add_consultation(result)

        # Attach session_id for persistence
        result.session_id = session.session_id

        # Run post-consult hooks
        for hook in self._post_consult_hooks:
            result = hook(result)

        # Auto-save to history if enabled
        if self._history:
            try:
                self._history.save(result)
                self._history.save_session(session)
            except Exception as e:
                # Don't fail consultation if history save fails
                logger.warning(f"Failed to save consultation to history: {e}")

        yield {"type": "complete", "result": result}

    async def _consult_individual(
        self,
        provider: LLMProvider,
        members: List[Persona],
        query: str,
        context: Optional[str],
    ) -> List[MemberResponse]:
        """Get individual responses from all members in parallel."""
        tasks = [self._get_member_response(provider, member, query, context) for member in members]
        return await asyncio.gather(*tasks)

    async def _consult_sequential(
        self,
        provider: LLMProvider,
        members: List[Persona],
        query: str,
        context: Optional[str],
    ) -> List[MemberResponse]:
        """Get responses sequentially, each seeing previous responses."""
        responses: List[MemberResponse] = []
        accumulated_context = context or ""

        for member in members:
            response = await self._get_member_response(provider, member, query, accumulated_context)
            responses.append(response)

            # Add this response to context for next member
            accumulated_context += f"\n\n{member.emoji} {member.name} said:\n{response.content}"

        return responses

    async def _consult_debate(
        self,
        provider: LLMProvider,
        members: List[Persona],
        query: str,
        context: Optional[str],
        rounds: int = 2,
    ) -> List[MemberResponse]:
        """Multi-round debate between members."""
        all_responses: List[MemberResponse] = []

        for round_num in range(rounds):
            round_context = context or ""

            # Add previous round responses to context
            if all_responses:
                round_context += "\n\nPrevious responses:\n"
                for resp in all_responses:
                    round_context += f"\n{resp.persona.emoji} {resp.persona.name}: {resp.content}\n"

            round_query = (
                query
                if round_num == 0
                else f"[Round {round_num + 1}] Respond to your colleagues' points on: {query}"
            )

            round_responses = await self._consult_individual(
                provider, members, round_query, round_context
            )
            all_responses.extend(round_responses)

        return all_responses

    async def _consult_vote(
        self,
        provider: LLMProvider,
        members: List[Persona],
        query: str,
        context: Optional[str],
    ) -> List[MemberResponse]:
        """Get votes/decisions from members."""
        vote_query = f"""
{query}

Please provide:
1. Your VOTE: APPROVE / REJECT / ABSTAIN
2. Your CONFIDENCE: HIGH / MEDIUM / LOW
3. Brief reasoning (2-3 sentences)

Format your response as:
VOTE: [your vote]
CONFIDENCE: [your confidence]
REASONING: [your reasoning]
"""
        return await self._consult_individual(provider, members, vote_query, context)

    async def _get_member_response(
        self,
        provider: LLMProvider,
        member: Persona,
        query: str,
        context: Optional[str],
    ) -> MemberResponse:
        """Get a single member's response."""
        system_prompt = member.get_system_prompt()
        user_prompt = member.format_response_prompt(query, context)

        try:
            member_provider = self._get_member_provider(member, provider)
            params = self._resolve_member_generation_params(member)
            if member_provider is provider and not member.provider and not member.model:
                manager = self._get_llm_manager()
                response = await asyncio.wait_for(
                    manager.generate(
                        system_prompt=system_prompt,
                        user_prompt=user_prompt,
                        provider=self._provider_name,
                        fallback=True,
                        max_tokens=params["max_tokens"],
                        temperature=params["temperature"],
                    ),
                    timeout=120.0,
                )
            else:
                response = await asyncio.wait_for(
                    member_provider.complete(
                        system_prompt=system_prompt,
                        user_prompt=user_prompt,
                        max_tokens=params["max_tokens"],
                        temperature=params["temperature"],
                    ),
                    timeout=120.0,
                )
            content = response.text

            # Run response hooks
            for hook in self._response_hooks:
                content = hook(member, content)

            return MemberResponse(
                persona=member,
                content=content,
                timestamp=datetime.now(),
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

    async def _get_member_response_stream(
        self,
        provider: LLMProvider,
        member: Persona,
        query: str,
        context: Optional[str],
    ) -> AsyncIterator[Dict[str, Any]]:
        """Stream a single member's response."""
        yield {
            "type": "response_start",
            "persona_id": member.id,
            "persona_name": member.name,
            "persona_emoji": member.emoji,
        }

        system_prompt = member.get_system_prompt()
        user_prompt = member.format_response_prompt(query, context)

        try:
            member_provider = self._get_member_provider(member, provider)
            params = self._resolve_member_generation_params(member)
            content_parts: List[str] = []
            async for chunk in member_provider.stream_complete(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                max_tokens=params["max_tokens"],
                temperature=params["temperature"],
            ):
                content_parts.append(chunk)
                yield {
                    "type": "response_chunk",
                    "persona_id": member.id,
                    "content": chunk,
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
        except Exception as e:
            error_msg = str(e)
            if "API key" in error_msg or "authentication" in error_msg.lower():
                error_msg = (
                    f"API authentication failed: {error_msg}. "
                    f"Please check your API key for provider '{self._provider_name}'. "
                    f"Council AI will try fallback providers if available."
                )
            elif "rate limit" in error_msg.lower():
                error_msg = f"Rate limit exceeded: {error_msg}. Please try again later."

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

    async def _consult_individual_stream(
        self,
        provider: LLMProvider,
        members: List[Persona],
        query: str,
        context: Optional[str],
    ) -> AsyncIterator[Dict[str, Any]]:
        """Get individual responses from all members (streaming, sequential for simplicity)."""
        # Stream each member's response sequentially
        # TODO: Optimize to stream multiple members concurrently in future
        for member in members:
            yield {"type": "progress", "message": f"Consulting {member.name}..."}
            async for update in self._get_member_response_stream(provider, member, query, context):
                yield update

    async def _consult_sequential_stream(
        self,
        provider: LLMProvider,
        members: List[Persona],
        query: str,
        context: Optional[str],
    ) -> AsyncIterator[Dict[str, Any]]:
        """Get responses sequentially, each seeing previous responses (streaming)."""
        accumulated_context = context or ""

        for member in members:
            async for update in self._get_member_response_stream(
                provider, member, query, accumulated_context
            ):
                yield update
                if update.get("type") == "response_complete":
                    response = update["response"]
                    accumulated_context += (
                        f"\n\n{member.emoji} {member.name} said:\n{response.content}"
                    )

    async def _consult_debate_stream(
        self,
        provider: LLMProvider,
        members: List[Persona],
        query: str,
        context: Optional[str],
        rounds: int = 2,
    ) -> AsyncIterator[Dict[str, Any]]:
        """Debate mode with streaming (simplified - streams first round)."""
        # For streaming, we'll stream the first round of responses
        async for update in self._consult_individual_stream(provider, members, query, context):
            yield update

    async def _consult_vote_stream(
        self,
        provider: LLMProvider,
        members: List[Persona],
        query: str,
        context: Optional[str],
    ) -> AsyncIterator[Dict[str, Any]]:
        """Vote mode with streaming."""
        vote_query = f"""
{query}

Please provide:
1. Your VOTE: APPROVE / REJECT / ABSTAIN
2. Your CONFIDENCE: HIGH / MEDIUM / LOW
3. Brief reasoning (2-3 sentences)

Format your response as:
VOTE: [your vote]
CONFIDENCE: [your confidence]
REASONING: [your reasoning]
"""
        # Stream individual votes
        async for update in self._consult_individual_stream(provider, members, vote_query, context):
            yield update

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
            if (
                provider is self._provider
                and not self.config.synthesis_provider
                and not self.config.synthesis_model
            ):
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
            return response.text
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
            async for chunk in provider.stream_complete(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                max_tokens=max_tokens,
                temperature=self.config.temperature,
            ):
                yield chunk
        except Exception as e:
            logger.error(f"Failed to stream synthesis: {e}")
            # Fallback
            yield f"Error generating synthesis: {str(e)}"
