"""chatbot knowledge base tables"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0003_chatbot_rag"
down_revision = "0002_portfolio_cms"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "chat_documents",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("original_filename", sa.String(500), nullable=False),
        sa.Column("stored_filename", sa.String(500), nullable=False),
        sa.Column("file_path", sa.String(1000), nullable=False),
        sa.Column("file_size", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("page_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("status", sa.String(32), nullable=False, server_default="processing"),
        sa.Column("error_message", sa.Text()),
        sa.Column("chunk_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "chat_chunks",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("document_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("chat_documents.id", ondelete="CASCADE"), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("embedding", postgresql.JSONB()),
        sa.Column("chunk_index", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("char_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_chat_chunks_document_id", "chat_chunks", ["document_id"])

    op.create_table(
        "chatbot_settings",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("bot_name", sa.String(120), nullable=False, server_default="Winston"),
        sa.Column("bot_subtitle", sa.String(200), nullable=False, server_default="EDI Expert"),
        sa.Column("avatar_url", sa.String(1000)),
        sa.Column(
            "welcome_message",
            sa.Text(),
            nullable=False,
            server_default=(
                "Welcome back! I'm Winston, an EDI Expert at Orderful. Looking to streamline your "
                "supply chain? Any questions I can answer for you?"
            ),
        ),
        sa.Column("privacy_policy_url", sa.String(500), nullable=False, server_default="#"),
        sa.Column("privacy_policy_label", sa.String(200), nullable=False, server_default="Orderful Privacy Policy"),
        sa.Column("quick_actions", postgresql.JSONB()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )


def downgrade():
    op.drop_table("chatbot_settings")
    op.drop_index("ix_chat_chunks_document_id", table_name="chat_chunks")
    op.drop_table("chat_chunks")
    op.drop_table("chat_documents")
