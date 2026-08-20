"""initial schema"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision="0001_initial"
down_revision=None
branch_labels=None
depends_on=None

def upgrade():
    testimonialstatus=postgresql.ENUM("PENDING","APPROVED","REJECTED",name="testimonialstatus")
    contactstatus=postgresql.ENUM("UNREAD","READ","REPLIED","ARCHIVED",name="contactstatus")
    testimonialstatus.create(op.get_bind(),checkfirst=True)
    contactstatus.create(op.get_bind(),checkfirst=True)
    testimonialstatus_col=postgresql.ENUM("PENDING","APPROVED","REJECTED",name="testimonialstatus",create_type=False)
    contactstatus_col=postgresql.ENUM("UNREAD","READ","REPLIED","ARCHIVED",name="contactstatus",create_type=False)

    op.create_table("admins",
        sa.Column("id",postgresql.UUID(as_uuid=True),primary_key=True),
        sa.Column("name",sa.String(120),nullable=False),
        sa.Column("email",sa.String(320),nullable=False),
        sa.Column("password_hash",sa.String(255),nullable=False),
        sa.Column("is_active",sa.Boolean(),nullable=False,server_default=sa.true()),
        sa.Column("token_version",sa.Integer(),nullable=False,server_default="0"),
        sa.Column("last_login_at",sa.DateTime(timezone=True)),
        sa.Column("created_at",sa.DateTime(timezone=True),nullable=False,server_default=sa.func.now()),
        sa.Column("updated_at",sa.DateTime(timezone=True),nullable=False,server_default=sa.func.now()),
        sa.UniqueConstraint("email"))
    op.create_index("ix_admins_email","admins",["email"])

    op.create_table("skills",
        sa.Column("id",postgresql.UUID(as_uuid=True),primary_key=True),
        sa.Column("name",sa.String(100),nullable=False),sa.Column("category",sa.String(80),nullable=False),
        sa.Column("icon",sa.String(255)),sa.Column("description",sa.Text()),sa.Column("proficiency",sa.Integer()),
        sa.Column("display_order",sa.Integer(),nullable=False,server_default="0"),sa.Column("is_active",sa.Boolean(),nullable=False,server_default=sa.true()),
        sa.Column("created_at",sa.DateTime(timezone=True),nullable=False,server_default=sa.func.now()),sa.Column("updated_at",sa.DateTime(timezone=True),nullable=False,server_default=sa.func.now()),
        sa.CheckConstraint("proficiency >= 0 AND proficiency <= 100",name="ck_skill_proficiency"))
    op.create_index("ix_skills_category","skills",["category"])
    op.create_index("ix_skills_active_order","skills",["is_active","display_order"])

    op.create_table("projects",
        sa.Column("id",postgresql.UUID(as_uuid=True),primary_key=True),sa.Column("title",sa.String(180),nullable=False),
        sa.Column("slug",sa.String(200),nullable=False),sa.Column("short_description",sa.String(500),nullable=False),sa.Column("description",sa.Text(),nullable=False),
        sa.Column("github_url",sa.String(500)),sa.Column("live_url",sa.String(500)),sa.Column("featured_image_url",sa.String(1000)),sa.Column("imagekit_file_id",sa.String(255)),
        sa.Column("category",sa.String(100),nullable=False),sa.Column("technologies",postgresql.ARRAY(sa.String(80)),nullable=False,server_default="{}"),
        sa.Column("featured",sa.Boolean(),nullable=False,server_default=sa.false()),sa.Column("is_published",sa.Boolean(),nullable=False,server_default=sa.false()),
        sa.Column("display_order",sa.Integer(),nullable=False,server_default="0"),sa.Column("created_at",sa.DateTime(timezone=True),nullable=False,server_default=sa.func.now()),
        sa.Column("updated_at",sa.DateTime(timezone=True),nullable=False,server_default=sa.func.now()),sa.UniqueConstraint("slug"))
    op.create_index("ix_projects_slug","projects",["slug"])
    op.create_index("ix_projects_public","projects",["is_published","featured","display_order"])

    op.create_table("testimonials",
        sa.Column("id",postgresql.UUID(as_uuid=True),primary_key=True),sa.Column("name",sa.String(120),nullable=False),sa.Column("role",sa.String(150)),
        sa.Column("linkedin_url",sa.String(500)),sa.Column("message",sa.Text(),nullable=False),sa.Column("avatar_url",sa.String(1000)),sa.Column("imagekit_file_id",sa.String(255)),
        sa.Column("rating",sa.Integer()),sa.Column("status",testimonialstatus_col,nullable=False,server_default="PENDING"),
        sa.Column("is_featured",sa.Boolean(),nullable=False,server_default=sa.false()),sa.Column("display_order",sa.Integer(),nullable=False,server_default="0"),
        sa.Column("approved_at",sa.DateTime(timezone=True)),sa.Column("rejected_at",sa.DateTime(timezone=True)),
        sa.Column("created_at",sa.DateTime(timezone=True),nullable=False,server_default=sa.func.now()),sa.Column("updated_at",sa.DateTime(timezone=True),nullable=False,server_default=sa.func.now()),
        sa.CheckConstraint("rating IS NULL OR (rating >= 1 AND rating <= 5)",name="ck_testimonial_rating"))
    op.create_index("ix_testimonials_public","testimonials",["status","is_featured","display_order"])

    op.create_table("contacts",
        sa.Column("id",postgresql.UUID(as_uuid=True),primary_key=True),sa.Column("name",sa.String(120),nullable=False),sa.Column("email",sa.String(320),nullable=False),
        sa.Column("subject",sa.String(200),nullable=False),sa.Column("message",sa.Text(),nullable=False),sa.Column("status",contactstatus_col,nullable=False,server_default="UNREAD"),
        sa.Column("read_at",sa.DateTime(timezone=True)),sa.Column("replied_at",sa.DateTime(timezone=True)),sa.Column("created_at",sa.DateTime(timezone=True),nullable=False,server_default=sa.func.now()),
        sa.Column("updated_at",sa.DateTime(timezone=True),nullable=False,server_default=sa.func.now()))
    op.create_index("ix_contacts_status","contacts",["status"])

    op.create_table("email_templates",
        sa.Column("id",postgresql.UUID(as_uuid=True),primary_key=True),sa.Column("name",sa.String(120),nullable=False),sa.Column("slug",sa.String(120),nullable=False),
        sa.Column("subject",sa.String(250),nullable=False),sa.Column("html_body",sa.Text(),nullable=False),sa.Column("text_body",sa.Text()),sa.Column("variables",sa.JSON(),nullable=False),
        sa.Column("is_active",sa.Boolean(),nullable=False,server_default=sa.true()),sa.Column("created_at",sa.DateTime(timezone=True),nullable=False,server_default=sa.func.now()),
        sa.Column("updated_at",sa.DateTime(timezone=True),nullable=False,server_default=sa.func.now()),sa.UniqueConstraint("slug"))
    op.create_index("ix_email_templates_slug","email_templates",["slug"])

    op.create_table("media",
        sa.Column("id",postgresql.UUID(as_uuid=True),primary_key=True),sa.Column("file_id",sa.String(255),nullable=False),sa.Column("url",sa.String(1000),nullable=False),
        sa.Column("file_name",sa.String(255),nullable=False),sa.Column("mime_type",sa.String(100),nullable=False),sa.Column("size",sa.BigInteger(),nullable=False),
        sa.Column("width",sa.Integer()),sa.Column("height",sa.Integer()),sa.Column("folder",sa.String(255),nullable=False),
        sa.Column("created_at",sa.DateTime(timezone=True),nullable=False,server_default=sa.func.now()),sa.Column("updated_at",sa.DateTime(timezone=True),nullable=False,server_default=sa.func.now()),
        sa.UniqueConstraint("file_id"))
    op.create_index("ix_media_folder","media",["folder"])

def downgrade():
    for t in ["media","email_templates","contacts","testimonials","projects","skills","admins"]:
        op.drop_table(t)
    sa.Enum(name="contactstatus").drop(op.get_bind(),checkfirst=True)
    sa.Enum(name="testimonialstatus").drop(op.get_bind(),checkfirst=True)
