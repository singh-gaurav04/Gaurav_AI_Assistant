# Portfolio CMS Backend

Production-oriented headless CMS backend for a personal portfolio using FastAPI, PostgreSQL, async SQLAlchemy, Alembic, JWT admin authentication, ImageKit, Pillow-based image optimization and provider-abstracted email delivery.

## Architecture

Router → Service → Repository → PostgreSQL

External integrations live in reusable services. Business logic is kept out of route handlers where practical. Public endpoints only expose active/published/approved content.

### Security decisions

- Argon2 password hashing.
- Short-lived JWT access tokens.
- `token_version` stored on the admin enables server-side revocation on logout without Redis.
- Trusted-host and CORS middleware.
- Security headers and request IDs.
- Environment-only secrets.
- Image MIME, size, integrity and dimension checks.
- Honeypot field on public contact form for basic spam resistance.
- No rate limiting, matching the requested constraint.

## Important production notes

1. The included logout revokes **all current access tokens for that admin** by incrementing `token_version`. If per-device logout is required later, add a durable PostgreSQL session table.
2. ImageKit deletion is performed before deleting the media row so failed remote deletion does not silently orphan state.
3. Email delivery uses the **Mailgun API** (`MAILGUN_API_KEY` + `MAILGUN_DOMAIN`) over HTTPS — works on Render free tier. Sandbox domains only send to authorized recipients until you verify a custom domain.
4. For multi-instance deployment, JWT authentication works without Redis because revocation state lives in PostgreSQL.
5. Run Alembic migrations; do not use `Base.metadata.create_all()`.
6. Supabase: use the **Session pooler** connection string (IPv4). Direct `db.*.supabase.co` URLs are IPv6-only and cause `Network is unreachable` on most hosts (Render, GitHub Actions, many VPS images).

## Setup

```bash
cp .env.example .env
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
python scripts/create_admin.py
uvicorn app.main:app --reload
```

API docs:
- `/docs`
- `/redoc`

Health:
- `/health`
- `/health/db`

## Docker

```bash
docker compose up --build
```

Services: FastAPI + PostgreSQL only.

## Main endpoints

Public:
- `GET /api/v1/portfolio`
- `GET /api/v1/projects`
- `GET /api/v1/projects/featured`
- `GET /api/v1/projects/{slug}`
- `GET /api/v1/skills`
- `GET /api/v1/testimonials`
- `POST /api/v1/contact`

Auth:
- `POST /api/v1/auth/login`
- `GET /api/v1/auth/me`
- `POST /api/v1/auth/logout`

Admin:
- `/api/v1/admin/dashboard`
- `/api/v1/admin/projects`
- `/api/v1/admin/skills`
- `/api/v1/admin/testimonials`
- `/api/v1/admin/contacts`
- `/api/v1/admin/media`

## Remaining extension points

The core implementation is runnable and intentionally avoids unnecessary infrastructure. For a full enterprise deployment, next additions should be:
- Complete email-template CRUD/preview/test routes.
- Contact reply endpoint wired to EmailService.
- Project/testimonial image attach/replace helpers.
- Recent-activity feed with a small audit/event table if durable activity history is required.
- Comprehensive async API integration tests using a dedicated PostgreSQL test database.
- CI pipeline for lint/type-check/test/migration verification.
