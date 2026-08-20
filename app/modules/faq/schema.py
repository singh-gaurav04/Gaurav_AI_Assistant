from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class FaqCreate(BaseModel):
    question: str = Field(min_length=1, max_length=2000)
    answer: str = Field(min_length=1, max_length=10000)
    display_order: int = 0
    is_active: bool = True


class FaqUpdate(FaqCreate):
    pass


class FaqOut(FaqCreate):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
