# Synthesis Generation
async def _generate_synthesis(
    self,
    provider: LLMProvider,
    query: str,
    context: Optional[str],
    responses: List[MemberResponse],
) -> str:
    """Generate a synthesis of all member responses."""
    # Handle no responses case early
    if not responses:
        return "No responses to synthesize."

    # Build responses text, excluding errored entries, with consistent formatting
    responses_text = "\n\n".join(
        f"{resp.persona.emoji} **{resp.persona.name}** ({resp.persona.title}):\n{resp.content}"
        for resp in responses
        if not getattr(resp, "error", False)
    )

    # Synthesis prompt: prefer config override, else use detailed default
    synthesis_prompt = self.config.synthesis_prompt or (
        "You are synthesizing advice from a council of experts. "
        "Provide a comprehensive summary that:\n"
        "1. Identifies key themes and consensus points\n"
        "2. Highlights important differences or tensions\n"
        "3. Offers actionable recommendations\n"
        "4. Notes any risks or considerations\n\n"
        "Be concise but thorough."
    )

    # Compose user prompt with optional context
    user_prompt = f"""
Query: {query}
{f"Context: {context}" if context else ""}

Responses:
{responses_text}
""".strip()

    # Call provider to generate synthesis text
    result = await provider.complete(
        prompt=f"{synthesis_prompt}\n\n{user_prompt}",
        max_tokens=1000,
        temperature=0.3,
    )

    return result.strip()
