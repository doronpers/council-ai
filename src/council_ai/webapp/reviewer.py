"""
LLM Response Reviewer - Supreme Court Style Review System

Provides endpoints for reviewing multiple LLM responses with a council of
"justices" who evaluate accuracy, consistency, insights, and errors.
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import re
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, TypeVar
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


# Google Docs Import Models
class GoogleDocsImportRequest(BaseModel):
    """Request to import from Google Docs."""

    url: Optional[str] = Field(None, description="Google Docs URL")
    content: Optional[str] = Field(None, description="Exported text/HTML content from Google Docs")


class GoogleDocsImportResponse(BaseModel):
    """Response from Google Docs import."""

    question: str
    responses: List[LLMResponse]
    success: bool
    message: Optional[str] = None


# Error Response Models
class ErrorResponse(BaseModel):
    """Structured error response."""

    error: str
    error_type: str
    detail: Optional[str] = None
    suggestion: Optional[str] = None


# Request/Response Models


class LLMResponse(BaseModel):
    """A single LLM response to review."""

    id: int = Field(..., description="Response number (1-5)")
    content: str = Field(..., min_length=1, max_length=100000)
    source: Optional[str] = Field(None, description="LLM source (e.g., 'GPT-4', 'Claude')")


class ReviewRequest(BaseModel):
    """Request to review multiple LLM responses."""

    question: str = Field(
        ..., min_length=1, max_length=10000, description="The original question asked"
    )
    responses: List[LLMResponse] = Field(..., min_length=2, max_length=5)

    # Council configuration
    justices: List[str] = Field(
        default=["dempsey", "kahneman", "rams", "treasure", "holman", "taleb", "grove"],
        description="List of justice persona IDs",
    )
    chair: str = Field(default="dempsey", description="Chair justice ID")
    vice_chair: str = Field(default="kahneman", description="Vice chair justice ID")
    include_sonotheia_experts: bool = Field(
        default=False, description="Include signal_analyst and compliance_auditor"
    )

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
    scores: Dict[
        str, float
    ]  # accuracy, factual_consistency, unique_insights, error_detection, sonotheia_relevance
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
    partial_results: bool = Field(
        default=False, description="True if some results are missing due to errors"
    )
    warnings: List[str] = Field(
        default_factory=list, description="Warnings about partial failures or rate limits"
    )


# Utility Functions

T = TypeVar("T")


async def _retry_with_backoff(
    func: Callable[..., Any],
    max_retries: int = 3,
    base_delay: float = 1.0,
    *args: Any,
    **kwargs: Any,
) -> T:
    """
    Retry an async function with exponential backoff on rate limit errors.

    Args:
        func: Async function to retry
        max_retries: Maximum number of retry attempts
        base_delay: Base delay in seconds (will be multiplied by 2^attempt)
        *args, **kwargs: Arguments to pass to func

    Returns:
        Result from func

    Raises:
        Last exception if all retries fail
    """
    last_exception = None

    for attempt in range(max_retries + 1):
        try:
            if asyncio.iscoroutinefunction(func):
                return await func(*args, **kwargs)
            else:
                return func(*args, **kwargs)
        except Exception as e:
            last_exception = e
            error_msg = str(e).lower()

            # Check if it's a rate limit error
            is_rate_limit = (
                "rate limit" in error_msg
                or "429" in error_msg
                or "rate_limit_error" in error_msg
                or "would exceed the rate limit" in error_msg
            )

            if not is_rate_limit or attempt >= max_retries:
                # Not a rate limit error or retries exhausted
                raise

            # Calculate delay with exponential backoff
            delay = base_delay * (2**attempt)
            logger.warning(
                f"Rate limit error (attempt {attempt + 1}/{max_retries + 1}): {e}. "
                f"Retrying in {delay:.1f}s..."
            )
            await asyncio.sleep(delay)

    # Should never reach here, but just in case
    if last_exception:
        raise last_exception
    raise RuntimeError("Retry logic failed unexpectedly")


def _parse_anthropic_error(error: Exception) -> Dict[str, Any]:
    """
    Parse Anthropic API error to extract rate limit details.

    Args:
        error: The exception from Anthropic API

    Returns:
        Dictionary with parsed error information
    """
    error_str = str(error)
    error_dict = {
        "type": "unknown",
        "message": error_str,
        "rate_limit_type": None,
        "current_usage": None,
        "limit": None,
        "retry_after": None,
        "suggestion": None,
    }

    # Check for rate limit error
    if "rate limit" in error_str.lower() or "429" in error_str or "rate_limit_error" in error_str:
        error_dict["type"] = "rate_limit"

        # Try to extract rate limit details from error message
        # Example: "10,000 input tokens per minute"
        token_match = re.search(
            r"(\d+[,\d]*)\s*(input|output)?\s*tokens?\s*per\s*(minute|hour|day)",
            error_str,
            re.IGNORECASE,
        )
        if token_match:
            error_dict["limit"] = token_match.group(1).replace(",", "")
            error_dict["rate_limit_type"] = token_match.group(2) or "input"
            error_dict["suggestion"] = (
                f"Rate limit: {error_dict['limit']} {error_dict['rate_limit_type']} tokens per minute. "
                "Try reducing the number of justices, shortening prompts, or waiting a minute."
            )
        else:
            error_dict["suggestion"] = (
                "Rate limit exceeded. Try reducing the number of justices, "
                "shortening prompts, or waiting a minute before retrying."
            )

    # Check for authentication errors
    elif (
        "api key" in error_str.lower()
        or "authentication" in error_str.lower()
        or "401" in error_str
    ):
        error_dict["type"] = "authentication"
        error_dict["suggestion"] = "Check your API key configuration and ensure it's valid."

    # Check for invalid request
    elif "invalid" in error_str.lower() or "400" in error_str:
        error_dict["type"] = "invalid_request"
        error_dict["suggestion"] = "Check your request parameters and try again."

    return error_dict


def _estimate_tokens(text: str) -> int:
    """
    Estimate token count for a text string.
    Uses a simple heuristic: ~4 characters per token for English text.

    Args:
        text: Text to estimate tokens for

    Returns:
        Estimated token count
    """
    if not text:
        return 0
    # Rough estimate: 1 token ≈ 4 characters for English
    return len(text) // 4


def _repair_json(json_str: str) -> Optional[str]:
    """
    Attempt to repair common JSON malformations.

    Args:
        json_str: Potentially malformed JSON string

    Returns:
        Repaired JSON string or None if repair failed
    """
    if not json_str:
        return None

    try:
        # Try parsing first - if it works, no repair needed
        json.loads(json_str)
        return json_str
    except json.JSONDecodeError:
        pass

    repaired = json_str

    # Fix single quotes to double quotes (but not inside strings)
    # This is tricky, so we'll be conservative
    repaired = re.sub(r"'(\w+)':", r'"\1":', repaired)
    repaired = re.sub(r":\s*'([^']*)'", r': "\1"', repaired)

    # Remove trailing commas before closing brackets/braces
    repaired = re.sub(r",(\s*[}\]])", r"\1", repaired)

    # Fix unescaped quotes in strings (basic attempt)
    # This is complex, so we'll skip it for now

    try:
        # Test if repair worked
        json.loads(repaired)
        return repaired
    except json.JSONDecodeError:
        return None


def _extract_json_balanced(text: str) -> Optional[str]:
    """
    Extract the largest valid JSON object using balanced bracket matching.

    Args:
        text: Text that may contain JSON

    Returns:
        Extracted JSON string or None
    """
    if not text:
        return None

    # Find all potential JSON object starts
    start_positions = []
    for i, char in enumerate(text):
        if char == "{":
            start_positions.append(i)

    # Try to find complete JSON objects
    for start in reversed(start_positions):  # Start from the end to get the largest
        depth = 0
        in_string = False
        escape_next = False

        for i in range(start, len(text)):
            char = text[i]

            if escape_next:
                escape_next = False
                continue

            if char == "\\":
                escape_next = True
                continue

            if char == '"' and not escape_next:
                in_string = not in_string
                continue

            if in_string:
                continue

            if char == "{":
                depth += 1
            elif char == "}":
                depth -= 1
                if depth == 0:
                    # Found a complete JSON object
                    json_candidate = text[start : i + 1]
                    try:
                        json.loads(json_candidate)
                        return json_candidate
                    except json.JSONDecodeError:
                        continue

    return None


def _extract_and_parse_json(content: str) -> tuple[Optional[Dict[str, Any]], Optional[str]]:
    """
    Multi-strategy JSON extraction and parsing.

    Args:
        content: Text content that may contain JSON

    Returns:
        Tuple of (parsed_dict, error_message)
        Returns (None, error_message) if parsing fails
    """
    if not content or not content.strip():
        return None, "Empty content"

    strategies = [
        ("direct_parse", lambda: json.loads(content.strip())),
        ("markdown_json_block", lambda: _extract_from_markdown(content, "json")),
        ("markdown_code_block", lambda: _extract_from_markdown(content, None)),
        ("json_repair", lambda: _try_repair_and_parse(content)),
        ("balanced_extraction", lambda: _try_balanced_extraction(content)),
    ]

    for strategy_name, strategy_func in strategies:
        try:
            result = strategy_func()
            if result:
                logger.debug(f"JSON parsing succeeded using strategy: {strategy_name}")
                return result, None
        except Exception as e:
            logger.debug(f"JSON parsing strategy '{strategy_name}' failed: {e}")
            continue

    return None, "All JSON parsing strategies failed"


def _extract_from_markdown(content: str, lang: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Extract JSON from markdown code blocks."""
    if lang:
        pattern = rf"```{lang}\s*\n?(.*?)```"
    else:
        pattern = r"```\s*\n?(.*?)```"

    matches = re.findall(pattern, content, re.DOTALL)
    for match in matches:
        try:
            return json.loads(match.strip())
        except json.JSONDecodeError:
            continue
    return None


