"""
LLM Response Reviewer - Supreme Court Style Review System

Provides endpoints for reviewing multiple LLM responses with a council of
"justices" who evaluate accuracy, consistency, insights, and errors.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import uuid4

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from council_ai import Council
from council_ai.core.config import ConfigManager, get_api_key
from council_ai.core.council import ConsultationMode, CouncilConfig
from council_ai.core.persona import list_personas

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/reviewer", tags=["reviewer"])


# Request/Response Models

class LLMResponse(BaseModel):
    """A single LLM response to review."""
    id: int = Field(..., description="Response number (1-5)")
    content: str = Field(..., min_length=1, max_length=100000)
    source: Optional[str] = Field(None, description="LLM source (e.g., 'GPT-4', 'Claude')")


class ReviewRequest(BaseModel):
    """Request to review multiple LLM responses."""
    question: str = Field(..., min_length=1, max_length=10000, description="The original question asked")
    responses: List[LLMResponse] = Field(..., min_length=2, max_length=5)

    # Council configuration
    justices: List[str] = Field(
        default=["dempsey", "kahneman", "rams", "treasure", "holman", "taleb", "grove"],
        description="List of justice persona IDs"
    )
    chair: str = Field(default="dempsey", description="Chair justice ID")
    vice_chair: str = Field(default="kahneman", description="Vice chair justice ID")
    include_sonotheia_experts: bool = Field(default=False, description="Include signal_analyst and compliance_auditor")

    # LLM configuration
    provider: Optional[str] = None
    model: Optional[str] = None
    base_url: Optional[str] = None
    api_key: Optional[str] = None
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(default=2000, ge=100, le=8000)


class JusticeOpinion(BaseModel):
    """A single justice's opinion on a response."""
    justice_id: str
    justice_name: str
    justice_emoji: str
    role: str  # "chair", "vice_chair", or "associate"
    opinion: str
    vote: str  # "approve", "approve_with_reservations", "dissent"


class ResponseAssessment(BaseModel):
    """Assessment of a single LLM response."""
    response_id: int
    source: Optional[str]
    scores: Dict[str, float]  # accuracy, factual_consistency, unique_insights, error_detection, sonotheia_relevance
    overall_score: float
    justifications: Dict[str, str]
    strengths: List[str]
    weaknesses: List[str]
    justice_opinions: List[JusticeOpinion]


class GroupDecision(BaseModel):
    """The council's collective decision."""
    ranking: List[int]  # Response IDs in order of preference
    winner: int  # Best response ID
    winner_score: float
    majority_opinion: str
    dissenting_opinions: List[str]
    vote_breakdown: Dict[str, int]  # {"approve": 5, "dissent": 2}


class SynthesizedResponse(BaseModel):
    """The synthesized best response."""
    combined_best: str  # Combined best parts from all responses
    refined_final: str  # Refined and polished version


class ReviewResult(BaseModel):
    """Complete review result."""
    review_id: str
    question: str
    responses_reviewed: int
    timestamp: str
    council_composition: Dict[str, Any]
    individual_assessments: List[ResponseAssessment]
    group_decision: GroupDecision
    synthesized_response: SynthesizedResponse


def _build_review_council(request: ReviewRequest) -> Council:
    """Build a council configured for response review."""
    config = ConfigManager().config
    provider = request.provider or config.api.provider
    model = request.model or config.api.model
    base_url = request.base_url or config.api.base_url
    api_key = request.api_key or get_api_key(provider)

    if not api_key:
        raise HTTPException(status_code=400, detail="API key is required for review.")

    council_config = CouncilConfig(
        temperature=request.temperature,
        max_tokens_per_response=request.max_tokens,
    )

    council = Council(
        api_key=api_key,
        provider=provider,
        model=model,
        base_url=base_url,
        config=council_config,
    )

    # Add justices with appropriate weights
    justices_to_add = list(request.justices)

    # Add Sonotheia experts if requested
    if request.include_sonotheia_experts:
        if "signal_analyst" not in justices_to_add:
            justices_to_add.append("signal_analyst")
        if "compliance_auditor" not in justices_to_add:
            justices_to_add.append("compliance_auditor")

    for justice_id in justices_to_add:
        try:
            weight = 1.0
            if justice_id == request.chair:
                weight = 1.5  # Chair has more influence
            elif justice_id == request.vice_chair:
                weight = 1.3  # Vice chair has slightly more influence
            council.add_member(justice_id, weight=weight)
        except ValueError as e:
            logger.warning(f"Could not add justice {justice_id}: {e}")

    return council


