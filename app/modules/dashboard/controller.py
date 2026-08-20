from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.dependencies import get_current_admin
from app.modules.project.model import Project
from app.modules.skill.model import Skill
from app.modules.testimonial.model import Testimonial, TestimonialStatus
from app.modules.contact.model import Contact, ContactStatus
from app.modules.experience.model import Experience
from app.modules.certification.model import Certification
from app.modules.visit.model import Visit

admin_router = APIRouter(prefix="/admin", tags=["Admin"], dependencies=[Depends(get_current_admin)])

@admin_router.get("/dashboard")
async def dashboard(db: AsyncSession = Depends(get_db)):
    async def count(model, *where):
        return int(await db.scalar(select(func.count()).select_from(model).where(*where)) or 0)
    return {"success": True, "data": {
        "projects": {"total": await count(Project), "published": await count(Project, Project.is_published.is_(True)), "featured": await count(Project, Project.featured.is_(True))},
        "skills": {"total": await count(Skill), "active": await count(Skill, Skill.is_active.is_(True))},
        "experiences": {"total": await count(Experience), "published": await count(Experience, Experience.is_published.is_(True))},
        "certifications": {"total": await count(Certification), "published": await count(Certification, Certification.is_published.is_(True))},
        "testimonials": {
            "total": await count(Testimonial),
            "pending": await count(Testimonial, Testimonial.status == TestimonialStatus.PENDING),
            "approved": await count(Testimonial, Testimonial.status == TestimonialStatus.APPROVED),
            "rejected": await count(Testimonial, Testimonial.status == TestimonialStatus.REJECTED),
        },
        "contacts": {"total": await count(Contact), "unread": await count(Contact, Contact.status == ContactStatus.UNREAD), "replied": await count(Contact, Contact.status == ContactStatus.REPLIED)},
        "visits": {"total": await count(Visit)},
    }}
