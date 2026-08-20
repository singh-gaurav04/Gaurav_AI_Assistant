from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field


class ServiceCreate(BaseModel):
    title: str = Field(min_length=1, max_length=180)
    slug: str | None = Field(default=None, max_length=200)
    short_description: str = Field(min_length=1, max_length=500)
    description: str = Field(min_length=1, max_length=30000)
    features: list[str] = Field(default_factory=list, max_length=40)
    duration: list[str] = Field(default_factory=list, max_length=20)
    how_it_works: list[str] = Field(default_factory=list, max_length=20)
    deliverables: list[str] = Field(default_factory=list, max_length=20)
    tag: str | None = Field(default=None, max_length=80)
    recommended: bool = False
    featured_image_url: str | None = Field(default=None, max_length=1000)
    imagekit_file_id: str | None = Field(default=None, max_length=255)
    gallery_images: list[dict] = Field(default_factory=list)
    icon: str | None = Field(default=None, max_length=80)
    display_order: int = 0
    is_published: bool = True


class ServiceUpdate(ServiceCreate):
    pass


class ServiceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    slug: str
    short_description: str
    description: str
    features: list[str]
    duration: list[str]
    how_it_works: list[str]
    deliverables: list[str]
    tag: str | None
    recommended: bool
    featured_image_url: str | None
    imagekit_file_id: str | None = None
    gallery_images: list[dict] = Field(default_factory=list)
    icon: str | None
    display_order: int
    is_published: bool
