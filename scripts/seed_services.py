import asyncio
from app.core.database import SessionLocal
from app.modules.service.schema import ServiceCreate
from app.modules.service.service import service_service
from app.modules.service.repository import service_repository

DEFAULTS = [
    {
        "title": "AI Agent Development",
        "slug": "ai-agent-development",
        "short_description": "Reasoning agents, tool-using workflows and automations designed for real use cases.",
        "description": "I design and build AI agents that can plan, call tools, and execute multi-step workflows reliably. From internal ops automations to customer-facing copilots, the focus is on practical outcomes: clear prompts, guardrails, observability, and production-ready deployment.",
        "features": [
            "Tool-calling agents with structured outputs",
            "Workflow orchestration and human-in-the-loop steps",
            "Monitoring, logging, and safe failure handling",
        ],
        "duration": [
            "Discovery & scope: 1-3 days",
            "Architecture + build: 1-2 weeks",
            "Testing + iterations: 3-6 days",
            "Handoff + support window: 3-7 days",
        ],
        "how_it_works": [
            "Kickoff call to confirm goals, constraints, and success criteria",
            "Design phase: system flow, tools, prompts, and guardrails",
            "Build phase: integration + backend wiring + admin configuration",
            "Review & delivery: testing, documentation, and next-step roadmap",
        ],
        "deliverables": [
            "Agent architecture and tool schema design",
            "Production-ready API + admin configuration",
            "Documentation and handoff for your team",
        ],
        "tag": "Popular",
        "recommended": True,
        "icon": "BrainCircuit",
        "display_order": 1,
    },
    {
        "title": "RAG Systems",
        "slug": "rag-systems",
        "short_description": "Retrieval-augmented applications using clean pipelines, grounded context and scalable architecture.",
        "description": "Retrieval-Augmented Generation systems that answer from your documents and data—not guesses. I implement ingestion, chunking, embeddings, vector search, and response generation with quality controls so answers stay grounded and useful.",
        "features": [
            "PDF/document ingestion and chunking strategy",
            "Vector search with relevance tuning",
            "Grounded responses with source-aware context",
        ],
        "duration": [
            "Discovery & data audit: 1-2 days",
            "Ingestion + retrieval build: 1-2 weeks",
            "Quality tuning + evaluation: 3-6 days",
            "Go-live + monitoring: 3-7 days",
        ],
        "how_it_works": [
            "Upload/prepare documents and define answer expectations",
            "Set up ingestion: chunking, embeddings, and retrieval configuration",
            "Implement grounded response generation with quality checks",
            "Tune for relevance and deliver evaluation + runbook",
        ],
        "deliverables": [
            "Document ingestion pipeline",
            "Vector store + retrieval layer",
            "Grounded Q&A interface or API",
        ],
        "tag": "AI Core",
        "recommended": False,
        "icon": "Layers3",
        "display_order": 2,
    },
    {
        "title": "AI Chatbots",
        "slug": "ai-chatbots",
        "short_description": "Professional support, product and knowledge assistants that feel fast, useful and reliable.",
        "description": "Custom chatbots for support, onboarding, and product assistance that feel like a real teammate. I combine conversational UX with backend knowledge retrieval so replies stay accurate, concise, and aligned with your brand voice.",
        "features": [
            "Personal assistant-style UX and tone",
            "Knowledge base + portfolio-aware responses",
            "Admin controls for content and behavior",
        ],
        "duration": [
            "Discovery & conversation design: 1-2 days",
            "Bot build + retrieval wiring: 1-2 weeks",
            "Testing + UX refinements: 3-6 days",
            "Deployment + iteration window: 3-7 days",
        ],
        "how_it_works": [
            "Define use cases, tone, and what the bot should/shouldn’t do",
            "Set up knowledge sources and response policies",
            "Implement chat UI + backend prompt/retrieval logic",
            "Test with real questions and deliver the configured chatbot",
        ],
        "deliverables": [
            "Branded chat widget or embedded UI",
            "Knowledge ingestion + response tuning",
            "Analytics hooks and admin settings",
        ],
        "tag": "Recommended",
        "recommended": True,
        "icon": "Bot",
        "display_order": 3,
    },
    {
        "title": "FastAPI Backend",
        "slug": "fastapi-backend",
        "short_description": "Asynchronous Python APIs, robust integrations and backend systems built for production.",
        "description": "Production-grade FastAPI backends with clean architecture, async database access, authentication, and integrations. Ideal when you need reliable APIs, admin panels, and scalable services behind your AI products.",
        "features": [
            "Async SQLAlchemy + PostgreSQL",
            "JWT auth, admin APIs, and media handling",
            "Clean module structure and migrations",
        ],
        "duration": [
            "Backend design + API contract: 2-4 days",
            "Implementation + integrations: 1-2 weeks",
            "Testing + security review: 3-6 days",
            "Deployment-ready handoff: 2-5 days",
        ],
        "how_it_works": [
            "Confirm endpoints, auth needs, data model, and non-functional requirements",
            "Implement modules with async DB + validation + structured errors",
            "Wire integrations (media, emails, third-party services) and admin APIs",
            "Deliver production build + docs + deployment notes",
        ],
        "deliverables": [
            "REST API with auth and validation",
            "Database schema + migrations",
            "Deployment-ready project structure",
        ],
        "tag": "Backend",
        "recommended": False,
        "icon": "ServerCog",
        "display_order": 4,
    },
    {
        "title": "AI SaaS / MVP",
        "slug": "ai-saas-mvp",
        "short_description": "From idea to working product: ship lean AI-powered MVPs and polished internal tools.",
        "description": "Move from concept to a shippable AI MVP quickly without sacrificing quality. I help define scope, build the core product loop, integrate models/APIs, and deliver a polished experience you can demo to users or investors.",
        "features": [
            "Scope definition and lean architecture",
            "Frontend + backend + AI integration",
            "Deployment-ready MVP delivery",
        ],
        "duration": [
            "Discovery + scope lock: 2-4 days",
            "Build core product loop: 1-3 weeks",
            "Polish, QA, and iteration: 3-7 days",
            "Launch prep + rollout support: 2-7 days",
        ],
        "how_it_works": [
            "Align on MVP scope, user journey, and measurable outcomes",
            "Build the core features end-to-end (UI + APIs + AI integration)",
            "QA with real scenarios and iterate to stability",
            "Deliver a deployable MVP with a launch checklist",
        ],
        "deliverables": [
            "Working MVP with core user loop",
            "Frontend + backend integration",
            "Launch checklist and next-step roadmap",
        ],
        "tag": "MVP",
        "recommended": False,
        "icon": "Sparkles",
        "display_order": 5,
    },
    {
        "title": "AI Integration",
        "slug": "ai-integration",
        "short_description": "Integrate OpenAI, Gemini, Mistral and related tooling into modern existing software stacks.",
        "description": "Add AI capabilities into your existing product without rewriting everything. I integrate LLM providers, embeddings, and automation hooks into your current stack with sensible abstractions and cost-aware design.",
        "features": [
            "OpenAI / Gemini / Mistral integrations",
            "Embeddings, batch jobs, and async pipelines",
            "Safe rollout patterns for production apps",
        ],
        "duration": [
            "Discovery + integration plan: 1-3 days",
            "Implementation + provider wiring: 1-2 weeks",
            "Safety + cost controls: 3-6 days",
            "Rollout + support: 3-7 days",
        ],
        "how_it_works": [
            "Review your current stack and define integration boundaries",
            "Set up provider abstraction, embeddings, and prompt policies",
            "Implement async processing and guardrails for safe behavior",
            "Deliver integration, tests, and guidance for production rollout",
        ],
        "deliverables": [
            "Provider abstraction layer",
            "Integration into existing workflows",
            "Cost and latency optimization notes",
        ],
        "tag": "Integration",
        "recommended": False,
        "icon": "Puzzle",
        "display_order": 6,
    },
]


async def main():
    async with SessionLocal() as db:
        existing = await service_repository.list(db, public_only=False)
        if existing:
            print(f"services already present: {len(existing)}")
            return
        for item in DEFAULTS:
            await service_service.create(db, ServiceCreate(**item, is_published=True))
        print(f"seeded {len(DEFAULTS)} services")


if __name__ == "__main__":
    asyncio.run(main())
