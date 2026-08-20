"""add services table"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0005_services"
down_revision = "0004_real_projects"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "services",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("title", sa.String(180), nullable=False),
        sa.Column("slug", sa.String(200), nullable=False),
        sa.Column("short_description", sa.String(500), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("features", postgresql.ARRAY(sa.String(500)), nullable=False, server_default="{}"),
        sa.Column("duration", postgresql.ARRAY(sa.String(500)), nullable=False, server_default="{}"),
        sa.Column("how_it_works", postgresql.ARRAY(sa.String(500)), nullable=False, server_default="{}"),
        sa.Column("deliverables", postgresql.ARRAY(sa.String(500)), nullable=False, server_default="{}"),
        sa.Column("tag", sa.String(80)),
        sa.Column("recommended", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("featured_image_url", sa.String(1000)),
        sa.Column("imagekit_file_id", sa.String(255)),
        sa.Column("icon", sa.String(80)),
        sa.Column("display_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("is_published", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_services_slug", "services", ["slug"], unique=True)
    op.create_index("ix_services_public", "services", ["is_published", "display_order"])
    op.create_index("ix_services_recommended", "services", ["recommended"])


def downgrade():
    op.drop_index("ix_services_recommended", table_name="services")
    op.drop_index("ix_services_public", table_name="services")
    op.drop_index("ix_services_slug", table_name="services")
    op.drop_table("services")
