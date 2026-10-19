"""Ingest the portfolio website content into the chatbot knowledge base.

Usage (from the backend root):
    python -m scripts.ingest_portfolio_site [path/to/portfolio.json]

Defaults to ../gaurav_portfolio/src/data/portfolio.json. Re-running replaces the
previous website document, so run it again whenever the site content changes.
"""

import asyncio
import json
import sys
from pathlib import Path

from app.core.config import settings
from app.core.database import SessionLocal
from app.modules.chatbot.repository import chatbot_repository
from app.modules.chatbot.service import chatbot_service

DOCUMENT_NAME = "portfolio-website.txt"
DEFAULT_SOURCE = Path(__file__).resolve().parents[2] / "gaurav_portfolio" / "src" / "data" / "portfolio.json"


def _join(items) -> str:
    return ", ".join(str(item) for item in items if item)


def build_text(data: dict) -> str:
    profile = data.get("profile") or {}
    name = profile.get("name") or "Gaurav Singh"
    site = settings.PUBLIC_SITE_URL.rstrip("/")
    sections: list[str] = []

    intro = [f"{name} — {profile.get('title', '')}.", profile.get("bio", ""), profile.get("hero_detail", "")]
    if profile.get("focus"):
        intro.append(f"Core focus: {_join(profile['focus'])}.")
    sections.append("ABOUT GAURAV\n" + " ".join(part for part in intro if part))

    if profile.get("about"):
        sections.append("ABOUT ME\n" + "\n".join(profile["about"]))

    contact = [
        f"Email: {profile.get('email')}" if profile.get("email") else "",
        f"Phone: {profile.get('phone')}" if profile.get("phone") else "",
        f"Location: {profile.get('location')}" if profile.get("location") else "",
        f"GitHub: {profile.get('github_url')}" if profile.get("github_url") else "",
        f"LinkedIn: {profile.get('linkedin_url')}" if profile.get("linkedin_url") else "",
        f"Portfolio website: {site}",
    ]
    if profile.get("resume_url"):
        contact.append(f"Latest resume: {site}/{profile['resume_url'].lstrip('/')}")
    sections.append("CONTACT\n" + "\n".join(line for line in contact if line))

    if data.get("skills"):
        lines = [f"{group['title']}: {_join(group.get('items', []))}." for group in data["skills"]]
        sections.append("TECHNICAL SKILLS\n" + "\n".join(lines))

    for exp in data.get("experiences") or []:
        body = [
            f"{exp.get('title')} at {exp.get('company')} ({exp.get('period', '')}, {exp.get('location', '')}).",
            exp.get("description", ""),
            " ".join(exp.get("achievements") or []),
        ]
        if exp.get("technologies"):
            body.append(f"Technologies: {_join(exp['technologies'])}.")
        sections.append("EXPERIENCE\n" + " ".join(part for part in body if part))

    def project_block(project: dict, label: str) -> str:
        head = f"{project.get('title')}"
        if project.get("category"):
            head += f" ({project['category']})"
        if project.get("period"):
            head += f", {project['period']}"
        body = [head + ".", project.get("description") or project.get("short_description", "")]
        if project.get("highlights"):
            body.append(" ".join(project["highlights"]))
        if project.get("focus"):
            body.append(f"Focus: {_join(project['focus'])}.")
        if project.get("technologies"):
            body.append(f"Tech stack: {_join(project['technologies'])}.")
        if project.get("live_url"):
            body.append(f"Live site: {project['live_url']}")
        if project.get("github_url"):
            body.append(f"Source code: {project['github_url']}")
        return f"{label}\n" + " ".join(part for part in body if part)

    for project in data.get("real_projects") or []:
        sections.append(project_block(project, "FEATURED PROJECT"))
    for project in data.get("projects") or []:
        sections.append(project_block(project, "OTHER PROJECT"))

    for item in data.get("achievements") or []:
        sections.append(f"ACHIEVEMENT\n{item.get('title')}. {item.get('description', '')}")

    for item in data.get("education") or []:
        sections.append(
            f"EDUCATION\n{item.get('degree')}, {item.get('institution')} ({item.get('period', '')}). {item.get('grade', '')}"
        )

    if data.get("certifications"):
        certs = [_join([c.get("title"), c.get("issuer"), c.get("date")]) for c in data["certifications"]]
        sections.append("CERTIFICATIONS\n" + "; ".join(certs) + ".")

    return "\n\n".join(sections)


async def main(source: Path) -> None:
    data = json.loads(source.read_text(encoding="utf-8"))
    text = build_text(data)

    async with SessionLocal() as db:
        for document in await chatbot_repository.list_documents(db):
            if document.original_filename == DOCUMENT_NAME:
                await chatbot_service.delete_document(db, document.id)
                print(f"Removed previous {DOCUMENT_NAME}")

    async with SessionLocal() as db:
        result = await chatbot_service.ingest_text(db, filename=DOCUMENT_NAME, text=text)
        print(f"Ingested {result.original_filename}: {result.chunk_count} chunks ({len(text)} chars)")


if __name__ == "__main__":
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_SOURCE
    asyncio.run(main(path))
