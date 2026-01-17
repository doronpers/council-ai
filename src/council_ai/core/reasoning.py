"""
Reasoning Modes for Council AI

Provides different reasoning strategies for LLMs to use deeper thinking.
"""

from enum import Enum
from typing import Optional


class ReasoningMode(str, Enum):
    """Different reasoning strategies for LLMs."""

    STANDARD = "standard"  # Default, no special reasoning
    CHAIN_OF_THOUGHT = "chain_of_thought"  # Step-by-step reasoning
    TREE_OF_THOUGHT = "tree_of_thought"  # Explore multiple reasoning paths
    REFLECTIVE = "reflective"  # Think, reflect, refine
    ANALYTICAL = "analytical"  # Deep analysis with evidence
    CREATIVE = "creative"  # Divergent thinking, multiple perspectives


def get_reasoning_prompt(mode: ReasoningMode, base_prompt: str) -> str:
    """Enhance a prompt with reasoning mode instructions.

    Args:
        mode: The reasoning mode to apply
        base_prompt: The original prompt

    Returns:
        Enhanced prompt with reasoning instructions
    """
    reasoning_instructions = {
        ReasoningMode.STANDARD: "",
        ReasoningMode.CHAIN_OF_THOUGHT: """
IMPORTANT: Use Chain-of-Thought reasoning. Break down your response into clear steps:
1. First, identify the key question or problem
2. Then, analyze each aspect step-by-step
3. Show your reasoning process explicitly
4. Finally, synthesize your conclusion

Format your response with clear step markers (Step 1:, Step 2:, etc.) showing your thinking process.
""",
        ReasoningMode.TREE_OF_THOUGHT: """
IMPORTANT: Use Tree-of-Thought reasoning. Explore multiple reasoning paths:
1. Identify 2-3 different approaches or perspectives
2. For each approach, think through the reasoning
3. Compare and contrast the different paths
4. Synthesize the best insights from each path

Format your response showing the different reasoning paths you explored.
""",
        ReasoningMode.REFLECTIVE: """
IMPORTANT: Use Reflective reasoning. Think deeply, then reflect and refine:
1. First Pass: Provide your initial analysis
2. Reflection: Critically examine your initial response
3. Refinement: Improve and deepen your analysis
4. Final Synthesis: Present your refined conclusion

Format your response with clear sections: Initial Analysis, Reflection, Refinement, Final Synthesis.
""",
        ReasoningMode.ANALYTICAL: """
IMPORTANT: Use Analytical reasoning. Provide deep analysis with evidence:
1. State your thesis or main point
2. Provide detailed evidence and reasoning
3. Consider counterarguments and limitations
4. Draw well-supported conclusions

Format your response with clear evidence, reasoning, and conclusions.
""",
        ReasoningMode.CREATIVE: """
IMPORTANT: Use Creative reasoning. Explore multiple perspectives and ideas:
1. Generate multiple different perspectives or solutions
2. Explore each perspective in depth
3. Identify connections and patterns
4. Synthesize novel insights

Format your response showing multiple perspectives and creative insights.
""",
    }

    instruction = reasoning_instructions.get(mode, "")
    if instruction:
        return f"{base_prompt}\n\n{instruction.strip()}"
    return base_prompt


def get_reasoning_suffix(mode: ReasoningMode) -> Optional[str]:
    """Get suffix to append to prompts for reasoning mode.

    Args:
        mode: The reasoning mode

    Returns:
        Suffix text or None
    """
    suffixes = {
        ReasoningMode.STANDARD: None,
        ReasoningMode.CHAIN_OF_THOUGHT: "\n\nRemember to show your step-by-step reasoning process.",
        ReasoningMode.TREE_OF_THOUGHT: "\n\nRemember to explore multiple reasoning paths.",
        ReasoningMode.REFLECTIVE: "\n\nRemember to reflect on and refine your thinking.",
        ReasoningMode.ANALYTICAL: "\n\nRemember to provide deep analysis with evidence.",
        ReasoningMode.CREATIVE: "\n\nRemember to explore multiple creative perspectives.",
    }
    return suffixes.get(mode)
