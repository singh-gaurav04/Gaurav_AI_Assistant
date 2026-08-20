from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field

class CertificationCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    issuer: str = Field(min_length=1, max_length=160)
    date: str = Field(min_length=1, max_length=40)
    description: str | None = Field(default=None, max_length=4000)
    credential_id: str | None = Field(default=None, max_length=160)
    link: str | None = Field(default=None, max_length=500)
    icon: str | None = Field(default=None, max_length=32)
    display_order: int = 0
    is_published: bool = True

class CertificationUpdate(CertificationCreate):
    pass

class CertificationOut(CertificationCreate):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
