"""add email_otp_challenges table"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0007_email_otp"
down_revision = "0006_gallery_images"
branch_labels = None
depends_on = None

purpose_enum = postgresql.ENUM("contact", "booking", name="emailotppurpose", create_type=False)


def upgrade():
    bind = op.get_bind()
    sa.Enum("contact", "booking", name="emailotppurpose").create(bind, checkfirst=True)

    op.create_table(
        "email_otp_challenges",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("email", sa.String(320), nullable=False),
        sa.Column("purpose", purpose_enum, nullable=False),
        sa.Column("otp_hash", sa.String(128), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("attempt_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_email_otp_challenges_email", "email_otp_challenges", ["email"])


def downgrade():
    op.drop_index("ix_email_otp_challenges_email", table_name="email_otp_challenges")
    op.drop_table("email_otp_challenges")
    sa.Enum(name="emailotppurpose").drop(op.get_bind(), checkfirst=True)
