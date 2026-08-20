"""add profile, experience, certification, visit tables"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0002_portfolio_cms"
down_revision = "0001_initial"
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        "profiles",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("title", sa.String(250), nullable=False),
        sa.Column("handle", sa.String(80)),
        sa.Column("bio", sa.Text(), nullable=False),
        sa.Column("location", sa.String(160)),
        sa.Column("email", sa.String(320), nullable=False),
        sa.Column("phone", sa.String(40)),
        sa.Column("graduation_year", sa.String(20)),
        sa.Column("profile_image_url", sa.String(1000)),
        sa.Column("resume_url", sa.String(1000)),
        sa.Column("is_placed", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("placement_status", sa.String(200)),
        sa.Column("placement_company", sa.String(160)),
        sa.Column("placement_role", sa.String(160)),
        sa.Column("github_url", sa.String(500)),
        sa.Column("linkedin_url", sa.String(500)),
        sa.Column("leetcode_url", sa.String(500)),
        sa.Column("response_time", sa.String(200)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        "experiences",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("title", sa.String(180), nullable=False),
        sa.Column("company", sa.String(180), nullable=False),
        sa.Column("location", sa.String(160)),
        sa.Column("period", sa.String(80), nullable=False),
        sa.Column("type", sa.String(80), nullable=False, server_default="Experience"),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("achievements", postgresql.ARRAY(sa.String(500)), nullable=False, server_default="{}"),
        sa.Column("technologies", postgresql.ARRAY(sa.String(80)), nullable=False, server_default="{}"),
        sa.Column("link", sa.String(500)),
        sa.Column("display_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("is_published", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_experiences_public", "experiences", ["is_published", "display_order"])

    op.create_table(
        "certifications",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("issuer", sa.String(160), nullable=False),
        sa.Column("date", sa.String(40), nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("credential_id", sa.String(160)),
        sa.Column("link", sa.String(500)),
        sa.Column("icon", sa.String(32)),
        sa.Column("display_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("is_published", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_certifications_public", "certifications", ["is_published", "display_order"])

    op.create_table(
        "visits",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("page", sa.String(1000), nullable=False),
        sa.Column("user_agent", sa.Text()),
        sa.Column("referrer", sa.String(1000)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_visits_created_at", "visits", ["created_at"])

def downgrade():
    op.drop_index("ix_visits_created_at", table_name="visits")
    op.drop_table("visits")
    op.drop_index("ix_certifications_public", table_name="certifications")
    op.drop_table("certifications")
    op.drop_index("ix_experiences_public", table_name="experiences")
    op.drop_table("experiences")
    op.drop_table("profiles")
