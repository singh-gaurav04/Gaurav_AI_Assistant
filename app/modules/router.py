from fastapi import APIRouter
from app.modules.auth.controller import router as auth_router
from app.modules.dashboard.controller import admin_router as dashboard_router
from app.modules.portfolio.controller import public_router as portfolio_router
from app.modules.profile.controller import public_router as profile_public, admin_router as profile_admin
from app.modules.skill.controller import public_router as skill_public, admin_router as skill_admin
from app.modules.project.controller import public_router as project_public, admin_router as project_admin
from app.modules.experience.controller import public_router as experience_public, admin_router as experience_admin
from app.modules.certification.controller import public_router as certification_public, admin_router as certification_admin
from app.modules.testimonial.controller import public_router as testimonial_public, admin_router as testimonial_admin
from app.modules.contact.controller import public_router as contact_public, admin_router as contact_admin
from app.modules.email_verification.controller import public_router as email_verification_public
from app.modules.visit.controller import public_router as visit_public
from app.modules.email_template.controller import admin_router as email_admin
from app.modules.media.controller import admin_router as media_admin
from app.modules.chatbot.controller import public_router as chatbot_public, admin_router as chatbot_admin
from app.modules.service.controller import public_router as service_public, admin_router as service_admin

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(auth_router)
api_router.include_router(portfolio_router)
api_router.include_router(profile_public)
api_router.include_router(skill_public)
api_router.include_router(project_public)
api_router.include_router(experience_public)
api_router.include_router(certification_public)
api_router.include_router(testimonial_public)
api_router.include_router(contact_public)
api_router.include_router(email_verification_public)
api_router.include_router(visit_public)
api_router.include_router(chatbot_public)
api_router.include_router(service_public)
api_router.include_router(dashboard_router)
api_router.include_router(profile_admin)
api_router.include_router(skill_admin)
api_router.include_router(project_admin)
api_router.include_router(experience_admin)
api_router.include_router(certification_admin)
api_router.include_router(testimonial_admin)
api_router.include_router(contact_admin)
api_router.include_router(email_admin)
api_router.include_router(media_admin)
api_router.include_router(chatbot_admin)
api_router.include_router(service_admin)
