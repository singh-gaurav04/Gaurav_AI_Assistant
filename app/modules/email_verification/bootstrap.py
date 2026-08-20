from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


async def ensure_email_otp_schema(db: AsyncSession) -> None:
    await db.execute(
        text(
            """
            DO $$ BEGIN
                CREATE TYPE emailotppurpose AS ENUM ('contact', 'booking');
            EXCEPTION
                WHEN duplicate_object THEN null;
            END $$;
            """
        )
    )
    await db.execute(
        text(
            """
            CREATE TABLE IF NOT EXISTS email_otp_challenges (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                email VARCHAR(320) NOT NULL,
                purpose emailotppurpose NOT NULL,
                otp_hash VARCHAR(128) NOT NULL,
                expires_at TIMESTAMPTZ NOT NULL,
                attempt_count INTEGER NOT NULL DEFAULT 0,
                created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
                updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
            );
            """
        )
    )
    await db.execute(
        text(
            """
            CREATE INDEX IF NOT EXISTS ix_email_otp_challenges_email
            ON email_otp_challenges (email);
            """
        )
    )
    await db.execute(
        text(
            """
            CREATE TABLE IF NOT EXISTS email_verifications (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                email VARCHAR(320) NOT NULL,
                purpose emailotppurpose NOT NULL,
                verified_at TIMESTAMPTZ NOT NULL,
                consumed_at TIMESTAMPTZ,
                contact_id UUID,
                created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
                updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
            );
            """
        )
    )
    await db.execute(
        text(
            """
            CREATE INDEX IF NOT EXISTS ix_email_verifications_email
            ON email_verifications (email);
            """
        )
    )
    await db.commit()