def _try_repair_and_parse(content: str) -> Optional[Dict[str, Any]]:
    """Try to repair JSON and parse it."""
    repaired = _repair_json(content)
    if repaired:
        try:
            return json.loads(repaired)
        except json.JSONDecodeError:
            pass
    return None


def _try_balanced_extraction(content: str) -> Optional[Dict[str, Any]]:
    """Try balanced bracket extraction and parse."""
    extracted = _extract_json_balanced(content)
    if extracted:
        try:
            return json.loads(extracted)
        except json.JSONDecodeError:
            pass
    return None


def _extract_data_from_text(text: str) -> Dict[str, Any]:
    """
    Extract key data from text when JSON parsing fails.
    Uses regex patterns to find scores, votes, and opinions.

    Args:
        text: Text content to extract data from

    Returns:
        Dictionary with extracted data
    """
    extracted = {
        "opinion": "",
        "vote": "approve",
        "assessments": [],
        "recommended_winner": 1,
    }

    # Try to find vote
    vote_match = re.search(r'(?:vote|decision):\s*["\']?(\w+)', text, re.IGNORECASE)
    if vote_match:
        vote = vote_match.group(1).lower()
        if "dissent" in vote:
            extracted["vote"] = "dissent"
        elif "reservation" in vote or "reserve" in vote:
            extracted["vote"] = "approve_with_reservations"
        else:
            extracted["vote"] = "approve"

    # Try to find recommended winner
    winner_match = re.search(r"(?:winner|best|recommended).*?(\d+)", text, re.IGNORECASE)
    if winner_match:
        try:
            extracted["recommended_winner"] = int(winner_match.group(1))
        except ValueError:
            pass

    # Extract opinion (first substantial paragraph)
    paragraphs = text.split("\n\n")
    for para in paragraphs:
        if len(para) > 50 and not para.strip().startswith("{"):
            extracted["opinion"] = para[:500]
            break

    # Try to extract scores
    score_pattern = r'["\']?(\w+)["\']?\s*:\s*(\d+\.?\d*)'
    scores = {}
    for match in re.finditer(score_pattern, text):
        key = match.group(1).lower()
        try:
            value = float(match.group(2))
            if key in [
                "accuracy",
                "factual_consistency",
                "unique_insights",
                "error_detection",
                "sonotheia_relevance",
            ]:
                scores[key] = value
        except ValueError:
            continue

    if scores:
        extracted["assessments"] = [
            {
                "response_id": extracted["recommended_winner"],
                "scores": scores,
            }
        ]

    return extracted