def _build_review_prompt(request: ReviewRequest) -> str:
    """Build the prompt for the review consultation."""
    responses_text = "\n\n".join([
        f"=== RESPONSE #{r.id} {'(from ' + r.source + ')' if r.source else ''} ===\n{r.content}"
        for r in request.responses
    ])

    prompt = f"""You are acting as a Supreme Court Justice reviewing multiple LLM responses to the same question.

## ORIGINAL QUESTION
{request.question}

## LLM RESPONSES TO REVIEW
{responses_text}

## YOUR TASK
As a justice on this review council, provide your assessment in the following JSON format:

```json
{{
  "response_assessments": [
    {{
      "response_id": 1,
      "scores": {{
        "accuracy": 8.5,
        "factual_consistency": 7.0,
        "unique_insights": 9.0,
        "error_detection": 8.0,
        "sonotheia_relevance": 6.0
      }},
      "overall_score": 7.7,
      "justifications": {{
        "accuracy": "Explanation of accuracy score...",
        "factual_consistency": "Explanation...",
        "unique_insights": "Explanation...",
        "error_detection": "Explanation...",
        "sonotheia_relevance": "Explanation if applicable..."
      }},
      "strengths": ["Strength 1", "Strength 2"],
      "weaknesses": ["Weakness 1", "Weakness 2"]
    }}
  ],
  "vote": "approve|approve_with_reservations|dissent",
  "opinion": "Your detailed judicial opinion explaining your assessment and vote...",
  "recommended_winner": 1,
  "dissent_reason": "If dissenting, explain why..."
}}
```

## EVALUATION CRITERIA
1. **Accuracy (1-10)**: Is the information correct and precise?
2. **Factual Consistency (1-10)**: Does it align with established facts and other responses?
3. **Unique Insights (1-10)**: Does it offer valuable perspectives not found elsewhere?
4. **Error Detection (1-10)**: Are there errors, hallucinations, or misleading statements? (Higher = fewer errors)
5. **Sonotheia Relevance (1-10)**: If applicable, how relevant is this to deepfake audio defense, voice authenticity, or regulated financial institutions?

Apply your unique expertise and perspective as {request.chair if hasattr(request, '_current_justice') else 'a justice'} to this review.

Provide your response ONLY as valid JSON matching the format above."""

    return prompt


def _build_synthesis_prompt(request: ReviewRequest, assessments: List[Dict]) -> str:
    """Build the prompt for synthesizing the best response."""
    responses_text = "\n\n".join([
        f"=== RESPONSE #{r.id} (Score: {next((a['overall_score'] for a in assessments if a.get('response_id') == r.id), 'N/A')}) ===\n{r.content}"
        for r in request.responses
    ])

    prompt = f"""Based on the council's review of multiple LLM responses, create an optimal synthesized response.

## ORIGINAL QUESTION
{request.question}

## REVIEWED RESPONSES WITH SCORES
{responses_text}

## YOUR TASK
Create two versions of an optimal response:

1. **Combined Best**: Take the strongest elements from each response and combine them into a comprehensive answer.

2. **Refined Final**: Starting from the combined version, refine and polish it into a single, authoritative response that:
   - Incorporates the most accurate information from all sources
   - Addresses any errors or gaps identified in the reviews
   - Presents information clearly and logically
   - Would be considered definitive on this topic

Respond in JSON format:
```json
{{
  "combined_best": "The combined response...",
  "refined_final": "The polished final response..."
}}
```"""

    return prompt


@router.get("/info")
async def reviewer_info() -> Dict[str, Any]:
    """Get information about the reviewer system."""
    personas = list_personas()

    # Categorize justices
    default_justices = ["dempsey", "kahneman", "rams", "treasure", "holman", "taleb", "grove"]
    sonotheia_experts = ["signal_analyst", "compliance_auditor"]

    available_justices = []
    for p in personas:
        justice_info = {
            "id": p.id,
            "name": p.name,
            "title": p.title,
            "emoji": p.emoji,
            "core_question": p.core_question,
            "is_default": p.id in default_justices,
            "is_sonotheia_expert": p.id in sonotheia_experts,
        }
        available_justices.append(justice_info)

    return {
        "version": "1.0.0",
        "default_justices": default_justices,
        "sonotheia_experts": sonotheia_experts,
        "available_justices": available_justices,
        "default_chair": "dempsey",
        "default_vice_chair": "kahneman",
        "evaluation_criteria": [
            {"id": "accuracy", "name": "Accuracy", "description": "Is the information correct and precise?"},
            {"id": "factual_consistency", "name": "Factual Consistency", "description": "Does it align with established facts?"},
            {"id": "unique_insights", "name": "Unique Insights", "description": "Does it offer valuable unique perspectives?"},
            {"id": "error_detection", "name": "Error Detection", "description": "Are there errors or hallucinations?"},
            {"id": "sonotheia_relevance", "name": "Sonotheia Relevance", "description": "Relevance to deepfake audio defense"},
        ],
    }


