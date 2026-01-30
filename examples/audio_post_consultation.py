"""
Audio Post-Production Consultation Examples

Demonstrates Council AI consultations for audio post-production scenarios,
typical of Full Sail University teaching contexts.
"""

from council_ai import Council


def example_dialogue_editing():
    """Example: Dialogue editing consultation."""
    print("=" * 60)
    print("Example: Dialogue Editing Consultation")
    print("=" * 60)

    council = Council.for_domain("audio_post", api_key="your-api-key")

    query = """
    I'm working on a dialogue edit for a scene where the actor's performance
    is great, but there's noticeable room tone shift between takes. The production
    sound has a -48dB noise floor in the first half, but drops to -52dB in the
    second half after a cut. Should I:

    1. Use iZotope RX to match the noise floor levels?
    2. Add room tone to smooth the transition?
    3. ADR the entire scene for consistency?

    The director wants to preserve the performance, and we're on a tight deadline.
    """

    result = council.consult(query)

    print("\n" + result.to_markdown())
    print("\n" + "=" * 60)


def example_adr_decision():
    """Example: ADR necessity assessment."""
    print("=" * 60)
    print("Example: ADR Decision Consultation")
    print("=" * 60)

    council = Council.for_domain("audio_post", api_key="your-api-key")

    query = """
    I have a line where the actor says "I can't believe you did that" but there's
    a loud car passing by in the background that wasn't caught during production.
    The line is emotionally critical to the scene. The noise is broadband, centered
    around 2-4kHz, and completely masks the dialogue. The actor is available for ADR
    but the director is hesitant about losing the "moment" of the original take.

    What's the best approach here?
    """

    result = council.consult(query)

    print("\n" + result.to_markdown())
    print("\n" + "=" * 60)


def example_atmos_mixing():
    """Example: Atmos panning strategy."""
    print("=" * 60)
    print("Example: Atmos Mixing Consultation")
    print("=" * 60)

    council = Council.for_domain("audio_post", api_key="your-api-key")

    query = """
    I'm mixing a dialogue-heavy scene in Dolby Atmos. The scene has two characters
    having a conversation in a coffee shop. The director wants the ambience to
    feel immersive but not distract from the dialogue. Currently I have:

    - Dialogue panned to center bed
    - Coffee shop ambience as a 7.1.2 bed
    - Occasional sound effects (coffee machine, door chime) as objects

    The mix sounds good in the stage, but when I check the home delivery version,
    the dialogue feels buried. Should I:

    1. Reduce the ambience bed levels?
    2. Move more elements to objects for better control?
    3. Adjust the dialogue anchor differently for home vs theatrical?
    """

    result = council.consult(query)

    print("\n" + result.to_markdown())
    print("\n" + "=" * 60)


def example_noise_floor_management():
    """Example: Noise floor assessment."""
    print("=" * 60)
    print("Example: Noise Floor Management")
    print("=" * 60)

    council = Council.for_domain("audio_post", api_key="your-api-key")

    query = """
    I'm evaluating production sound for a student film. The dialogue tracks have
    a consistent -45dB noise floor, which is higher than I'd like. The noise is
    primarily air conditioning hum at 60Hz and some broadband hiss. The student
    wants to know if they need to ADR everything or if we can clean it up in post.

    What's your assessment? Should we attempt noise reduction, or is ADR the safer
    choice given the noise floor level?
    """

    result = council.consult(query)

    print("\n" + result.to_markdown())
    print("\n" + "=" * 60)


if __name__ == "__main__":
    print("\n🏛️ Council AI - Audio Post-Production Consultation Examples\n")
    print("These examples demonstrate typical scenarios from Full Sail University")
    print("audio post-production courses.\n")

    # Note: These examples require API keys to run
    print("Note: Set your API key in the code or environment variable.\n")

    # Uncomment to run examples:
    # example_dialogue_editing()
    # example_adr_decision()
    # example_atmos_mixing()
    # example_noise_floor_management()

    print("\nTo run these examples, uncomment the function calls above and")
    print("provide your API key.\n")