def _create_fallback_synthesis(
    assessments: List[ResponseAssessment], question: str, responses: List[LLMResponse]
) -> SynthesizedResponse:
    """
    Create a fallback synthesis when rate limits prevent full synthesis.

    Args:
        assessments: Individual response assessments
        question: Original question
        responses: Original LLM responses

    Returns:
        SynthesizedResponse with fallback content
    """
    if not assessments:
        return SynthesizedResponse(
            combined_best="Unable to generate synthesis due to rate limits.",
            refined_final="Unable to generate synthesis due to rate limits.",
        )

    # Find the winner
    winner = max(assessments, key=lambda a: a.overall_score)
    winner_response = next((r for r in responses if r.id == winner.response_id), None)

    # Create simple synthesis from winner and top strengths
    top_strengths = winner.strengths[:3] if winner.strengths else []
    strengths_text = "\n".join(f"- {s}" for s in top_strengths) if top_strengths else ""

    combined = f"""Based on the council's review, Response #{winner.response_id} received the highest score ({winner.overall_score}/10).

Key strengths:
{strengths_text if strengths_text else "See individual assessments for details."}

{winner_response.content[:500] if winner_response else "See individual assessments for the winning response."}"""

    refined = f"""After comprehensive review by the council, Response #{winner.response_id} has been identified as the strongest answer to: "{question}"

The response scored {winner.overall_score}/10 overall, excelling in multiple evaluation criteria. See individual assessments for detailed analysis."""

    return SynthesizedResponse(combined_best=combined, refined_final=refined)


def _validate_review_request(request: ReviewRequest) -> None:
    """Validate the review request and raise helpful errors."""
    # Validate question
    if not request.question or not request.question.strip():
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty. Please provide a question to review responses for.",
        )

    # Validate responses
    if not request.responses:
        raise HTTPException(status_code=400, detail="At least 2 responses are required for review.")

    if len(request.responses) < 2:
        raise HTTPException(
            status_code=400,
            detail=f"At least 2 responses required, but only {len(request.responses)} provided.",
        )

    if len(request.responses) > 5:
        raise HTTPException(
            status_code=400,
            detail=f"Maximum 5 responses allowed, but {len(request.responses)} provided.",
        )

    # Validate response IDs are unique
    response_ids = [r.id for r in request.responses]
    if len(response_ids) != len(set(response_ids)):
        raise HTTPException(
            status_code=400, detail="Response IDs must be unique. Found duplicate IDs."
        )

    # Validate response content
    for r in request.responses:
        if not r.content or not r.content.strip():
            raise HTTPException(
                status_code=400,
                detail=f"Response #{r.id} has empty content. All responses must have content.",
            )

    # Validate justices
    if not request.justices:
        raise HTTPException(status_code=400, detail="At least one justice is required for review.")

    # Validate chair and vice_chair are in justices list
    if request.chair not in request.justices:
        raise HTTPException(
            status_code=400,
            detail=f"Chair '{request.chair}' must be included in the justices list.",
        )

    if request.vice_chair not in request.justices:
        raise HTTPException(
            status_code=400,
            detail=f"Vice chair '{request.vice_chair}' must be included in the justices list.",
        )

    if request.chair == request.vice_chair:
        raise HTTPException(
            status_code=400, detail="Chair and vice chair must be different personas."
        )

    # Validate persona IDs exist
    available_personas = {p.id for p in list_personas()}
    invalid_justices = [j for j in request.justices if j not in available_personas]
    if invalid_justices:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid justice IDs: {', '.join(invalid_justices)}. Available personas: {', '.join(sorted(available_personas)[:10])}...",
        )

    if request.chair not in available_personas:
        raise HTTPException(
            status_code=400,
            detail=f"Chair persona '{request.chair}' not found. Available: {', '.join(sorted(available_personas)[:10])}...",
        )

    if request.vice_chair not in available_personas:
        raise HTTPException(
            status_code=400,
            detail=f"Vice chair persona '{request.vice_chair}' not found. Available: {', '.join(sorted(available_personas)[:10])}...",
        )