@router.post("/review")
async def review_responses(request: ReviewRequest) -> ReviewResult:
    """
    Review multiple LLM responses using the justice council.

    This endpoint performs a comprehensive review of 2-5 LLM responses,
    providing individual assessments, a group decision, and a synthesized
    optimal response.
    """
    council = _build_review_council(request)
    review_prompt = _build_review_prompt(request)

    try:
        # Get individual justice assessments
        result = await council.consult_async(
            review_prompt,
            mode=ConsultationMode.SYNTHESIS,
        )

        # Parse individual responses
        all_assessments = []
        justice_opinions = []

        for response in result.responses:
            try:
                # Try to parse JSON from the response
                content = response.content
                # Extract JSON from markdown code blocks if present
                if "```json" in content:
                    json_start = content.find("```json") + 7
                    json_end = content.find("```", json_start)
                    content = content[json_start:json_end].strip()
                elif "```" in content:
                    json_start = content.find("```") + 3
                    json_end = content.find("```", json_start)
                    content = content[json_start:json_end].strip()

                parsed = json.loads(content)

                # Determine role
                role = "associate"
                if response.persona_id == request.chair:
                    role = "chair"
                elif response.persona_id == request.vice_chair:
                    role = "vice_chair"

                justice_opinions.append({
                    "justice_id": response.persona_id,
                    "justice_name": response.persona_name,
                    "justice_emoji": response.persona_emoji or "👤",
                    "role": role,
                    "opinion": parsed.get("opinion", ""),
                    "vote": parsed.get("vote", "approve"),
                    "assessments": parsed.get("response_assessments", []),
                    "recommended_winner": parsed.get("recommended_winner", 1),
                })

            except (json.JSONDecodeError, KeyError) as e:
                logger.warning(f"Could not parse response from {response.persona_id}: {e}")
                # Create a basic opinion from non-JSON response
                role = "associate"
                if response.persona_id == request.chair:
                    role = "chair"
                elif response.persona_id == request.vice_chair:
                    role = "vice_chair"

                justice_opinions.append({
                    "justice_id": response.persona_id,
                    "justice_name": response.persona_name,
                    "justice_emoji": response.persona_emoji or "👤",
                    "role": role,
                    "opinion": response.content[:500] + "..." if len(response.content) > 500 else response.content,
                    "vote": "approve",
                    "assessments": [],
                    "recommended_winner": 1,
                })

        # Aggregate scores across justices
        response_scores = {r.id: {"scores": {}, "opinions": [], "strengths": [], "weaknesses": []} for r in request.responses}

        for opinion in justice_opinions:
            for assessment in opinion.get("assessments", []):
                rid = assessment.get("response_id")
                if rid in response_scores:
                    for criterion, score in assessment.get("scores", {}).items():
                        if criterion not in response_scores[rid]["scores"]:
                            response_scores[rid]["scores"][criterion] = []
                        response_scores[rid]["scores"][criterion].append(score)

                    response_scores[rid]["strengths"].extend(assessment.get("strengths", []))
                    response_scores[rid]["weaknesses"].extend(assessment.get("weaknesses", []))

            response_scores[opinion.get("recommended_winner", 1)]["opinions"].append(opinion)

        # Calculate final assessments
        individual_assessments = []
        for r in request.responses:
            scores_data = response_scores.get(r.id, {})
            avg_scores = {}
            for criterion, score_list in scores_data.get("scores", {}).items():
                if score_list:
                    avg_scores[criterion] = round(sum(score_list) / len(score_list), 1)
                else:
                    avg_scores[criterion] = 5.0  # Default

            # Ensure all criteria have scores
            for criterion in ["accuracy", "factual_consistency", "unique_insights", "error_detection", "sonotheia_relevance"]:
                if criterion not in avg_scores:
                    avg_scores[criterion] = 5.0

            overall = round(sum(avg_scores.values()) / len(avg_scores), 1) if avg_scores else 5.0

            # Get justice opinions for this response
            response_justice_opinions = [
                JusticeOpinion(
                    justice_id=op["justice_id"],
                    justice_name=op["justice_name"],
                    justice_emoji=op["justice_emoji"],
                    role=op["role"],
                    opinion=op["opinion"],
                    vote=op["vote"],
                )
                for op in justice_opinions
            ]

            assessment = ResponseAssessment(
                response_id=r.id,
                source=r.source,
                scores=avg_scores,
                overall_score=overall,
                justifications={k: f"Average score from {len(scores_data.get('scores', {}).get(k, []))} justices" for k in avg_scores},
                strengths=list(set(scores_data.get("strengths", [])))[:5],
                weaknesses=list(set(scores_data.get("weaknesses", [])))[:5],
                justice_opinions=response_justice_opinions,
            )
            individual_assessments.append(assessment)

        # Sort by overall score to get ranking
        sorted_assessments = sorted(individual_assessments, key=lambda a: a.overall_score, reverse=True)
        ranking = [a.response_id for a in sorted_assessments]
        winner = ranking[0] if ranking else 1
        winner_score = sorted_assessments[0].overall_score if sorted_assessments else 5.0

        # Count votes
        vote_breakdown = {"approve": 0, "approve_with_reservations": 0, "dissent": 0}
        dissenting_opinions = []
        for op in justice_opinions:
            vote = op.get("vote", "approve")
            if vote in vote_breakdown:
                vote_breakdown[vote] += 1
            if vote == "dissent":
                dissenting_opinions.append(f"{op['justice_emoji']} {op['justice_name']}: {op['opinion'][:200]}...")

        group_decision = GroupDecision(
            ranking=ranking,
            winner=winner,
            winner_score=winner_score,
            majority_opinion=result.synthesis or "The council has reached a consensus.",
            dissenting_opinions=dissenting_opinions,
            vote_breakdown=vote_breakdown,
        )

        # Generate synthesized response
        synthesis_prompt = _build_synthesis_prompt(request, [a.model_dump() for a in individual_assessments])
        synthesis_result = await council.consult_async(
            synthesis_prompt,
            mode=ConsultationMode.SYNTHESIS,
        )

        # Parse synthesis
        synthesized = SynthesizedResponse(
            combined_best="",
            refined_final="",
        )

        if synthesis_result.synthesis:
            try:
                content = synthesis_result.synthesis
                if "```json" in content:
                    json_start = content.find("```json") + 7
                    json_end = content.find("```", json_start)
                    content = content[json_start:json_end].strip()
                elif "```" in content:
                    json_start = content.find("```") + 3
                    json_end = content.find("```", json_start)
                    content = content[json_start:json_end].strip()

                parsed = json.loads(content)
                synthesized = SynthesizedResponse(
                    combined_best=parsed.get("combined_best", synthesis_result.synthesis),
                    refined_final=parsed.get("refined_final", synthesis_result.synthesis),
                )
            except json.JSONDecodeError:
                synthesized = SynthesizedResponse(
                    combined_best=synthesis_result.synthesis,
                    refined_final=synthesis_result.synthesis,
                )

        # Build council composition info
        council_composition = {
            "chair": {"id": request.chair, "name": next((p.name for p in list_personas() if p.id == request.chair), request.chair)},
            "vice_chair": {"id": request.vice_chair, "name": next((p.name for p in list_personas() if p.id == request.vice_chair), request.vice_chair)},
            "total_justices": len(justice_opinions),
            "includes_sonotheia_experts": request.include_sonotheia_experts,
        }

        return ReviewResult(
            review_id=str(uuid4()),
            question=request.question,
            responses_reviewed=len(request.responses),
            timestamp=datetime.utcnow().isoformat(),
            council_composition=council_composition,
            individual_assessments=individual_assessments,
            group_decision=group_decision,
            synthesized_response=synthesized,
        )

    except Exception as e:
        logger.error(f"Review failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/review/stream")
