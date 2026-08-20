from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field

class EmailTemplateUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=120)
    subject: str | None = Field(default=None, max_length=250)
    html_body: str | None = None
    text_body: str | None = None
    variables: list[str] | None = None
    is_active: bool | None = None

class EmailTemplateOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    name: str
    slug: str
    subject: str
    html_body: str
    text_body: str | None
    variables: list[str]
    is_active: bool
