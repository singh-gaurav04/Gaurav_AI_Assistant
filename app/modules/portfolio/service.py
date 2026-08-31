import asyncio

from app.core.cache import get_cached, set_cached
from app.core.database import SessionLocal
from app.modules.certification.schema import CertificationOut
from app.modules.certification.service import certification_service
from app.modules.experience.schema import ExperienceOut
from app.modules.experience.service import experience_service
from app.modules.faq.schema import FaqOut
from app.modules.faq.service import faq_service
from app.modules.profile.schema import ProfileOut
from app.modules.profile.service import profile_service
from app.modules.project.repository import project_repository
from app.modules.project.schema import ProjectOut
from app.modules.service.schema import ServiceOut
from app.modules.service.service import service_service
from app.modules.skill.schema import SkillOut
from app.modules.skill.service import skill_service
from app.modules.testimonial.repository import testimonial_repository
from app.modules.testimonial.schema import TestimonialOut

PORTFOLIO_CACHE_KEY = "portfolio:public"
PORTFOLIO_CACHE_TTL = 60


async def _fetch_profile():
    async with SessionLocal() as db:
        return await profile_service.get_or_none(db)


async def _fetch_skills():
    async with SessionLocal() as db:
        return await skill_service.list(db, True)


async def _fetch_projects():
    async with SessionLocal() as db:
        return await project_repository.all_published(db)


async def _fetch_experiences():
    async with SessionLocal() as db:
        return await experience_service.list(db, True)


async def _fetch_certifications():
    async with SessionLocal() as db:
        return await certification_service.list(db, True)


async def _fetch_testimonials():
    async with SessionLocal() as db:
        return await testimonial_repository.list_public(db)


async def _fetch_services():
    async with SessionLocal() as db:
        return await service_service.list(db, public_only=True)


async def _fetch_faqs():
    async with SessionLocal() as db:
        return await faq_service.list(db, True)


def _serialize_portfolio(
    profile,
    skills,
    projects,
    experiences,
    certifications,
    testimonials,
    services,
    faqs,
) -> dict:
    archive_projects = [x for x in projects if not x.is_real_project]
    real_projects = [x for x in projects if x.is_real_project]
    featured = [x for x in archive_projects if x.featured]

    return {
        "profile": ProfileOut.model_validate(profile).model_dump(mode="json") if profile else None,
        "skills": [SkillOut.model_validate(x).model_dump(mode="json") for x in skills],
        "projects": [ProjectOut.model_validate(x).model_dump(mode="json") for x in archive_projects],
        "real_projects": [ProjectOut.model_validate(x).model_dump(mode="json") for x in real_projects],
        "featured_projects": [ProjectOut.model_validate(x).model_dump(mode="json") for x in featured],
        "experiences": [ExperienceOut.model_validate(x).model_dump(mode="json") for x in experiences],
        "certifications": [CertificationOut.model_validate(x).model_dump(mode="json") for x in certifications],
        "testimonials": [TestimonialOut.model_validate(x).model_dump(mode="json") for x in testimonials],
        "services": [ServiceOut.model_validate(x).model_dump(mode="json") for x in services],
        "faqs": [FaqOut.model_validate(x).model_dump(mode="json") for x in faqs],
        "stats": {
            "projects": len(archive_projects),
            "real_projects": len(real_projects),
            "skills": len(skills),
            "experiences": len(experiences),
            "certifications": len(certifications),
            "testimonials": len(testimonials),
            "services": len(services),
            "faqs": len(faqs),
        },
    }


async def build_portfolio_payload() -> dict:
    (
        profile,
        skills,
        projects,
        experiences,
        certifications,
        testimonials,
        services,
        faqs,
    ) = await asyncio.gather(
        _fetch_profile(),
        _fetch_skills(),
        _fetch_projects(),
        _fetch_experiences(),
        _fetch_certifications(),
        _fetch_testimonials(),
        _fetch_services(),
        _fetch_faqs(),
    )

    return _serialize_portfolio(
        profile,
        skills,
        projects,
        experiences,
        certifications,
        testimonials,
        services,
        faqs,
    )


async def get_portfolio_payload() -> dict:
    cached = await get_cached(PORTFOLIO_CACHE_KEY)
    if cached is not None:
        return cached

    payload = await build_portfolio_payload()
    await set_cached(PORTFOLIO_CACHE_KEY, payload, PORTFOLIO_CACHE_TTL)
    return payload
