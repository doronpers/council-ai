"""
Comprehensive tests for the reasoning module.

Tests cover:
- ReasoningMode enum validation
- Prompt enhancement for different reasoning strategies
- Reasoning suffix generation
- Integration with consultation workflows
- Prompt composition with reasoning modes
- Error handling for invalid modes
"""

import pytest

from council_ai.core.reasoning import ReasoningMode, get_reasoning_prompt, get_reasoning_suffix

# ============================================================================
# ReasoningMode Enum Tests
# ============================================================================


class TestReasoningModeEnum:
    """Test ReasoningMode enum and valid values."""

    def test_reasoning_mode_values_exist(self):
        """Test all expected reasoning mode values exist."""
        expected_modes = [
            "standard",
            "chain_of_thought",
            "tree_of_thought",
            "reflective",
            "analytical",
            "creative",
        ]

        for mode_name in expected_modes:
            mode = ReasoningMode(mode_name)
            assert mode is not None
            assert mode.value == mode_name

    def test_reasoning_mode_from_enum(self):
        """Test accessing reasoning modes via enum attributes."""
        assert ReasoningMode.STANDARD.value == "standard"
        assert ReasoningMode.CHAIN_OF_THOUGHT.value == "chain_of_thought"
        assert ReasoningMode.TREE_OF_THOUGHT.value == "tree_of_thought"
        assert ReasoningMode.REFLECTIVE.value == "reflective"
        assert ReasoningMode.ANALYTICAL.value == "analytical"
        assert ReasoningMode.CREATIVE.value == "creative"

    def test_reasoning_mode_string_comparison(self):
        """Test ReasoningMode can be compared as strings."""
        mode = ReasoningMode.STANDARD
        assert mode == ReasoningMode.STANDARD
        assert mode == "standard"
        # Value attribute gives the string representation
        assert mode.value == "standard"

    def test_reasoning_mode_invalid_value(self):
        """Test invalid reasoning mode raises ValueError."""
        with pytest.raises(ValueError):
            ReasoningMode("invalid_mode")

    def test_reasoning_mode_case_sensitive(self):
        """Test reasoning modes are case-sensitive."""
        with pytest.raises(ValueError):
            ReasoningMode("STANDARD")

    def test_reasoning_mode_list(self):
        """Test listing all reasoning modes."""
        modes = list(ReasoningMode)
        assert len(modes) == 6
        assert ReasoningMode.STANDARD in modes
        assert ReasoningMode.CHAIN_OF_THOUGHT in modes


# ============================================================================
# Prompt Enhancement Tests
# ============================================================================


