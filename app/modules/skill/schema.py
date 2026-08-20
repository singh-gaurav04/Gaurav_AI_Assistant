from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field

class SkillCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    category: str = Field(min_length=1, max_length=80)
    icon: str | None = Field(default=None, max_length=255)
    description: str | None = Field(default=None, max_length=2000)
    proficiency: int | None = Field(default=None, ge=0, le=100)
    display_order: int = 0
    is_active: bool = True

class SkillUpdate(SkillCreate):
    pass

class SkillOut(SkillCreate):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
