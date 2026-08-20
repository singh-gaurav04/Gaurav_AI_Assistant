from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field, HttpUrl

class ProjectCreate(BaseModel):
    title: str = Field(min_length=1, max_length=180)
    slug: str | None = Field(default=None, max_length=200)
    short_description: str = Field(min_length=1, max_length=500)
    description: str = Field(min_length=1, max_length=30000)
    github_url: HttpUrl | None = None
    live_url: HttpUrl | None = None
    featured_image_url: str | None = Field(default=None, max_length=1000)
    imagekit_file_id: str | None = Field(default=None, max_length=255)
    gallery_images: list[dict] = Field(default_factory=list)
    category: str = Field(min_length=1, max_length=100)
    technologies: list[str] = Field(default_factory=list, max_length=30)
    featured: bool = False
    is_published: bool = False
    is_real_project: bool = False
    display_order: int = 0

class ProjectUpdate(ProjectCreate):
    pass

class ProjectOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    title: str
    slug: str
    short_description: str
    description: str
    github_url: str | None
    live_url: str | None
    featured_image_url: str | None
    imagekit_file_id: str | None = None
    gallery_images: list[dict] = Field(default_factory=list)
    category: str
    technologies: list[str]
    featured: bool
    is_published: bool
    is_real_project: bool
    display_order: int
