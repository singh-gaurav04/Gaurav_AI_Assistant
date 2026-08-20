from pydantic import BaseModel, Field

class VisitCreate(BaseModel):
    page: str = Field(min_length=1, max_length=1000)
    user_agent: str | None = Field(default=None, max_length=2000)
    referrer: str | None = Field(default=None, max_length=1000)
