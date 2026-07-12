from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, Field, model_validator

from app.models.interaction import InteractionSource, InteractionStatus, InteractionType, InterestLevel, Sentiment
from app.schemas.common import ORMBase


class InteractionBase(BaseModel):
    doctor_id: UUID
    user_id: UUID
    interaction_type: InteractionType
    interaction_date: datetime
    duration_minutes: int | None = Field(default=None, ge=0, le=1440)
    location: str | None = Field(default=None, max_length=200)
    purpose: str | None = Field(default=None, max_length=200)
    discussion_points: str | None = None
    products_discussed: list[str] = Field(default_factory=list)
    samples_distributed: bool = False
    sentiment: Sentiment | None = None
    follow_up_required: bool = False
    follow_up_actions: str | None = None
    follow_up_date: date | None = None
    attendees: str | None = None
    topics_discussed: str | None = None
    clinical_evidence: str | None = None
    questions_raised: str | None = None
    objections: str | None = None
    competitor_discussion: str | None = None
    promotional_materials: str | None = None
    brochures_shared: str | None = None
    interest_level: InterestLevel | None = None
    next_best_action: str | None = None
    ai_summary: str | None = None
    ai_suggestions: list[str] = Field(default_factory=list)
    missing_information: list[str] = Field(default_factory=list)
    confidence_score: float | None = Field(default=None, ge=0, le=1)
    source: InteractionSource = InteractionSource.MANUAL
    status: InteractionStatus = InteractionStatus.SUBMITTED

    @model_validator(mode="after")
    def validate_follow_up(self) -> "InteractionBase":
        if self.follow_up_required and not self.follow_up_date:
            raise ValueError("follow_up_date is required when follow_up_required is true")
        return self


class InteractionCreate(InteractionBase):
    pass


class InteractionUpdate(BaseModel):
    doctor_id: UUID | None = None
    interaction_type: InteractionType | None = None
    interaction_date: datetime | None = None
    duration_minutes: int | None = Field(default=None, ge=0, le=1440)
    location: str | None = Field(default=None, max_length=200)
    purpose: str | None = Field(default=None, max_length=200)
    discussion_points: str | None = None
    products_discussed: list[str] | None = None
    samples_distributed: bool | None = None
    sentiment: Sentiment | None = None
    follow_up_required: bool | None = None
    follow_up_actions: str | None = None
    follow_up_date: date | None = None
    attendees: str | None = None
    topics_discussed: str | None = None
    clinical_evidence: str | None = None
    questions_raised: str | None = None
    objections: str | None = None
    competitor_discussion: str | None = None
    promotional_materials: str | None = None
    brochures_shared: str | None = None
    interest_level: InterestLevel | None = None
    next_best_action: str | None = None
    ai_summary: str | None = None
    ai_suggestions: list[str] | None = None
    missing_information: list[str] | None = None
    confidence_score: float | None = Field(default=None, ge=0, le=1)
    status: InteractionStatus | None = None


class InteractionRead(InteractionBase, ORMBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
