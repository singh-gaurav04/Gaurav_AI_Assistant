from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field

class ProfileUpdate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    title: str = Field(min_length=1, max_length=250)
    handle: str | None = Field(default=None, max_length=80)
    bio: str = Field(min_length=1, max_length=8000)
    location: str | None = Field(default=None, max_length=160)
    email: str = Field(min_length=3, max_length=320, pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
    phone: str | None = Field(default=None, max_length=40)
    graduation_year: str | None = Field(default=None, max_length=20)
    profile_image_url: str | None = Field(default=None, max_length=1000)
    resume_url: str | None = Field(default=None, max_length=1000)
    is_placed: bool = False
    placement_status: str | None = Field(default=None, max_length=200)
    placement_company: str | None = Field(default=None, max_length=160)
    placement_role: str | None = Field(default=None, max_length=160)
    github_url: str | None = Field(default=None, max_length=500)
    linkedin_url: str | None = Field(default=None, max_length=500)
    leetcode_url: str | None = Field(default=None, max_length=500)
    response_time: str | None = Field(default=None, max_length=200)

class ProfileOut(ProfileUpdate):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
