"""
Analysis Engine for Council AI.

Responsible for analyzing council consultations to extract structured insights,
calculate consensus, and identify points of contention.
"""

from __future__ import annotations

import json
import logging
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from ..providers import LLMProvider

logger = logging.getLogger(__name__)


class AnalysisResult(BaseModel):
    """Structured analysis of a consultation."""

    consensus_score: int = Field(
        ..., description="Numerical score 0-100 indicating level of agreement"
    )
    consensus_summary: str = Field(..., description="Brief summary of the consensus")
    key_themes: List[str] = Field(..., description="Main themes discussed")
    tensions: List[str] = Field(..., description="Specific points of disagreement or contention")
    recommendation: str = Field(..., description="Synthesized recommendation")


class AnalysisEngine:
    """Uses an LLM to analyze consultation results."""

    def __init__(self, provider: LLMProvider, model: Optional[str] = None):
        self.provider = provider
        self.model = model

    async def analyze(
        self, query: str, context: Optional[str], responses: List[Dict[str, Any]]
    ) -> AnalysisResult:
        """
        Analyze a set of responses to a query.

        Args:
            query: The original query
            context: Context provided
            responses: List of response dictionaries (must include 'persona.name' and 'content')

        Returns:
            AnalysisResult object
        """
        # Prepare the prompt
        response_text = ""
        for r in responses:
            persona_name = r.get("persona", {}).get("name", "Member")
            content = r.get("content", "")
            response_text += f"\n--- {persona_name} ---\n{content}\n"

        prompt = f"""
You are the Chief Analyst for an AI Advisory Council.
Your task is to analyze the following responses to a user query and provide a structured assessment.

QUERY: {query}
CONTEXT: {context or "None"}

RESPONSES:
{response_text}

---
INSTRUCTIONS:
1. Determine a Consensus Score (0-100), where 0 is total disagreement/chaos and 100 is unanimous agreement.
2. Summarize the consensus (or lack thereof) in one sentence.
3. Identify 3-5 key themes.
4. Identify distinct points of tension or disagreement between members.
5. Provide a single, actionable recommendation synthesized from the advice.

OUTPUT FORMAT:
Return ONLY a valid JSON object with the following structure:
{{
  "consensus_score": 85,
  "consensus_summary": "Most members agree on X, but differ on implementation details.",
  "key_themes": ["Theme 1", "Theme 2"],
  "tensions": ["Member A prefers X while Member B warns against it"],
  "recommendation": " Proceed with X but mitigate Y."
}}
"""

        try:
            # We use a lower temperature for analysis
            response = await self.provider.complete(
                system_prompt="You are a precise analytical engine. Output valid JSON only.",
                user_prompt=prompt,
                max_tokens=1000,
                temperature=0.2,
            )

            raw_text = response.text.strip()
            # Basic cleanup if code blocks are used
            if "```json" in raw_text:
                raw_text = raw_text.split("```json")[1].split("```")[0].strip()
            elif "```" in raw_text:
                raw_text = raw_text.split("```")[1].split("```")[0].strip()

            data = json.loads(raw_text)
            return AnalysisResult(**data)

        except Exception as e:
            logger.error(f"Analysis failed: {e}")
            # Fallback result
            return AnalysisResult(
                consensus_score=50,
                consensus_summary="Analysis failed. See individual responses.",
                key_themes=["Analysis Unavailable"],
                tensions=[],
                recommendation="Review individual responses manually.",
            )
