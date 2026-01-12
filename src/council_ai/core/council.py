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
from typing import Any, AsyncIterator, Callable, Dict, List, Optional, Union

from pydantic import BaseModel

from ..providers import (
    LLMProvider,
    get_provider,
    normalize_model_params,
    validate_model_params,
)
from .config import get_api_key
from .persona import Persona, PersonaManager, get_persona_manager
from .schemas import SynthesisSchema
from .session import ConsultationResult, MemberResponse, Session

ALL_MEMBERS_FAILED_MESSAGE = (
    "All council members failed to respond; see individual error messages."
)

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
            history: ConsultationHistory instance for auto-saving (optional)
        """
        self.config = config or CouncilConfig()
        self._persona_manager = persona_manager or get_persona_manager()
        self._members: Dict[str, Persona] = {}
        self._provider: Optional[LLMProvider] = None
        self._provider_name = provider
        self._api_key = api_key
        self._model = model
        self._base_url = base_url
        self._provider_cache: Dict[tuple[str, Optional[str], Optional[str]], LLMProvider] = {}
        self._sessions: List[Session] = []
        self._current_session: Optional[Session] = None
        self._history = history

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

    def _get_member_provider(self, member: Persona, default_provider: LLMProvider) -> LLMProvider:
        """Get or create a provider for a specific member's model override."""
        if not member.model or member.model == self._model:
            return default_provider

        cache_key = (self._provider_name, member.model, self._base_url)
        if cache_key not in self._provider_cache:
            self._provider_cache[cache_key] = get_provider(
                self._provider_name,
                api_key=self._api_key,
                model=member.model,
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
        structured_synthesis = None
        if mode in (ConsultationMode.SYNTHESIS, ConsultationMode.DEBATE):
            # Try structured synthesis if enabled in config
            if getattr(self.config, "use_structured_output", False):
                try:
                    structured_synthesis = await self._generate_structured_synthesis(
                        provider, query, context, responses
                    )
                    if structured_synthesis is None:
                        synthesis = await self._generate_synthesis(
                            provider, query, context, responses
                        )
                    else:
                        # Convert structured to text for backward compatibility
                        synthesis = self._format_structured_synthesis(structured_synthesis)
                except Exception:
                    # Fallback to free-form synthesis
                    synthesis = await self._generate_synthesis(provider, query, context, responses)
            else:
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

        # Auto-save to history if enabled
        if self._history:
            try:
                self._history.save(result)
            except Exception:
                # Don't fail consultation if history save fails
                import sys

                print("Warning: Failed to save consultation to history", file=sys.stderr)

        return result

    async def consult_stream(
        self,
        query: str,
        context: Optional[str] = None,
        mode: Optional[ConsultationMode] = None,
        members: Optional[List[str]] = None,
    ) -> AsyncIterator[Dict[str, Any]]:
        """
        Stream consultation results as they're generated.

        Yields progress updates and response chunks:
        - {"type": "progress", "message": "Consulting Rams..."}
        - {"type": "response_start", "persona_id": "rams", "persona_name": "Dieter Rams"}
        - {"type": "response_chunk", "persona_id": "rams", "content": "chunk of text"}
        - {"type": "response_complete", "persona_id": "rams", "response": MemberResponse}
        - {"type": "synthesis_start"}
        - {"type": "synthesis_chunk", "content": "chunk of synthesis"}
        - {"type": "synthesis_complete", "synthesis": "full synthesis"}
        - {"type": "complete", "result": ConsultationResult}
        """
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

        # Get responses based on mode (streaming)
        responses = []
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
            yield {"type": "synthesis_start"}
            synthesis_parts = []
            async for chunk in self._generate_synthesis_stream(provider, query, context, responses):
                yield {"type": "synthesis_chunk", "content": chunk}
                synthesis_parts.append(chunk)
            synthesis = "".join(synthesis_parts)
            yield {"type": "synthesis_complete", "synthesis": synthesis}

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
            except Exception:
                # Don't fail consultation if history save fails
                import sys

                print("Warning: Failed to save consultation to history", file=sys.stderr)

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
            member_provider = self._get_member_provider(member, provider)
            params = self._resolve_member_generation_params(member)
            content = await member_provider.complete(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                max_tokens=params["max_tokens"],
                temperature=params["temperature"],
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
            content_parts = []
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
        vote_query = f"{query}\n\nPlease vote: YES, NO, or ABSTAIN, and provide brief reasoning."
        async for update in self._consult_individual_stream(provider, members, vote_query, context):
            yield update

    async def _generate_synthesis_stream(
        self,
        provider: LLMProvider,
        query: str,
        context: Optional[str],
        responses: List[MemberResponse],
    ) -> AsyncIterator[str]:
        """Generate a synthesis of all member responses (streaming)."""
        responses_text = "\n\n".join(
            [
                f"### {r.persona.emoji} {r.persona.name} ({r.persona.title}):\n{r.content}"
                for r in responses
                if not r.error
            ]
        )
        if not responses_text.strip():
            yield ALL_MEMBERS_FAILED_MESSAGE
            return

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

        user_prompt = f"""
Original Query: {query}

{f"Context: {context}" if context else ""}

## Council Responses:

{responses_text}

---

Please synthesize these perspectives.
"""

        async for chunk in provider.stream_complete(
            system_prompt=synthesis_prompt,
            user_prompt=user_prompt,
            max_tokens=self.config.max_tokens_per_response * 2,
            temperature=0.5,  # Lower temperature for synthesis
        ):
            yield chunk

    async def _generate_structured_synthesis(
        self,
        provider: LLMProvider,
        query: str,
        context: Optional[str],
        responses: List[MemberResponse],
    ) -> Optional[SynthesisSchema]:
        """Generate a structured synthesis using JSON schema."""
        responses_text = "\n\n".join(
            [
                f"### {r.persona.emoji} {r.persona.name} ({r.persona.title}):\n{r.content}"
                for r in responses
                if not r.error
            ]
        )
        if not responses_text.strip():
            return None

        synthesis_prompt = (
            self.config.synthesis_prompt
            or """
You are a council facilitator synthesizing multiple perspectives.

Based on the individual council member responses below, provide a structured analysis with:
1. Key Points of Agreement
2. Key Points of Tension
3. Synthesized Recommendation
4. Action Items (with priority)
5. Recommendations (with confidence)
6. Pros and Cons (if applicable)

Be concise but comprehensive. Weight each advisor's input according to their expertise relevance.
"""
        )

        user_prompt = f"""
Original Query: {query}

{f"Context: {context}" if context else ""}

## Council Responses:

{responses_text}

---

Please synthesize these perspectives in the requested structured format.
"""

        # Get JSON schema from SynthesisSchema
        json_schema = SynthesisSchema.model_json_schema()

        try:
            structured_data = await provider.complete_structured(
                system_prompt=synthesis_prompt,
                user_prompt=user_prompt,
                json_schema=json_schema,
                max_tokens=self.config.max_tokens_per_response * 2,
                temperature=0.5,
            )

            # Validate and parse
            return SynthesisSchema(**structured_data)
        except Exception:
            # Fallback to None - will use free-form synthesis
            return None

    def _format_structured_synthesis(self, structured: Optional[SynthesisSchema]) -> str:
        """Format structured synthesis as markdown text."""
        if not structured:
            return ""

        lines = []

        if structured.key_points_of_agreement:
            lines.append("## Key Points of Agreement")
            lines.append("")
            for point in structured.key_points_of_agreement:
                lines.append(f"- {point}")
            lines.append("")

        if structured.key_points_of_tension:
            lines.append("## Key Points of Tension")
            lines.append("")
            for point in structured.key_points_of_tension:
                lines.append(f"- {point}")
            lines.append("")

        if structured.synthesized_recommendation:
            lines.append("## Synthesized Recommendation")
            lines.append("")
            lines.append(structured.synthesized_recommendation)
            lines.append("")

        if structured.action_items:
            lines.append("## Action Items")
            lines.append("")
            for item in structured.action_items:
                priority_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(
                    item.priority.lower(), "•"
                )
                owner_text = f" ({item.owner})" if item.owner else ""
                due_text = f" - Due: {item.due_date}" if item.due_date else ""
                lines.append(f"{priority_emoji} {item.description}{owner_text}{due_text}")
            lines.append("")

        if structured.recommendations:
            lines.append("## Recommendations")
            lines.append("")
            for rec in structured.recommendations:
                conf_emoji = {"high": "✓", "medium": "~", "low": "?"}.get(
                    rec.confidence.lower(), "•"
                )
                lines.append(f"### {conf_emoji} {rec.title}")
                lines.append(f"*Confidence: {rec.confidence}*")
                lines.append("")
                lines.append(rec.description)
                if rec.rationale:
                    lines.append(f"*Rationale: {rec.rationale}*")
                lines.append("")

        if structured.pros_cons:
            lines.append("## Pros and Cons")
            lines.append("")
            if structured.pros_cons.pros:
                lines.append("### Pros")
                for pro in structured.pros_cons.pros:
                    lines.append(f"- {pro}")
                lines.append("")
            if structured.pros_cons.cons:
                lines.append("### Cons")
                for con in structured.pros_cons.cons:
                    lines.append(f"- {con}")
                lines.append("")
            if structured.pros_cons.net_assessment:
                lines.append(f"**Net Assessment:** {structured.pros_cons.net_assessment}")
                lines.append("")

        return "\n".join(lines)

    async def _generate_synthesis(
        self,
        provider: LLMProvider,
        query: str,
        context: Optional[str],
        responses: List[MemberResponse],
    ) -> str:
        """Generate a synthesis of all member responses."""
        responses_text = "\n\n".join(
            [
                f"### {r.persona.emoji} {r.persona.name} ({r.persona.title}):\n{r.content}"
                for r in responses
                if not r.error
            ]
        )
        if not responses_text.strip():
            return ALL_MEMBERS_FAILED_MESSAGE

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

    def list_history(self, limit: Optional[int] = None, offset: int = 0) -> List[Dict[str, Any]]:
        """List saved consultations from history."""
        if not self._history:
            return []
        return self._history.list(limit=limit, offset=offset)

    def get_history(self, consultation_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific consultation from history."""
        if not self._history:
            return None
        return self._history.load(consultation_id)

    def search_history(self, query: str, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Search consultations in history."""
        if not self._history:
            return []
        return self._history.search(query, limit=limit)
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
