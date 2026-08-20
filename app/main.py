import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.core.database import SessionLocal, get_db
from app.core.exceptions import AppError, app_error_handler
from app.core.middleware import RequestContextMiddleware
from app.modules.email_template.seed import ensure_default_email_templates, sync_default_email_templates
from app.modules.email_verification.bootstrap import ensure_email_otp_schema
from app.modules.chatbot.bootstrap import ensure_chatbot_schema
from app.modules.faq.bootstrap import ensure_faq_schema
from app.modules.chatbot.vectorstore import ensure_pinecone_index
from app.modules.auth.bootstrap import ensure_bootstrap_admin
from app.modules.profile.bootstrap import ensure_professional_profile_copy
from app.modules.router import api_router

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")

@asynccontextmanager
async def lifespan(_: FastAPI):
    async with SessionLocal() as db:
        created = await ensure_default_email_templates(db)
        if created:
            logging.getLogger(__name__).info("Seeded %s default email template(s)", created)
        synced = await sync_default_email_templates(db)
        if synced:
            logging.getLogger(__name__).info("Synced %s email template(s) to latest HTML", synced)
        await ensure_email_otp_schema(db)
        await ensure_chatbot_schema(db)
        seeded_faqs = await ensure_faq_schema(db)
        if seeded_faqs:
            logging.getLogger(__name__).info("Seeded %s default FAQ(s)", seeded_faqs)
        if await ensure_professional_profile_copy(db):
            logging.getLogger(__name__).info("Updated profile copy to remove junior wording")
        await ensure_bootstrap_admin(db)
        ensure_pinecone_index()
    yield

app=FastAPI(title=settings.APP_NAME,version="1.0.0",docs_url="/docs",redoc_url="/redoc",lifespan=lifespan)
app.add_exception_handler(AppError,app_error_handler)
app.add_middleware(RequestContextMiddleware)
app.add_middleware(TrustedHostMiddleware,allowed_hosts=settings.allowed_hosts)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET","POST","PUT","PATCH","DELETE","OPTIONS"],
    allow_headers=["Authorization","Content-Type","X-Request-ID"],
)
app.include_router(api_router)

@app.get("/health",tags=["Health"])
async def health():
    return {"status":"healthy"}

@app.get("/health/db",tags=["Health"])
async def health_db(db:AsyncSession=Depends(get_db)):
    await db.execute(text("SELECT 1"))
    return {"status":"healthy"}
