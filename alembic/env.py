from logging.config import fileConfig
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config
from alembic import context
from app.core.config import settings
from app.core.db_url import (
    assert_database_host_reachable,
    build_connect_args,
    explain_db_connect_error,
    DatabaseNetworkError,
)
from app.modules.shared.model import Base
import app.modules

config = context.config
config.set_main_option("sqlalchemy.url", settings.async_database_url)
if config.config_file_name:
    fileConfig(config.config_file_name)
target_metadata = Base.metadata


def run_migrations_offline():
    context.configure(
        url=settings.async_database_url,
        target_metadata=target_metadata,
        literal_binds=True,
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations():
    assert_database_host_reachable(settings.async_database_url)
    section = config.get_section(config.config_ini_section) or {}
    section["sqlalchemy.url"] = settings.async_database_url
    connectable = async_engine_from_config(
        section,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
        connect_args=build_connect_args(settings.async_database_url, settings.DATABASE_SSL),
    )
    try:
        async with connectable.connect() as connection:

            def do_migrations(conn):
                context.configure(connection=conn, target_metadata=target_metadata, compare_type=True)
                with context.begin_transaction():
                    context.run_migrations()

            await connection.run_sync(do_migrations)
    except (OSError, ConnectionError) as exc:
        hint = explain_db_connect_error(exc, settings.async_database_url)
        if hint:
            raise DatabaseNetworkError(hint) from exc
        raise
    finally:
        await connectable.dispose()


def run_migrations_online():
    import asyncio

    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
