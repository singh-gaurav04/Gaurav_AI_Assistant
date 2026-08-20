from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field
from app.modules.contact.model import ContactStatus

class ContactCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    email: str = Field(min_length=3, max_length=320, pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
    subject: str = Field(min_length=3, max_length=200)
    message: str = Field(min_length=10, max_length=5000)
    website: str | None = Field(default=None, max_length=0)
    verification_token: str = Field(min_length=10, max_length=2048)

class ContactOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    name: str
    email: str
    subject: str
    message: str
    status: ContactStatus

class ContactAdminOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    name: str
    email: str
    subject: str
    message: str
    status: ContactStatus
    read_at: datetime | None
    replied_at: datetime | None
    created_at: datetime

class ContactReply(BaseModel):
    message: str = Field(min_length=1, max_length=8000)
