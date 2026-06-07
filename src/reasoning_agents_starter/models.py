from pydantic import BaseModel, Field


class LearnerProfile(BaseModel):
    learner_id: str = Field(..., description="Synthetic learner identifier")
    role: str
    certification: str
    practice_score_avg: int = Field(ge=0, le=100)
    hours_studied: int = Field(ge=0)
    exam_outcome: str


class WorkSignal(BaseModel):
    employee_id: str
    meeting_hours_per_week: int = Field(ge=0)
    focus_hours_per_week: int = Field(ge=0)
    preferred_learning_slot: str