async def review_responses_stream(request: ReviewRequest) -> StreamingResponse:
    """Stream the review process as Server-Sent Events."""

    async def generate_stream():
        try:
            yield f"data: {json.dumps({'type': 'started', 'message': 'Review started...'})}\n\n"

            council = _build_review_council(request)
            review_prompt = _build_review_prompt(request)

            yield f"data: {json.dumps({'type': 'council_assembled', 'justices': len(request.justices)})}\n\n"

            # Stream individual assessments
            yield f"data: {json.dumps({'type': 'phase', 'phase': 'individual_review', 'message': 'Justices reviewing responses...'})}\n\n"

            async for update in council.consult_stream(
                review_prompt,
                mode=ConsultationMode.SYNTHESIS,
            ):
                if update.get("type") == "response_start":
                    yield f"data: {json.dumps({'type': 'justice_start', 'justice': update.get('persona_name', 'Unknown')})}\n\n"
                elif update.get("type") == "response_complete":
                    yield f"data: {json.dumps({'type': 'justice_complete', 'justice': update.get('persona_name', 'Unknown')})}\n\n"
                elif update.get("type") == "synthesis_start":
                    yield f"data: {json.dumps({'type': 'phase', 'phase': 'synthesis', 'message': 'Synthesizing group decision...'})}\n\n"

            # Final result (call non-streaming for complete result)
            result = await review_responses(request)
            yield f"data: {json.dumps({'type': 'complete', 'result': result.model_dump()})}\n\n"

        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'error': str(e)})}\n\n"

    return StreamingResponse(
        generate_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