def _build_review_council(request: ReviewRequest) -> Council:
    """Build a council configured for response review."""
    try:
        config = ConfigManager().config
        provider = request.provider or config.api.provider
        model = request.model or config.api.model
        base_url = request.base_url or config.api.base_url
        api_key = request.api_key or get_api_key(provider)

        if not api_key:
            raise HTTPException(
                status_code=400,
                detail="API key is required for review. Set it via environment variable, config file, or request parameter.",
            )

        try:
            council_config = CouncilConfig(
                temperature=request.temperature,
                max_tokens_per_response=request.max_tokens,
            )
        except Exception as e:
            raise HTTPException(
                status_code=400, detail=f"Invalid council configuration: {str(e)}"
            ) from e

        try:
            council = Council(
                api_key=api_key,
                provider=provider,
                model=model,
                base_url=base_url,
                config=council_config,
            )
        except ValueError as e:
            raise HTTPException(
                status_code=400, detail=f"Failed to create council: {str(e)}"
            ) from e
        except Exception as e:
            logger.error(f"Unexpected error creating council: {e}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail="Failed to initialize council. Please check your API key and provider configuration.",
            ) from e

        # Add justices with appropriate weights
        justices_to_add = list(request.justices)
        added_justices = []

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
                added_justices.append(justice_id)
            except ValueError as e:
                logger.warning(f"Could not add justice {justice_id}: {e}")
                # Don't fail completely, but warn if critical justices are missing
                if justice_id in [request.chair, request.vice_chair]:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Failed to add {justice_id} ({'chair' if justice_id == request.chair else 'vice chair'}): {str(e)}",
                    )

        if not added_justices:
            raise HTTPException(
                status_code=400,
                detail="No justices could be added to the council. Please check that the persona IDs are valid.",
            )

        logger.info(
            f"Built review council with {len(added_justices)} justices: {', '.join(added_justices)}"
        )
        return council

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error building council: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Failed to build review council: {str(e)}"
        ) from e


def _format_responses_for_prompt(responses: List[LLMResponse]) -> str:
    """Format LLM responses into a text block for prompts."""
    return "\n\n".join(
        [
            f"=== RESPONSE #{r.id} {'(from ' + r.source + ')' if r.source else ''} ===\n{r.content}"
            for r in responses
        ]
    )


def _build_review_prompt(request: ReviewRequest) -> str:
    """Build the prompt for the review consultation."""
    responses_text = _format_responses_for_prompt(request.responses)

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

Apply your unique expertise and perspective to this review.