class TestPromptEnhancement:
    """Test prompt enhancement with reasoning instructions."""

    def test_standard_mode_no_enhancement(self):
        """Test STANDARD mode returns unchanged prompt."""
        base_prompt = "What is machine learning?"
        enhanced = get_reasoning_prompt(ReasoningMode.STANDARD, base_prompt)
        assert enhanced == base_prompt

    def test_chain_of_thought_enhancement(self):
        """Test CHAIN_OF_THOUGHT adds step-by-step instructions."""
        base_prompt = "What is machine learning?"
        enhanced = get_reasoning_prompt(ReasoningMode.CHAIN_OF_THOUGHT, base_prompt)

        assert base_prompt in enhanced
        assert "step" in enhanced.lower() or "Step" in enhanced
        assert "reasoning" in enhanced.lower()

    def test_tree_of_thought_enhancement(self):
        """Test TREE_OF_THOUGHT adds multi-path reasoning instructions."""
        base_prompt = "How should we approach this problem?"
        enhanced = get_reasoning_prompt(ReasoningMode.TREE_OF_THOUGHT, base_prompt)

        assert base_prompt in enhanced
        assert "path" in enhanced.lower() or "approach" in enhanced.lower()
        assert "explore" in enhanced.lower() or "Explore" in enhanced

    def test_reflective_enhancement(self):
        """Test REFLECTIVE adds reflection and refinement instructions."""
        base_prompt = "What are the implications?"
        enhanced = get_reasoning_prompt(ReasoningMode.REFLECTIVE, base_prompt)

        assert base_prompt in enhanced
        assert "reflect" in enhanced.lower()
        assert "refine" in enhanced.lower() or "Refine" in enhanced

    def test_analytical_enhancement(self):
        """Test ANALYTICAL adds evidence and reasoning instructions."""
        base_prompt = "Analyze this data."
        enhanced = get_reasoning_prompt(ReasoningMode.ANALYTICAL, base_prompt)

        assert base_prompt in enhanced
        assert "evidence" in enhanced.lower() or "Evidence" in enhanced
        assert "analysis" in enhanced.lower() or "Analysis" in enhanced

    def test_creative_enhancement(self):
        """Test CREATIVE adds multiple perspectives instructions."""
        base_prompt = "Generate ideas for improvement."
        enhanced = get_reasoning_prompt(ReasoningMode.CREATIVE, base_prompt)

        assert base_prompt in enhanced
        assert "perspective" in enhanced.lower() or "Perspective" in enhanced
        assert "creative" in enhanced.lower() or "Creative" in enhanced

    def test_enhancement_preserves_base_prompt(self):
        """Test all modes preserve the base prompt."""
        base_prompt = "Tell me about quantum computing."

        for mode in ReasoningMode:
            enhanced = get_reasoning_prompt(mode, base_prompt)
            # Either exactly the same (STANDARD) or contains the base
            if mode != ReasoningMode.STANDARD:
                assert base_prompt in enhanced
            else:
                assert enhanced == base_prompt

    def test_enhancement_adds_structure(self):
        """Test enhancements add structure to prompts."""
        base_prompt = "Solve this puzzle."

        for mode in [
            ReasoningMode.CHAIN_OF_THOUGHT,
            ReasoningMode.TREE_OF_THOUGHT,
            ReasoningMode.ANALYTICAL,
        ]:
            enhanced = get_reasoning_prompt(mode, base_prompt)
            # Should be longer due to instructions
            assert len(enhanced) > len(base_prompt)

    def test_prompt_with_special_characters(self):
        """Test enhancement works with special characters in prompt."""
        base_prompt = 'What\'s the "best" approach? (A) or (B)?'
        enhanced = get_reasoning_prompt(ReasoningMode.CHAIN_OF_THOUGHT, base_prompt)

        assert base_prompt in enhanced
        assert '"' in enhanced
        assert "(" in enhanced


# ============================================================================
# Reasoning Suffix Tests
# ============================================================================


class TestReasoningSuffix:
    """Test reasoning suffix generation."""

    def test_standard_mode_no_suffix(self):
        """Test STANDARD mode returns None suffix."""
        suffix = get_reasoning_suffix(ReasoningMode.STANDARD)
        assert suffix is None

    def test_chain_of_thought_suffix(self):
        """Test CHAIN_OF_THOUGHT returns appropriate suffix."""
        suffix = get_reasoning_suffix(ReasoningMode.CHAIN_OF_THOUGHT)

        assert suffix is not None
        assert isinstance(suffix, str)
        assert "step" in suffix.lower() or "Step" in suffix
        assert "reasoning" in suffix.lower() or "process" in suffix.lower()

    def test_tree_of_thought_suffix(self):
        """Test TREE_OF_THOUGHT returns appropriate suffix."""
        suffix = get_reasoning_suffix(ReasoningMode.TREE_OF_THOUGHT)

        assert suffix is not None
        assert "path" in suffix.lower() or "explore" in suffix.lower()

    def test_reflective_suffix(self):
        """Test REFLECTIVE returns appropriate suffix."""
        suffix = get_reasoning_suffix(ReasoningMode.REFLECTIVE)

        assert suffix is not None
        assert "reflect" in suffix.lower()

    def test_analytical_suffix(self):
        """Test ANALYTICAL returns appropriate suffix."""
        suffix = get_reasoning_suffix(ReasoningMode.ANALYTICAL)

        assert suffix is not None
        assert "analysis" in suffix.lower() or "evidence" in suffix.lower()

    def test_creative_suffix(self):
        """Test CREATIVE returns appropriate suffix."""
        suffix = get_reasoning_suffix(ReasoningMode.CREATIVE)

        assert suffix is not None
        assert "creative" in suffix.lower() or "perspective" in suffix.lower()

    def test_suffix_format(self):
        """Test all suffixes start with newline for formatting."""
        for mode in ReasoningMode:
            suffix = get_reasoning_suffix(mode)
            if suffix is not None:
                assert suffix.startswith("\n"), f"{mode} suffix should start with newline"

    def test_all_modes_have_suffix_or_none(self):
        """Test every mode returns either string or None."""
        for mode in ReasoningMode:
            suffix = get_reasoning_suffix(mode)
            assert suffix is None or isinstance(suffix, str)

    def test_suffix_uniqueness(self):
        """Test different modes return different suffixes."""
        suffixes = {}

        for mode in ReasoningMode:
            suffix = get_reasoning_suffix(mode)
            # Only non-None suffixes
            if suffix is not None:
                suffixes[mode] = suffix

        # Check that all non-None suffixes are different
        suffix_values = list(suffixes.values())
        assert len(suffix_values) == len(set(suffix_values)), "Suffixes should be unique"


