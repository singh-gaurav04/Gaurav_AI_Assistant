import asyncio
import uuid
from sqlalchemy import select
from app.core.database import SessionLocal
from app.modules.profile.model import Profile
from app.modules.skill.model import Skill
from app.modules.project.model import Project
from app.modules.experience.model import Experience
from app.modules.certification.model import Certification

SKILLS = [
    ("LangChain", "AI_STACK", "🔗", 90, 0),
    ("LangGraph", "AI_STACK", "🧠", 85, 1),
    ("RAG Systems", "AI_STACK", "📚", 90, 2),
    ("Prompt Engineering", "AI_STACK", "✍️", 88, 3),
    ("Agentic AI", "AI_STACK", "🤖", 85, 4),
    ("Hugging Face Transformers", "AI_STACK", "🤗", 85, 5),
    ("OpenAI API", "AI_STACK", "⚡", 85, 6),
    ("Mistral API", "AI_STACK", "🌪️", 80, 7),
    ("Embeddings & Vector Search", "AI_STACK", "🔍", 88, 8),
    ("Multi-Agent Systems", "AI_STACK", "🧩", 85, 9),
    ("Python", "programming", "🐍", 92, 10),
    ("Java", "programming", "☕", 88, 11),
    ("C++", "programming", "⚡", 85, 12),
    ("JavaScript", "programming", "🟨", 80, 13),
    ("FastAPI", "frameworks", "⚡", 90, 14),
    ("Spring Boot", "frameworks", "🍃", 85, 15),
    ("React.js", "frameworks", "⚛️", 82, 16),
    ("Node.js", "frameworks", "🟢", 78, 17),
    ("Express.js", "frameworks", "🚀", 78, 18),
    ("PyTorch", "ml_dl", "🔥", 85, 19),
    ("Scikit-learn", "ml_dl", "📈", 80, 20),
    ("Pandas", "ml_dl", "📊", 82, 21),
    ("NumPy", "ml_dl", "🔢", 80, 22),
    ("Model Training", "ml_dl", "🏋️", 85, 23),
    ("Fine-tuning", "ml_dl", "🎯", 80, 24),
    ("Model Evaluation", "ml_dl", "📏", 85, 25),
    ("Pinecone", "vector_db", "🌲", 85, 26),
    ("Qdrant", "vector_db", "📦", 80, 27),
    ("Docker", "deployment", "🐳", 88, 28),
    ("AWS EC2", "deployment", "☁️", 80, 29),
    ("AWS S3", "deployment", "🗂️", 78, 30),
    ("Model Deployment", "deployment", "🚀", 85, 31),
    ("REST API (FastAPI)", "deployment", "🔌", 90, 32),
    ("Git", "tools", "📝", 90, 33),
    ("GitHub", "tools", "🐙", 88, 34),
    ("Postman", "tools", "📮", 82, 35),
    ("VS Code", "tools", "💻", 90, 36),
]

PROJECTS = [
    {
        "title": "AI Personal Assistant Chatbot",
        "slug": "ai-personal-assistant-chatbot",
        "short_description": "Context-aware RAG chatbot with FastAPI and a live conversational UI.",
        "description": "Developed an AI-powered personal assistant chatbot capable of answering queries based on user context using LLMs and Retrieval-Augmented Generation (RAG). Integrated FastAPI backend with a responsive frontend to deliver real-time conversational experience. Implemented prompt engineering, API handling, and optimized response generation for intelligent interactions.",
        "github_url": "https://github.com/singh-gaurav04/Gaurav_AI_Assistant",
        "live_url": "https://gaurav26lnct.netlify.app/",
        "category": "AI",
        "technologies": ["Python", "FastAPI", "LangChain", "OpenAI API", "React.js"],
        "featured": True,
        "is_published": True,
        "display_order": 0,
    },
    {
        "title": "AI-Powered EDI Converter & Learning Platform",
        "slug": "knowedi",
        "short_description": "Converts EDI data into readable formats and includes interview-ready learning modules.",
        "description": "Developed an AI-powered tool that converts EDI (Electronic Data Interchange) data into human-readable, printable formats. The platform also includes an interactive learning module to help users understand EDI concepts and prepare for interviews with curated questions and explanations.",
        "github_url": "https://github.com/singh-gaurav04/KnowEDI",
        "live_url": "https://knowedi.vercel.app/",
        "category": "AI",
        "technologies": ["Python", "FastAPI", "LangChain", "GPT", "React.js"],
        "featured": True,
        "is_published": True,
        "display_order": 1,
    },
    {
        "title": "Job Portal App",
        "slug": "job-portal-app",
        "short_description": "Full-stack job portal with JWT auth and role-based admin controls.",
        "description": "Full-stack Job Portal application featuring modules for user registration, job posting, and admin controls with JWT-based authentication and role-based authorization.",
        "github_url": "https://github.com/singh-gaurav04/JOB_PORTAL",
        "live_url": "https://github.com/singh-gaurav04/JOB_PORTAL",
        "category": "web",
        "technologies": ["Java", "Spring Boot", "Spring Security", "React.js", "MongoDB"],
        "featured": True,
        "is_published": True,
        "display_order": 2,
    },
    {
        "title": "Car Price Predictor App",
        "slug": "car-price-predictor",
        "short_description": "Linear regression model that estimates car prices from vehicle features.",
        "description": "A web application that predicts the price of a car based on its features using linear regression.",
        "github_url": "https://github.com/singh-gaurav04/Car_predictor_app",
        "live_url": "https://github.com/singh-gaurav04/Car_predictor_app",
        "category": "AI",
        "technologies": ["React", "Node.js", "Machine Learning", "Linear Regression", "Python", "scikit-learn"],
        "featured": True,
        "is_published": True,
        "display_order": 3,
    },
]

