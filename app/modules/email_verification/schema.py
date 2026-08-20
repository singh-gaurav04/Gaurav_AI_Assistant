from pydantic import BaseModel, Field


class SendOtpRequest(BaseModel):
    email: str = Field(min_length=3, max_length=320, pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
    purpose: str = Field(pattern=r"^(contact|booking)$")


class VerifyOtpRequest(BaseModel):
    email: str = Field(min_length=3, max_length=320, pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
    purpose: str = Field(pattern=r"^(contact|booking)$")
    otp: str = Field(min_length=4, max_length=8, pattern=r"^\d+$")