# ============================================================================
# Prompt Composition Tests
# ============================================================================


class TestPromptComposition:
    """Test combining enhancement and suffixes."""

    def test_enhancement_and_suffix_together(self):
        """Test using enhancement and suffix together."""
        base_prompt = "What is AI?"
        mode = ReasoningMode.CHAIN_OF_THOUGHT

        enhanced = get_reasoning_prompt(mode, base_prompt)
        suffix = get_reasoning_suffix(mode)

        if suffix:
            combined = enhanced + suffix
            assert base_prompt in combined
            assert "step" in combined.lower() or "Step" in combined

    def test_multiple_mode_prompts(self):
        """Test composing prompts for multiple modes."""
        base_prompt = "Compare these options."
        modes = [
            ReasoningMode.ANALYTICAL,
            ReasoningMode.TREE_OF_THOUGHT,
            ReasoningMode.REFLECTIVE,
        ]

        prompts = []
        for mode in modes:
            enhanced = get_reasoning_prompt(mode, base_prompt)
            suffix = get_reasoning_suffix(mode)
            if suffix:
                enhanced += suffix
            prompts.append(enhanced)

        # All should be different
        assert len(set(prompts)) == len(prompts)
        # All should contain base prompt
        for prompt in prompts:
            assert base_prompt in prompt

    def test_prompt_length_varies_by_mode(self):
        """Test that prompt length increases with reasoning complexity."""
        base_prompt = "Solve the problem."
        lengths = {}

        for mode in ReasoningMode:
            enhanced = get_reasoning_prompt(mode, base_prompt)
            suffix = get_reasoning_suffix(mode)
            if suffix:
                enhanced += suffix
            lengths[mode] = len(enhanced)

        # STANDARD should be shortest
        assert lengths[ReasoningMode.STANDARD] <= lengths[ReasoningMode.CHAIN_OF_THOUGHT]
        # Complex modes should be longer
        assert lengths[ReasoningMode.REFLECTIVE] > lengths[ReasoningMode.STANDARD]


# ============================================================================
# Integration Tests
# ============================================================================


class TestReasoningIntegration:
    """Test reasoning modes in consultation scenarios."""

    def test_reasoning_mode_for_analysis_query(self):
        """Test selecting ANALYTICAL for data analysis queries."""
        query = "Analyze the quarterly financial data."
        mode = ReasoningMode.ANALYTICAL

        enhanced = get_reasoning_prompt(mode, query)
        assert "evidence" in enhanced.lower() or "analysis" in enhanced.lower()

    def test_reasoning_mode_for_problem_solving(self):
        """Test selecting CHAIN_OF_THOUGHT for problem-solving."""
        query = "How should we solve this complex issue?"
        mode = ReasoningMode.CHAIN_OF_THOUGHT

        enhanced = get_reasoning_prompt(mode, query)
        assert "step" in enhanced.lower() or "Step" in enhanced

    def test_reasoning_mode_for_brainstorming(self):
        """Test selecting CREATIVE for brainstorming."""
        query = "Generate innovative solutions for customer retention."
        mode = ReasoningMode.CREATIVE

        enhanced = get_reasoning_prompt(mode, query)
        assert "perspective" in enhanced.lower() or "creative" in enhanced.lower()

    def test_reasoning_mode_for_strategic_decision(self):
        """Test selecting REFLECTIVE for strategic decisions."""
        query = "Should we restructure our organization?"
        mode = ReasoningMode.REFLECTIVE

        enhanced = get_reasoning_prompt(mode, query)
        assert "reflect" in enhanced.lower()

    def test_reasoning_mode_for_exploration(self):
        """Test selecting TREE_OF_THOUGHT for exploration."""
        query = "What are different approaches to market expansion?"
        mode = ReasoningMode.TREE_OF_THOUGHT

        enhanced = get_reasoning_prompt(mode, query)
        assert "path" in enhanced.lower() or "approach" in enhanced.lower()

    def test_mixed_reasoning_scenarios(self):
        """Test different reasoning modes for various scenarios."""
        scenarios = [
            ("technical_debug", ReasoningMode.CHAIN_OF_THOUGHT),
            ("policy_analysis", ReasoningMode.ANALYTICAL),
            ("creative_campaign", ReasoningMode.CREATIVE),
            ("strategic_review", ReasoningMode.REFLECTIVE),
            ("option_comparison", ReasoningMode.TREE_OF_THOUGHT),
        ]

        for _scenario_type, mode in scenarios:
            suffix = get_reasoning_suffix(mode)
            # Each mode should have proper suffix (or None for STANDARD)
            if mode != ReasoningMode.STANDARD:
                assert suffix is not None


