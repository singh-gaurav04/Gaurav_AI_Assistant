from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field

class ExperienceCreate(BaseModel):
    title: str = Field(min_length=1, max_length=180)
    company: str = Field(min_length=1, max_length=180)
    location: str | None = Field(default=None, max_length=160)
    period: str = Field(min_length=1, max_length=80)
    type: str = Field(default="Experience", max_length=80)
    description: str = Field(min_length=1, max_length=8000)
    achievements: list[str] = Field(default_factory=list)
    technologies: list[str] = Field(default_factory=list)
    link: str | None = Field(default=None, max_length=500)
    display_order: int = 0
    is_published: bool = True

class ExperienceUpdate(ExperienceCreate):
    pass

class ExperienceOut(ExperienceCreate):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
