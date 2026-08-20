"""add is_real_project flag to projects"""
from alembic import op
import sqlalchemy as sa

revision = "0004_real_projects"
down_revision = "0003_chatbot_rag"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "projects",
        sa.Column("is_real_project", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.create_index("ix_projects_real_published", "projects", ["is_real_project", "is_published"])


def downgrade():
    op.drop_index("ix_projects_real_published", table_name="projects")
    op.drop_column("projects", "is_real_project")