CERTIFICATIONS = [
    ("Master Java and Spring Boot", "Udemy (Telusko)", "2025", "Comprehensive course covering Java fundamentals and Spring Boot development", "UC-198f1282-d19c-491e-87c9-15a3bc963911", "https://drive.google.com/file/d/1ck1icA22LNmR-_INO3o7Bc7gDHf92S_0/view?usp=drive_link", "☕", 0),
    ("Backend Domination", "Sheryians Coding School", "2024", "Advanced backend development course focusing on modern web technologies", "9753a39d", "https://drive.google.com/file/d/1zLIyI5nGFDH1RHErcKnFSJG9vA76LNiA/view?usp=drive_link", "🚀", 1),
    ("Database Management System", "NPTEL", "2024", "Comprehensive course on database design, implementation, and management", "NPTEL-DBMS-2024", "https://drive.google.com/file/d/1xgOcqUYPhwBapmXoW2xsmvZvrnLGLXLv/view?usp=drive_link", "🗄️", 2),
    ("AWS Certified Solutions Architect", "AWS", "2024", "Cloud platform certification", "--", "https://www.credly.com/go/hh50F4n0", "☁️", 3),
    ("FastAPI Development", "Udemy", "2025", "Built high-performance APIs for AI/ML applications using FastAPI", "--", None, "⚡", 4),
    ("Generative AI Fundamentals", "Udemy", "2025", "Learned LLMs, prompt engineering, and AI-powered application development", "--", None, "🤖", 5),
]

async def main():
    async with SessionLocal() as db:
        if not await db.scalar(select(Profile).limit(1)):
            db.add(Profile(
                id=uuid.uuid4(),
                name="Gaurav Singh",
                title="AI Engineer | GenAI | Backend",
                handle="singh-gaurav04",
                bio="AI Engineer focused on Generative AI, RAG systems, and backend development. I build production-ready intelligent applications with Python, FastAPI, LangChain, and modern full-stack tools. Open to AI Engineer and GenAI roles.",
                location="Bengaluru, Karnataka",
                email="gaurav26lnct@gmail.com",
                phone="+91 7479582593",
                graduation_year="2026",
                profile_image_url="/logo.png",
                resume_url="/assets/documents/Resume.pdf",
                is_placed=False,
                placement_status="Open to AI Engineer roles",
                github_url="https://github.com/singh-gaurav04",
                linkedin_url="https://www.linkedin.com/in/gaurav26lnct/",
                leetcode_url="https://leetcode.com/u/Gaurav__04/",
                response_time="I typically respond within 24 hours",
            ))

        if not await db.scalar(select(Skill).limit(1)):
            for name, category, icon, proficiency, order in SKILLS:
                db.add(Skill(name=name, category=category, icon=icon, proficiency=proficiency, display_order=order, is_active=True))

        if not await db.scalar(select(Project).limit(1)):
            for item in PROJECTS:
                db.add(Project(**item))

        if not await db.scalar(select(Experience).limit(1)):
            db.add(Experience(
                title="Top Performer in Web Development",
                company="GDSC in LNCTE",
                location="Bhopal, Madhya Pradesh",
                period="2024",
                type="Achievement",
                description="Recognized as top performer in web development activities and competitions within the Google Developer Student Club at LNCTE.",
                achievements=[
                    "Demonstrated exceptional skills in web development technologies",
                    "Contributed significantly to club activities and projects",
                    "Mentored fellow students in web development best practices",
                ],
                technologies=["HTML", "CSS", "JavaScript", "React", "Node.js"],
                link="https://gdsc.community.dev/",
                display_order=0,
                is_published=True,
            ))

        if not await db.scalar(select(Certification).limit(1)):
            for title, issuer, date, description, credential_id, link, icon, order in CERTIFICATIONS:
                db.add(Certification(
                    title=title, issuer=issuer, date=date, description=description,
                    credential_id=credential_id, link=link, icon=icon, display_order=order, is_published=True,
                ))

        from app.modules.email_template.seed import ensure_default_email_templates
        await ensure_default_email_templates(db)

        await db.commit()
        print("Portfolio seed complete")

if __name__ == "__main__":
    asyncio.run(main())