# ============================================================================
# Edge Cases and Error Handling
# ============================================================================


class TestReasoningEdgeCases:
    """Test edge cases and error conditions."""

    def test_empty_prompt(self):
        """Test handling empty prompt."""
        empty_prompt = ""
        mode = ReasoningMode.CHAIN_OF_THOUGHT

        enhanced = get_reasoning_prompt(mode, empty_prompt)
        # Should still generate instructions
        assert len(enhanced) > 0
        assert "step" in enhanced.lower() or "Step" in enhanced

    def test_very_long_prompt(self):
        """Test handling very long prompt."""
        long_prompt = "Question: " + ("A" * 5000)
        mode = ReasoningMode.ANALYTICAL

        enhanced = get_reasoning_prompt(mode, long_prompt)
        assert long_prompt in enhanced
        assert len(enhanced) > len(long_prompt)

    def test_prompt_with_newlines(self):
        """Test prompt with multiple newlines."""
        multiline_prompt = "Question 1?\nQuestion 2?\nQuestion 3?"
        mode = ReasoningMode.REFLECTIVE

        enhanced = get_reasoning_prompt(mode, multiline_prompt)
        assert multiline_prompt in enhanced

    def test_unicode_in_prompt(self):
        """Test prompt with unicode characters."""
        unicode_prompt = "What about émojis 🎯 and spëcial çharacters?"
        mode = ReasoningMode.CHAIN_OF_THOUGHT

        enhanced = get_reasoning_prompt(mode, unicode_prompt)
        assert unicode_prompt in enhanced
        assert "🎯" in enhanced

    def test_reasoning_mode_iteration(self):
        """Test iterating over all reasoning modes."""
        count = 0
        for mode in ReasoningMode:
            suffix = get_reasoning_suffix(mode)
            enhanced = get_reasoning_prompt(mode, "test")
            assert suffix is None or isinstance(suffix, str)
            assert isinstance(enhanced, str)
            count += 1

        assert count == 6, "Should have 6 reasoning modes"

    def test_consistency_of_mode_values(self):
        """Test consistency between enum value and string."""
        for mode in ReasoningMode:
            # Mode should equal its value as string
            assert mode == mode.value
            # Mode should be created from its value
            assert ReasoningMode(mode.value) == mode


# ============================================================================
# Documentation and Help Tests
# ============================================================================


class TestReasoningDocumentation:
    """Test that reasoning modes are documented and discoverable."""

    def test_reasoning_mode_has_docstring(self):
        """Test ReasoningMode enum has documentation."""
        assert ReasoningMode.__doc__ is not None

    def test_reasoning_functions_have_docstrings(self):
        """Test reasoning functions are documented."""
        assert get_reasoning_prompt.__doc__ is not None
        assert get_reasoning_suffix.__doc__ is not None

    def test_all_modes_produce_non_empty_instructions(self):
        """Test non-standard modes produce non-empty instructions."""
        for mode in ReasoningMode:
            if mode != ReasoningMode.STANDARD:
                enhanced = get_reasoning_prompt(mode, "test")
                # Enhanced should be longer than base
                assert len(enhanced) > 4

    def test_reasoning_mode_names_meaningful(self):
        """Test reasoning mode names are meaningful."""
        meaningful_names = {
            "standard": "baseline",
            "chain_of_thought": "step_based",
            "tree_of_thought": "multi_path",
            "reflective": "self_reflective",
            "analytical": "evidence_based",
            "creative": "divergent",
        }

        for name in meaningful_names:
            # Name should convey purpose
            assert len(name) > 0
            assert isinstance(name, str)
            # Validate that the name is a valid ReasoningMode enum value
            _ = ReasoningMode(name)
