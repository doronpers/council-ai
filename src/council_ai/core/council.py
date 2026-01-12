"""
Council - The Core Advisory Council Engine

The Council class orchestrates multiple personas to provide
comprehensive advice, reviews, and decision support.
"""

from __future__ import annotations

import asyncio
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Union

from pydantic import BaseModel

from ..providers import LLMProvider, get_provider
from .config import get_api_key
from .persona import Persona, PersonaManager, get_persona_manager
from .session import ConsultationResult, MemberResponse, Session


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
    context_window: int = 10  # Number of previous exchanges to include


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
    ):
        """
        Initialize a Council.

        Args:
            api_key: API key for the LLM provider (or set via environment)
            provider: LLM provider name ("anthropic", "openai", etc.)
            config: Council configuration
            persona_manager: Custom persona manager (uses global if None)
        """
        self.config = config or CouncilConfig()
        self._persona_manager = persona_manager or get_persona_manager()
        self._members: Dict[str, Persona] = {}
        self._provider: Optional[LLMProvider] = None
        self._provider_name = provider
        self._api_key = api_key
        self._model = model
        self._base_url = base_url
        self._sessions: List[Session] = []
        self._current_session: Optional[Session] = None

        # Callbacks for extensibility
        self._pre_consult_hooks: List[Callable] = []
        self._post_consult_hooks: List[Callable] = []
        self._response_hooks: List[Callable] = []

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
                pass  # Skip if persona not found

        return council

    def _get_provider(self, fallback: bool = True) -> LLMProvider:
        """
        Get or create the LLM provider.
        
        Args:
            fallback: If True, will try fallback providers if primary fails
            
        Returns:
            LLMProvider instance
        """
        if self._provider is None:
            try:
                self._provider = get_provider(
                    self._provider_name,
                    api_key=self._api_key,
                    model=self._model,
                    base_url=self._base_url,
                )
            except (ValueError, ImportError) as e:
                if fallback:
                    # Try fallback providers in order: anthropic, gemini, openai
                    fallback_order = ["anthropic", "gemini", "openai"]
                    fallback_order = [p for p in fallback_order if p != self._provider_name]

                    last_error = e
                    for fallback_provider in fallback_order:
                        fallback_key = get_api_key(fallback_provider)
                        if fallback_key:
                            try:
                                self._provider = get_provider(
                                    fallback_provider,
                                    api_key=fallback_key,
                                    model=self._model,
                                    base_url=self._base_url,
                                )
                                import sys
                                print(
                                    f"Warning: {self._provider_name} provider failed ({str(e)}). "
                                    f"Falling back to {fallback_provider}.",
                                    file=sys.stderr,
                                )
                                self._provider_name = fallback_provider
                                break
                            except Exception:
                                continue

                    if self._provider is None:
                        raise ValueError(
                            f"Primary provider '{self._provider_name}' failed: {str(last_error)}. "
                            f"No fallback providers available. Please check your API keys. "
                            f"Run 'council providers --diagnose' for troubleshooting."
                        ) from last_error
                else:
                    raise
        return self._provider

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
    ) -> ConsultationResult:
        """Async version of consult."""
        mode = mode or self.config.mode
        provider = self._get_provider(fallback=True)

        # Get active members
        active_members = self._get_active_members(members)
        if not active_members:
            raise ValueError("No active council members")

        # Run pre-consult hooks
        for hook in self._pre_consult_hooks:
            query, context = hook(query, context)

        # Start session
        session = self._start_session(query, context)

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
        if mode in (ConsultationMode.SYNTHESIS, ConsultationMode.DEBATE):
            synthesis = await self._generate_synthesis(provider, query, context, responses)

        # Create result
        result = ConsultationResult(
            query=query,
            context=context,
            responses=responses,
            synthesis=synthesis,
            mode=mode,
            timestamp=datetime.now(),
        )

        # Update session
        session.add_consultation(result)

        # Run post-consult hooks
        for hook in self._post_consult_hooks:
            result = hook(result)

        return result

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
        responses = []
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
        all_responses = []

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
            content = await provider.complete(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                max_tokens=self.config.max_tokens_per_response,
                temperature=self.config.temperature,
            )

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

    async def _generate_synthesis(
        self,
        provider: LLMProvider,
        query: str,
        context: Optional[str],
        responses: List[MemberResponse],
    ) -> str:
        """Generate a synthesis of all member responses."""
        synthesis_prompt = (
            self.config.synthesis_prompt
            or """
You are a council facilitator synthesizing multiple perspectives.

Based on the individual council member responses below, provide:
1. **Key Points of Agreement**: Where do the advisors align?
2. **Key Points of Tension**: Where do they disagree or see different risks?
3. **Synthesized Recommendation**: What's the balanced path forward?
4. **Action Items**: Concrete next steps based on the collective wisdom

Be concise but comprehensive. Weight each advisor's input according to their expertise relevance.
"""
        )

        responses_text = "\n\n".join(
            [
                f"### {r.persona.emoji} {r.persona.name} ({r.persona.title}):\n{r.content}"
                for r in responses
                if not r.error
            ]
        )

        user_prompt = f"""
Original Query: {query}

{f"Context: {context}" if context else ""}

## Council Responses:

{responses_text}

---

Please synthesize these perspectives.
"""

        return await provider.complete(
            system_prompt=synthesis_prompt,
            user_prompt=user_prompt,
            max_tokens=self.config.max_tokens_per_response * 2,
            temperature=0.5,  # Lower temperature for synthesis
        )

    def _get_active_members(self, specific_members: Optional[List[str]] = None) -> List[Persona]:
        """Get list of active members, optionally filtered."""
        if specific_members:
            return [
                self._members[mid]
                for mid in specific_members
                if mid in self._members and self._members[mid].enabled
            ]
        return [m for m in self._members.values() if m.enabled]

    # ═══════════════════════════════════════════════════════════════════════════
    # Session Management
    # ═══════════════════════════════════════════════════════════════════════════

    def _start_session(self, query: str, context: Optional[str]) -> Session:
        """Start a new consultation session."""
        session = Session(
            council_name=self.config.name,
            members=[m.id for m in self._members.values()],
        )
        self._sessions.append(session)
        self._current_session = session
        return session

    def get_session_history(self, limit: int = 10) -> List[Session]:
        """Get recent session history."""
        return self._sessions[-limit:]

    def clear_history(self) -> None:
        """Clear session history."""
        self._sessions.clear()
        self._current_session = None

    # ═══════════════════════════════════════════════════════════════════════════
    # Hooks & Extensibility
    # ═══════════════════════════════════════════════════════════════════════════

    def add_pre_consult_hook(self, hook: Callable[[str, Optional[str]], tuple]) -> None:
        """Add a hook that runs before consultation."""
        self._pre_consult_hooks.append(hook)

    def add_post_consult_hook(
        self, hook: Callable[[ConsultationResult], ConsultationResult]
    ) -> None:
        """Add a hook that runs after consultation."""
        self._post_consult_hooks.append(hook)

    def add_response_hook(self, hook: Callable[[Persona, str], str]) -> None:
        """Add a hook that processes each member's response."""
        self._response_hooks.append(hook)

    # ═══════════════════════════════════════════════════════════════════════════
    # Serialization
    # ═══════════════════════════════════════════════════════════════════════════

    def to_dict(self) -> Dict[str, Any]:
        """Export council configuration."""
        return {
            "config": self.config.model_dump(),
            "members": [m.id for m in self._members.values()],
            "provider": self._provider_name,
            "model": self._model,
            "base_url": self._base_url,
        }

    def __repr__(self) -> str:
        member_count = len(self._members)
        enabled_count = len([m for m in self._members.values() if m.enabled])
        return f"Council(name='{self.config.name}', members={enabled_count}/{member_count})"
