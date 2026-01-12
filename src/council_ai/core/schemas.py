"""
Structured Output Schemas for Consultation Results
"""

from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


class ActionItem(BaseModel):
    """An actionable item from a consultation."""

    description: str = Field(..., description="What needs to be done")
    priority: str = Field(default="medium", description="Priority: high, medium, low")
    owner: Optional[str] = Field(default=None, description="Who should do this")
    due_date: Optional[str] = Field(default=None, description="When this should be done")


class Recommendation(BaseModel):
    """A recommendation from the council."""

    title: str = Field(..., description="Short title of the recommendation")
    description: str = Field(..., description="Detailed description")
    confidence: str = Field(default="medium", description="Confidence level: high, medium, low")
    rationale: str = Field(..., description="Why this recommendation")


class ProsCons(BaseModel):
    """Pros and cons analysis."""

    pros: List[str] = Field(default_factory=list, description="List of advantages/benefits")
    cons: List[str] = Field(default_factory=list, description="List of disadvantages/risks")
    net_assessment: str = Field(..., description="Overall assessment given pros and cons")


class SynthesisSchema(BaseModel):
    """Structured synthesis of council responses."""

    key_points_of_agreement: List[str] = Field(
        default_factory=list, description="Where advisors align"
    )
    key_points_of_tension: List[str] = Field(
        default_factory=list, description="Where advisors disagree or see different risks"
    )
    synthesized_recommendation: str = Field(..., description="The balanced path forward")
    action_items: List[ActionItem] = Field(default_factory=list, description="Concrete next steps")
    recommendations: List[Recommendation] = Field(
        default_factory=list, description="Specific recommendations"
    )
    pros_cons: Optional[ProsCons] = Field(
        default=None, description="Pros and cons analysis if applicable"
    )

    def to_json_schema(self) -> dict:
        """Generate JSON schema for this model."""
        return self.model_json_schema()
