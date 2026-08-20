from uuid import UUID
from pydantic import BaseModel, Field, model_validator


class ConversationTurn(BaseModel):
    role: str = Field(pattern="^(user|assistant)$")
    content: str = Field(min_length=1, max_length=8000)


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)
    conversation: list[ConversationTurn] = Field(default_factory=list)


class ChatSource(BaseModel):
    document_id: UUID
    filename: str
    snippet: str


class ChatResponseData(BaseModel):
    response: str
    sources: list[ChatSource] = Field(default_factory=list)


class QuickActionOut(BaseModel):
    label: str
    icon: str
    message: str


class LlmModelOption(BaseModel):
    id: str
    label: str


class LlmProviderOption(BaseModel):
    id: str
    label: str
    configured: bool
    models: list[LlmModelOption] = Field(default_factory=list)


class ChatbotConfigOut(BaseModel):
    bot_name: str
    bot_subtitle: str
    avatar_url: str | None = None
    welcome_message: str
    privacy_policy_url: str
    privacy_policy_label: str
    quick_actions: list[QuickActionOut] = Field(default_factory=list)
    # Admin-only LLM fields (safe defaults on public too)
    llm_provider: str = "openai"
    llm_model: str = "gpt-4o-mini"
    llm_temperature: float = 0.2
    llm_providers: list[LlmProviderOption] = Field(default_factory=list)
    embedding_provider: str = "hash"
    mistral_embed_configured: bool = False
    pinecone_configured: bool = False
    chunk_size: int = 800
    chunk_overlap: int = 120


class ChatbotConfigUpdate(BaseModel):
    bot_name: str = Field(min_length=1, max_length=120)
    bot_subtitle: str = Field(min_length=1, max_length=200)
    avatar_url: str | None = None
    welcome_message: str = Field(min_length=1, max_length=4000)
    privacy_policy_url: str = Field(min_length=1, max_length=500)
    privacy_policy_label: str = Field(min_length=1, max_length=200)
    quick_actions: list[QuickActionOut] = Field(default_factory=list)
    llm_provider: str = Field(default="openai", min_length=2, max_length=40)
    llm_model: str = Field(default="gpt-4o-mini", min_length=2, max_length=120)
    llm_temperature: float = Field(default=0.2, ge=0, le=2)
    chunk_size: int = Field(default=800, ge=100, le=4000)
    chunk_overlap: int = Field(default=120, ge=0, le=2000)

    @model_validator(mode="after")
    def validate_chunk_overlap(self):
        if self.chunk_overlap >= self.chunk_size:
            raise ValueError("chunk_overlap must be smaller than chunk_size")
        return self


class ChatDocumentOut(BaseModel):
    id: UUID
    original_filename: str
    file_size: int
    page_count: int
    status: str
    error_message: str | None = None
    chunk_count: int
    created_at: str

    model_config = {"from_attributes": True}
