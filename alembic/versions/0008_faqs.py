"""FAQs table."""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0008_faqs"
down_revision = "0007_email_otp"
branch_labels = None
depends_on = None

DEFAULT_FAQS = [
    (
        "What AI engineering services do you offer?",
        "I build GenAI products including RAG systems, LangChain/LangGraph agents, AI chatbots, FastAPI backends, and full-stack AI applications for startups and teams.",
        0,
    ),
    (
        "Are you available for AI engineer or software engineer jobs?",
        "Yes. I am open to full-time and freelance roles as an AI Engineer, GenAI Engineer, Backend Engineer, or Software Engineer focused on production AI systems.",
        1,
    ),
    (
        "Which technologies do you use for AI products?",
        "Python, LangChain, LangGraph, OpenAI, Gemini, FastAPI, React, PostgreSQL, Pinecone/Qdrant/Weaviate, Docker, and cloud platforms like Azure, Render, and Vercel.",
        2,
    ),
    (
        "How can I hire you for an AI project?",
        "Use the Hire Me or Book service options on this site, or reach out via email or LinkedIn. Typical work includes RAG setups, custom agents, and AI product MVPs.",
        3,
    ),
]


def upgrade():
    op.create_table(
        "faqs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("question", sa.Text(), nullable=False),
        sa.Column("answer", sa.Text(), nullable=False),
        sa.Column("display_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_faqs_display_order", "faqs", ["display_order"])
    op.create_index("ix_faqs_is_active", "faqs", ["is_active"])

    faqs = sa.table(
        "faqs",
        sa.column("id", postgresql.UUID(as_uuid=True)),
        sa.column("question", sa.Text()),
        sa.column("answer", sa.Text()),
        sa.column("display_order", sa.Integer()),
        sa.column("is_active", sa.Boolean()),
    )
    import uuid

    op.bulk_insert(
        faqs,
        [
            {
                "id": str(uuid.uuid4()),
                "question": q,
                "answer": a,
                "display_order": order,
                "is_active": True,
            }
            for q, a, order in DEFAULT_FAQS
        ],
    )


def downgrade():
    op.drop_index("ix_faqs_is_active", table_name="faqs")
    op.drop_index("ix_faqs_display_order", table_name="faqs")
    op.drop_table("faqs")
