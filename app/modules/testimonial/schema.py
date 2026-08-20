from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field, HttpUrl
from app.modules.testimonial.model import TestimonialStatus

class TestimonialUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    role: str | None = Field(default=None, max_length=150)
    linkedin_url: HttpUrl | None = None
    message: str | None = Field(default=None, min_length=5, max_length=5000)
    rating: int | None = Field(default=None, ge=1, le=5)
    is_featured: bool | None = None
    display_order: int | None = None

class TestimonialCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    role: str | None = Field(default=None, max_length=150)
    linkedin_url: str | None = Field(default=None, max_length=500)
    message: str = Field(min_length=5, max_length=5000)
    rating: int | None = Field(default=None, ge=1, le=5)
    is_featured: bool = False
    display_order: int = 0


class FeedbackCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    linkedin_url: str | None = Field(default=None, max_length=500)
    message: str = Field(min_length=5, max_length=5000)

class TestimonialOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    name: str
    role: str | None
    linkedin_url: str | None
    message: str
    avatar_url: str | None
    rating: int | None
    status: TestimonialStatus
    is_featured: bool
    display_order: int