Provide your response ONLY as valid JSON matching the format above."""

    return prompt


def _build_synthesis_prompt(request: ReviewRequest, assessments: List[Dict]) -> str:
    """Build the prompt for synthesizing the best response."""
    # Build text block with scores for the synthesizer
    responses_text = "\n\n".join(
        [
            f"=== RESPONSE #{r.id} (Score: {next((a['overall_score'] for a in assessments if a.get('response_id') == r.id), 'N/A')}) ===\n{r.content}"
            for r in request.responses
        ]
    )

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


def _parse_google_docs_content(content: str) -> tuple[Optional[str], List[Dict[str, str]]]:
    """
    Parse Google Docs content to extract question and responses.

    Supports multiple formats:
    1. Structured: "Question: ... Response 1: ... Response 2: ..."
    2. Markers: "## Question\n...\n## Response 1\n..."
    3. Numbered: "1. Question: ...\n2. Response 1: ..."
    4. Auto-detect: Find question-like text and response-like sections

    Args:
        content: Raw text content from Google Docs

    Returns:
        Tuple of (question, list of responses with id and content)
    """
    if not content or not content.strip():
        return None, []

    # Clean up content
    content = content.strip()

    # Try structured format with explicit markers
    question_match = re.search(
        r"(?:^|\n)(?:##\s*)?(?:Question|QUESTION|Original Question):\s*(.+?)(?=\n(?:##\s*)?(?:Response|RESPONSE|Answer|ANSWER)|$)",
        content,
        re.IGNORECASE | re.DOTALL,
    )

    if question_match:
        question = question_match.group(1).strip()
        # Extract responses after the question
        remaining = content[question_match.end() :].strip()
    else:
        # Try to find question in first paragraph or section
        lines = content.split("\n")
        # First substantial paragraph might be the question
        question = None
        for i, line in enumerate(lines[:10]):  # Check first 10 lines
            line = line.strip()
            if len(line) > 20 and "?" in line:
                question = line
                remaining = "\n".join(lines[i + 1 :])
                break

        if not question:
            # Use first paragraph as question
            first_para = content.split("\n\n")[0] if "\n\n" in content else content.split("\n")[0]
            if len(first_para) > 10:
                question = first_para.strip()
                remaining = content[len(first_para) :].strip()
            else:
                return None, []

    # Extract responses
    responses = []

    # Try multiple patterns to find responses
    response_patterns = [
        # Pattern 1: "Response 1:", "Response #1:", "Answer 1:", etc.
        r"(?:^|\n)(?:##\s*)?(?:Response|RESPONSE|Answer|ANSWER)\s*#?(\d+)[:\-]\s*(.+?)(?=\n(?:##\s*)?(?:Response|RESPONSE|Answer|ANSWER)\s*#?\d+|$)",
        # Pattern 2: Numbered list "1. ...", "2. ..."
        r"(?:^|\n)(\d+)\.\s+(.+?)(?=\n\d+\.|$)",
        # Pattern 3: Section headers "=== Response 1 ==="
        r"===?\s*(?:Response|RESPONSE|Answer|ANSWER)\s*#?(\d+)\s*===?\s*\n(.+?)(?=\n===?\s*(?:Response|RESPONSE|Answer|ANSWER)|$)",
    ]

    for pattern in response_patterns:
        matches = re.finditer(pattern, remaining, re.IGNORECASE | re.DOTALL | re.MULTILINE)
        found_responses = []
        for match in matches:
            if len(match.groups()) == 2:
                resp_id = match.group(1)
                resp_content = match.group(2).strip()
            else:
                resp_id = str(len(found_responses) + 1)
                resp_content = match.group(0).strip()

            if resp_content and len(resp_content) > 10:
                found_responses.append(
                    {
                        "id": int(resp_id) if resp_id.isdigit() else len(found_responses) + 1,
                        "content": resp_content,
                    }
                )

        if len(found_responses) >= 2:
            responses = found_responses
            break

    # If no structured responses found, try to split by double newlines or sections
    if not responses:
        # Split by double newlines and treat each as a potential response
        sections = [s.strip() for s in remaining.split("\n\n") if s.strip()]
        # Filter out very short sections and question-like sections
        potential_responses = [
            s
            for s in sections
            if len(s) > 50 and not s.lower().startswith(("question", "original"))
        ]

        if len(potential_responses) >= 2:
            responses = [
                {"id": i + 1, "content": resp}
                for i, resp in enumerate(potential_responses[:5])  # Max 5 responses
            ]

    # Clean up question
    if question:
        # Remove markdown headers if present
        question = re.sub(r"^#+\s*", "", question)
        question = question.strip()

    return question, responses


async def _fetch_google_docs_content(url: str) -> Optional[str]:
    """
    Fetch content from Google Docs URL.

    Note: This requires Google API credentials. For now, we'll return None
    and rely on exported content instead.

    Args:
        url: Google Docs URL

    Returns:
        Document content or None if not available
    """
    # Extract document ID from URL
    doc_id_match = re.search(r"/document/d/([a-zA-Z0-9-_]+)", url)
    if not doc_id_match:
        return None

    doc_id = doc_id_match.group(1)

    # Try to use Google Docs API if credentials are available
    try:
        from googleapiclient.discovery import build

        # Check for credentials
        creds_path = os.path.expanduser("~/.config/council-ai/google_credentials.json")
        if not os.path.exists(creds_path):
            # Try environment variable for API key (read-only access)
            api_key = os.environ.get("GOOGLE_API_KEY")
            if api_key:
                try:
                    service = build("docs", "v1", developerKey=api_key)
                    doc = service.documents().get(documentId=doc_id).execute()
                    # Extract text content
                    content = []
                    for element in doc.get("body", {}).get("content", []):
                        if "paragraph" in element:
                            para = element["paragraph"]
                            for text_elem in para.get("elements", []):
                                if "textRun" in text_elem:
                                    content.append(text_elem["textRun"]["content"])
                    return "\n".join(content)
                except Exception as e:
                    logger.warning(f"Failed to fetch Google Doc via API: {e}")
                    return None
            return None
    except ImportError:
        logger.debug("Google API client not installed, skipping API fetch")
        return None
    except Exception as e:
        logger.warning(f"Error fetching Google Doc: {e}")
        return None

    return None


@router.post("/import/googledocs", response_model=GoogleDocsImportResponse)
async def import_google_docs(request: GoogleDocsImportRequest) -> GoogleDocsImportResponse:
    """
    Import question and responses from Google Docs.

    Supports:
    - Google Docs URL (requires GOOGLE_API_KEY environment variable)
    - Exported text/HTML content (paste or upload)
    """
    content = None

    # Try to fetch from URL if provided
    if request.url:
        content = await _fetch_google_docs_content(request.url)
        if not content:
            return GoogleDocsImportResponse(
                question="",
                responses=[],
                success=False,
                message="Could not fetch Google Doc. Please export the content and paste it, or set GOOGLE_API_KEY environment variable.",
            )

    # Use provided content if available
    if request.content:
        content = request.content

    if not content:
        return GoogleDocsImportResponse(
            question="",
            responses=[],
            success=False,
            message="No content provided. Please provide either a Google Docs URL or exported content.",
        )

    # Parse content
    question, responses_data = _parse_google_docs_content(content)

    if not question:
        return GoogleDocsImportResponse(
            question="",
            responses=[],
            success=False,
            message="Could not extract question from document. Please ensure the document has a clear question section.",
        )

    if len(responses_data) < 2:
        return GoogleDocsImportResponse(
            question=question,
            responses=[],
            success=False,
            message=f"Found only {len(responses_data)} response(s). Need at least 2 responses for review.",
        )

    # Convert to LLMResponse objects
    responses = [
        LLMResponse(
            id=resp["id"],
            content=resp["content"],
            source=None,  # Could be extracted from content if marked
        )
        for resp in responses_data[:5]  # Max 5 responses
    ]

    return GoogleDocsImportResponse(
        question=question,
        responses=responses,
        success=True,
        message=f"Successfully imported {len(responses)} responses.",
    )


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
            {
                "id": "accuracy",
                "name": "Accuracy",
                "description": "Is the information correct and precise?",
            },
            {
                "id": "factual_consistency",
                "name": "Factual Consistency",
                "description": "Does it align with established facts?",
            },
            {
                "id": "unique_insights",
                "name": "Unique Insights",
                "description": "Does it offer valuable unique perspectives?",
            },
            {
                "id": "error_detection",
                "name": "Error Detection",
                "description": "Are there errors or hallucinations?",
            },
            {
                "id": "sonotheia_relevance",
                "name": "Sonotheia Relevance",
                "description": "Relevance to deepfake audio defense",
            },
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
    # Validate request early
    try:
        _validate_review_request(request)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Validation error: {e}", exc_info=True)
        raise HTTPException(status_code=400, detail=f"Request validation failed: {str(e)}") from e

    # Build council with error handling
    try:
        council = _build_review_council(request)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to build council: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Failed to initialize review council: {str(e)}"
        ) from e

    try:
        review_prompt = _build_review_prompt(request)
    except Exception as e:
        logger.error(f"Failed to build review prompt: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Failed to prepare review prompt: {str(e)}"
        ) from e

    # Estimate token usage and warn if high
    estimated_tokens = _estimate_tokens(review_prompt)
    estimated_tokens += sum(_estimate_tokens(r.content) for r in request.responses)
    estimated_tokens += len(request.justices) * 500  # Rough estimate per justice response

    warnings = []
    if estimated_tokens > 8000:
        warnings.append(
            f"Estimated token usage ({estimated_tokens:,}) is high. "
            "Consider reducing the number of justices or shortening responses to avoid rate limits."
        )
        logger.warning(f"High token usage estimated: {estimated_tokens:,} tokens")

    try:
        # Get individual justice assessments with retry logic
        logger.info(f"Starting review consultation for {len(request.responses)} responses")

        async def _consult_with_retry():
            return await council.consult_async(
                review_prompt,
                mode=ConsultationMode.SYNTHESIS,
            )

        result = await _retry_with_backoff(
            _consult_with_retry,
            max_retries=3,
            base_delay=1.0,
        )

        if not result:
            raise HTTPException(
                status_code=500, detail="Council consultation returned no result. Please try again."
            )

        if not result.responses:
            raise HTTPException(
                status_code=500,
                detail="Council consultation completed but no justice responses were received. Please check your API configuration.",
            )

        # Parse individual responses
        justice_opinions = []

        for response in result.responses:
            try:
                # Validate response has required attributes
                if not hasattr(response, "persona") or not response.persona:
                    logger.error(f"Response missing persona attribute: {response}")
                    continue

                if not hasattr(response, "content"):
                    logger.warning(
                        f"Response from {response.persona.id if hasattr(response, 'persona') else 'unknown'} has no content"
                    )
                    continue

                # Use robust JSON extraction
                content = response.content or ""
                parsed, parse_error = _extract_and_parse_json(content)

                if parsed is None:
                    # JSON parsing failed, create fallback opinion
                    persona_id = response.persona.id
                    logger.warning(f"Could not parse JSON from {persona_id}: {parse_error}")
                    warnings.append(
                        f"Could not parse structured response from {response.persona.name}"
                    )

                    # Try to extract key information from text using regex
                    extracted_data = _extract_data_from_text(content)

                    role = "associate"
                    if persona_id == request.chair:
                        role = "chair"
                    elif persona_id == request.vice_chair:
                        role = "vice_chair"

                    justice_opinions.append(
                        {
                            "justice_id": persona_id,
                            "justice_name": response.persona.name,
                            "justice_emoji": response.persona.emoji or "👤",
                            "role": role,
                            "opinion": extracted_data.get("opinion")
                            or (content[:500] + "..." if len(content) > 500 else content),
                            "vote": extracted_data.get("vote", "approve"),
                            "assessments": extracted_data.get("assessments", []),
                            "recommended_winner": extracted_data.get("recommended_winner", 1),
                        }
                    )
                    continue

                # Successfully parsed JSON
                # Determine role
                persona_id = response.persona.id
                role = "associate"
                if persona_id == request.chair:
                    role = "chair"
                elif persona_id == request.vice_chair:
                    role = "vice_chair"

                justice_opinions.append(
                    {
                        "justice_id": persona_id,
                        "justice_name": response.persona.name,
                        "justice_emoji": response.persona.emoji or "👤",
                        "role": role,
                        "opinion": parsed.get("opinion", ""),
                        "vote": parsed.get("vote", "approve"),
                        "assessments": parsed.get("response_assessments", []),
                        "recommended_winner": parsed.get("recommended_winner", 1),
                    }
                )

            except (KeyError, AttributeError) as e:
                try:
                    persona_id = (
                        response.persona.id
                        if hasattr(response, "persona") and response.persona
                        else "unknown"
                    )
                    logger.warning(f"Error processing response from {persona_id}: {e}")
                    warnings.append(
                        f"Error processing response from {response.persona.name if hasattr(response, 'persona') and response.persona else 'unknown'}"
                    )

                    # Create a basic opinion from non-JSON response
                    role = "associate"
                    if hasattr(response, "persona") and response.persona:
                        if persona_id == request.chair:
                            role = "chair"
                        elif persona_id == request.vice_chair:
                            role = "vice_chair"

                    justice_opinions.append(
                        {
                            "justice_id": persona_id,
                            "justice_name": (
                                response.persona.name
                                if hasattr(response, "persona") and response.persona
                                else "Unknown"
                            ),
                            "justice_emoji": (
                                response.persona.emoji
                                if hasattr(response, "persona") and response.persona
                                else "👤"
                            ),
                            "role": role,
                            "opinion": (
                                (response.content[:500] + "...")
                                if hasattr(response, "content") and len(response.content) > 500
                                else (
                                    response.content
                                    if hasattr(response, "content")
                                    else "No response content available"
                                )
                            ),
                            "vote": "approve",
                            "assessments": [],
                            "recommended_winner": 1,
                        }
                    )
                except Exception as inner_e:
                    logger.error(f"Failed to create fallback opinion: {inner_e}", exc_info=True)
                    # Skip this response if we can't even create a fallback
                    continue

        # Aggregate scores across justices
        response_scores = {
            r.id: {"scores": {}, "opinions": [], "strengths": [], "weaknesses": []}
            for r in request.responses
        }

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
            for criterion in [
                "accuracy",
                "factual_consistency",
                "unique_insights",
                "error_detection",
                "sonotheia_relevance",
            ]:
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
                justifications={
                    k: f"Average score from {len(scores_data.get('scores', {}).get(k, []))} justices"
                    for k in avg_scores
                },
                strengths=list(set(scores_data.get("strengths", [])))[:5],
                weaknesses=list(set(scores_data.get("weaknesses", [])))[:5],
                justice_opinions=response_justice_opinions,
            )
            individual_assessments.append(assessment)

        # Sort by overall score to get ranking
        sorted_assessments = sorted(
            individual_assessments, key=lambda a: a.overall_score, reverse=True
        )
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
                dissenting_opinions.append(
                    f"{op['justice_emoji']} {op['justice_name']}: {op['opinion'][:200]}..."
                )

        group_decision = GroupDecision(
            ranking=ranking,
            winner=winner,
            winner_score=winner_score,
            majority_opinion=result.synthesis or "The council has reached a consensus.",
            dissenting_opinions=dissenting_opinions,
            vote_breakdown=vote_breakdown,
        )

        # Generate synthesized response with retry and graceful degradation
        synthesized = SynthesizedResponse(
            combined_best="",
            refined_final="",
        )
        partial_results = False

        try:
            synthesis_prompt = _build_synthesis_prompt(
                request, [a.model_dump() for a in individual_assessments]
            )

            # Try synthesis with retry logic
            try:

                async def _synthesize_with_retry():
                    return await council.consult_async(
                        synthesis_prompt,
                        mode=ConsultationMode.SYNTHESIS,
                    )

                synthesis_result = await _retry_with_backoff(
                    _synthesize_with_retry,
                    max_retries=3,
                    base_delay=1.0,
                )
            except Exception as retry_error:
                # Check if it's a rate limit error after retries
                error_info = _parse_anthropic_error(retry_error)
                if error_info["type"] == "rate_limit":
                    logger.warning(
                        f"Synthesis failed due to rate limit after retries: {retry_error}"
                    )
                    warnings.append(
                        f"Synthesis generation skipped due to rate limits. "
                        f"{error_info.get('suggestion', 'Please try again later.')}"
                    )
                    partial_results = True
                    # Use fallback synthesis
                    synthesized = _create_fallback_synthesis(
                        individual_assessments, request.question, request.responses
                    )
                else:
                    # Other error, still use fallback
                    logger.warning(f"Synthesis generation failed: {retry_error}")
                    warnings.append("Synthesis generation failed, using fallback synthesis.")
                    partial_results = True
                    synthesized = _create_fallback_synthesis(
                        individual_assessments, request.question, request.responses
                    )
                synthesis_result = None

            # Parse synthesis if we got a result
            if synthesis_result and synthesis_result.synthesis:
                try:
                    content = synthesis_result.synthesis
                    parsed, parse_error = _extract_and_parse_json(content)

                    if parsed:
                        synthesized = SynthesizedResponse(
                            combined_best=parsed.get("combined_best", synthesis_result.synthesis),
                            refined_final=parsed.get("refined_final", synthesis_result.synthesis),
                        )
                    else:
                        # JSON parsing failed, use synthesis as-is
                        logger.warning(f"Failed to parse synthesis JSON: {parse_error}")
                        synthesized = SynthesizedResponse(
                            combined_best=synthesis_result.synthesis,
                            refined_final=synthesis_result.synthesis,
                        )
                except Exception as e:
                    logger.warning(f"Failed to parse synthesis: {e}")
                    synthesized = SynthesizedResponse(
                        combined_best=synthesis_result.synthesis or "Synthesis unavailable",
                        refined_final=synthesis_result.synthesis or "Synthesis unavailable",
                    )
            elif synthesis_result is None:
                # Already handled above with fallback
                pass
            else:
                logger.warning("Synthesis result was empty, using fallback")
                warnings.append("Synthesis result was empty, using fallback synthesis.")
                partial_results = True
                synthesized = _create_fallback_synthesis(
                    individual_assessments, request.question, request.responses
                )

        except Exception as e:
            logger.error(f"Unexpected error in synthesis generation: {e}", exc_info=True)
            # Don't fail the whole request if synthesis fails
            warnings.append(f"Synthesis generation encountered an error: {str(e)[:100]}")
            partial_results = True
            synthesized = _create_fallback_synthesis(
                individual_assessments, request.question, request.responses
            )

        # Build council composition info
        council_composition = {
            "chair": {
                "id": request.chair,
                "name": next(
                    (p.name for p in list_personas() if p.id == request.chair), request.chair
                ),
            },
            "vice_chair": {
                "id": request.vice_chair,
                "name": next(
                    (p.name for p in list_personas() if p.id == request.vice_chair),
                    request.vice_chair,
                ),
            },
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
            partial_results=partial_results,
            warnings=warnings,
        )

    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except ValueError as e:
        logger.error(f"Validation error in review: {e}", exc_info=True)
        raise HTTPException(status_code=400, detail=f"Invalid request: {str(e)}") from e
    except TimeoutError as e:
        logger.error(f"Review timed out: {e}", exc_info=True)
        raise HTTPException(
            status_code=504,
            detail="Review request timed out. The council consultation took too long. Please try again with fewer responses or a simpler question.",
        ) from e
    except Exception as e:
        logger.error(f"Review failed with unexpected error: {e}", exc_info=True)
        # Parse error for better messaging
        error_info = _parse_anthropic_error(e)
        error_msg = str(e)

        if (
            error_info["type"] == "authentication"
            or "API key" in error_msg
            or "authentication" in error_msg.lower()
        ):
            raise HTTPException(
                status_code=401,
                detail=error_info.get("suggestion")
                or "API authentication failed. Please check your API key and provider configuration.",
            ) from e
        elif (
            error_info["type"] == "rate_limit"
            or "rate limit" in error_msg.lower()
            or "429" in error_msg
        ):
            suggestion = (
                error_info.get("suggestion")
                or "API rate limit exceeded. Please wait a moment and try again."
            )
            raise HTTPException(status_code=429, detail=suggestion) from e
        else:
            raise HTTPException(
                status_code=500,
                detail=f"Review failed: {error_msg}. Please check the logs for more details or try again.",
            ) from e


@router.post("/review/stream")
async def review_responses_stream(request: ReviewRequest) -> StreamingResponse:
    """Stream the review process as Server-Sent Events."""

    async def generate_stream():
        try:
            # Validate request early
            try:
                _validate_review_request(request)
            except HTTPException as e:
                yield f"data: {json.dumps({'type': 'error', 'error': e.detail, 'error_type': 'validation'})}\n\n"
                return
            except Exception as e:
                yield f"data: {json.dumps({'type': 'error', 'error': f'Validation failed: {str(e)}', 'error_type': 'validation'})}\n\n"
                return

            yield f"data: {json.dumps({'type': 'started', 'message': 'Review started...'})}\n\n"

            try:
                council = _build_review_council(request)
            except HTTPException as e:
                yield f"data: {json.dumps({'type': 'error', 'error': e.detail, 'error_type': 'council_setup'})}\n\n"
                return
            except Exception as e:
                logger.error(f"Failed to build council in stream: {e}", exc_info=True)
                yield f"data: {json.dumps({'type': 'error', 'error': f'Failed to initialize council: {str(e)}', 'error_type': 'council_setup'})}\n\n"
                return

            try:
                review_prompt = _build_review_prompt(request)
            except Exception as e:
                logger.error(f"Failed to build prompt in stream: {e}", exc_info=True)
                yield f"data: {json.dumps({'type': 'error', 'error': f'Failed to prepare review: {str(e)}', 'error_type': 'prompt_build'})}\n\n"
                return

            yield f"data: {json.dumps({'type': 'council_assembled', 'justices': len(request.justices)})}\n\n"

            # Stream individual assessments
            yield f"data: {json.dumps({'type': 'phase', 'phase': 'individual_review', 'message': 'Justices reviewing responses...'})}\n\n"

            try:
                async for update in council.consult_stream(
                    review_prompt,
                    mode=ConsultationMode.SYNTHESIS,
                ):
                    try:
                        if update.get("type") == "response_start":
                            yield f"data: {json.dumps({'type': 'justice_start', 'justice': update.get('persona_name', 'Unknown')})}\n\n"
                        elif update.get("type") == "response_complete":
                            yield f"data: {json.dumps({'type': 'justice_complete', 'justice': update.get('persona_name', 'Unknown')})}\n\n"
                        elif update.get("type") == "synthesis_start":
                            yield f"data: {json.dumps({'type': 'phase', 'phase': 'synthesis', 'message': 'Synthesizing group decision...'})}\n\n"
                    except Exception as e:
                        logger.warning(f"Error processing stream update: {e}")
                        # Continue streaming even if one update fails

                # Final result (call non-streaming for complete result)
                try:
                    result = await review_responses(request)
                    yield f"data: {json.dumps({'type': 'complete', 'result': result.model_dump()})}\n\n"
                except HTTPException as e:
                    yield f"data: {json.dumps({'type': 'error', 'error': e.detail, 'error_type': 'review_failed', 'status_code': e.status_code})}\n\n"
                except Exception as e:
                    logger.error(f"Failed to get final result in stream: {e}", exc_info=True)
                    yield f"data: {json.dumps({'type': 'error', 'error': f'Failed to complete review: {str(e)}', 'error_type': 'review_failed'})}\n\n"

            except TimeoutError as e:
                logger.error(f"Stream timed out: {e}", exc_info=True)
                yield f"data: {json.dumps({'type': 'error', 'error': 'Review timed out. Please try again.', 'error_type': 'timeout'})}\n\n"
            except Exception as e:
                logger.error(f"Stream error: {e}", exc_info=True)
                yield f"data: {json.dumps({'type': 'error', 'error': str(e), 'error_type': 'stream_error'})}\n\n"

        except Exception as e:
            logger.error(f"Unexpected error in stream: {e}", exc_info=True)
            yield f"data: {json.dumps({'type': 'error', 'error': f'Unexpected error: {str(e)}', 'error_type': 'unexpected'})}\n\n"

    return StreamingResponse(
        generate_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
