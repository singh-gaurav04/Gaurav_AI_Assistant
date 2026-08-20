from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

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


async def ensure_faq_schema(db: AsyncSession) -> int:
    """Create faqs table if missing and seed defaults when empty. Returns seeded count."""
    await db.execute(
        text(
            """
            CREATE TABLE IF NOT EXISTS faqs (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                question TEXT NOT NULL,
                answer TEXT NOT NULL,
                display_order INTEGER NOT NULL DEFAULT 0,
                is_active BOOLEAN NOT NULL DEFAULT TRUE,
                created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
                updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
            );
            """
        )
    )
    await db.execute(text("CREATE INDEX IF NOT EXISTS ix_faqs_display_order ON faqs (display_order);"))
    await db.execute(text("CREATE INDEX IF NOT EXISTS ix_faqs_is_active ON faqs (is_active);"))
    await db.commit()

    count = await db.scalar(text("SELECT COUNT(*) FROM faqs"))
    if count and int(count) > 0:
        return 0

    seeded = 0
    for question, answer, order in DEFAULT_FAQS:
        await db.execute(
            text(
                """
                INSERT INTO faqs (id, question, answer, display_order, is_active)
                VALUES (gen_random_uuid(), :question, :answer, :display_order, TRUE)
                """
            ),
            {"question": question, "answer": answer, "display_order": order},
        )
        seeded += 1
    await db.commit()
    return seeded
