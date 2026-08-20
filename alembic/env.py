from logging.config import fileConfig
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config
from alembic import context
from app.core.config import settings
from app.modules.shared.model import Base
import app.modules

config=context.config
config.set_main_option("sqlalchemy.url",settings.DATABASE_URL)
if config.config_file_name:
    fileConfig(config.config_file_name)
target_metadata=Base.metadata

def run_migrations_offline():
    context.configure(url=settings.DATABASE_URL,target_metadata=target_metadata,literal_binds=True,compare_type=True)
    with context.begin_transaction(): context.run_migrations()

async def run_async_migrations():
    connectable=async_engine_from_config(config.get_section(config.config_ini_section),prefix="sqlalchemy.",poolclass=pool.NullPool)
    async with connectable.connect() as connection:
        def do_migrations(conn):
            context.configure(connection=conn, target_metadata=target_metadata, compare_type=True)
            with context.begin_transaction():
                context.run_migrations()

        await connection.run_sync(do_migrations)
    await connectable.dispose()

def run_migrations_online():
    import asyncio
    asyncio.run(run_async_migrations())

if context.is_offline_mode(): run_migrations_offline()
else: run_migrations_online()
