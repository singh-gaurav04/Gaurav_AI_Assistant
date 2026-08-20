from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.modules.profile.service import profile_service
from app.modules.profile.schema import ProfileOut
from app.modules.skill.service import skill_service
from app.modules.skill.schema import SkillOut
from app.modules.project.repository import project_repository
from app.modules.project.schema import ProjectOut
from app.modules.experience.service import experience_service
from app.modules.experience.schema import ExperienceOut
from app.modules.certification.service import certification_service
from app.modules.certification.schema import CertificationOut
from app.modules.testimonial.repository import testimonial_repository
from app.modules.testimonial.schema import TestimonialOut
from app.modules.service.service import service_service
from app.modules.service.schema import ServiceOut
from app.modules.faq.service import faq_service
from app.modules.faq.schema import FaqOut

public_router = APIRouter(tags=["Portfolio"])

@public_router.get("/portfolio")
async def portfolio(db: AsyncSession = Depends(get_db)):
    profile = await profile_service.get_or_none(db)
    skills = await skill_service.list(db, True)
    projects = await project_repository.all_published(db)
    real_projects = await project_repository.real_projects(db)
    archive_projects = [x for x in projects if not x.is_real_project]
    featured = [x for x in archive_projects if x.featured]
    experiences = await experience_service.list(db, True)
    certifications = await certification_service.list(db, True)
    testimonials = await testimonial_repository.list_public(db)
    services = await service_service.list(db, public_only=True)
    faqs = await faq_service.list(db, True)
    return {"success": True, "data": {
        "profile": ProfileOut.model_validate(profile) if profile else None,
        "skills": [SkillOut.model_validate(x) for x in skills],
        "projects": [ProjectOut.model_validate(x) for x in archive_projects],
        "real_projects": [ProjectOut.model_validate(x) for x in real_projects],
        "featured_projects": [ProjectOut.model_validate(x) for x in featured],
        "experiences": [ExperienceOut.model_validate(x) for x in experiences],
        "certifications": [CertificationOut.model_validate(x) for x in certifications],
        "testimonials": [TestimonialOut.model_validate(x) for x in testimonials],
        "services": [ServiceOut.model_validate(x) for x in services],
        "faqs": [FaqOut.model_validate(x) for x in faqs],
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
    }}
