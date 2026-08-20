"""Normalize Postgres URLs for asyncpg + Supabase (SSL / pooler)."""

from __future__ import annotations

from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse


def normalize_database_url(url: str) -> str:
    """Accept postgres:// or postgresql:// and force postgresql+asyncpg://."""
    value = (url or "").strip()
    if not value:
        raise ValueError("DATABASE_URL is empty")

    if value.startswith("postgres://"):
        value = "postgresql://" + value[len("postgres://") :]
    if value.startswith("postgresql://") and not value.startswith("postgresql+asyncpg://"):
        value = "postgresql+asyncpg://" + value[len("postgresql://") :]

    return value


def _host_is_local(hostname: str | None) -> bool:
    if not hostname:
        return True
    host = hostname.lower().strip()
    return host in {"localhost", "127.0.0.1", "::1", "db", "postgres"} or host.endswith(".local")


def _is_supabase_host(hostname: str | None) -> bool:
    if not hostname:
        return False
    host = hostname.lower()
    return "supabase.co" in host or "supabase.com" in host


def _is_transaction_pooler(hostname: str | None, port: int | None) -> bool:
    """Supabase transaction pooler typically uses port 6543."""
    if port == 6543:
        return True
    if hostname and "pooler" in hostname.lower() and port == 6543:
        return True
    return False


def resolve_ssl_mode(url: str, ssl_setting: str = "auto") -> str | None:
    """
    Return asyncpg ssl mode: 'require', True-equivalent, or None to skip.
    ssl_setting: auto | require | disable
    """
    mode = (ssl_setting or "auto").strip().lower()
    if mode in {"disable", "false", "0", "off"}:
        return None
    if mode in {"require", "true", "1", "on"}:
        return "require"

    # auto
    parsed = urlparse(url)
    if _host_is_local(parsed.hostname):
        return None
    if _is_supabase_host(parsed.hostname):
        return "require"
    # Remote non-local hosts (Render/Supabase/Neon/etc.) — prefer SSL
    return "require"


def build_connect_args(url: str, ssl_setting: str = "auto") -> dict:
    """SQLAlchemy create_async_engine connect_args for asyncpg."""
    parsed = urlparse(url)
    port = parsed.port
    args: dict = {}

    ssl_mode = resolve_ssl_mode(url, ssl_setting)
    if ssl_mode:
        # asyncpg accepts True or ssl.SSLContext; "require" works on recent asyncpg
        args["ssl"] = True

    if _is_transaction_pooler(parsed.hostname, port):
        # PgBouncer transaction mode does not support prepared statements
        args["statement_cache_size"] = 0

    return args


def ensure_ssl_query_param(url: str, ssl_setting: str = "auto") -> str:
    """Optionally add ssl=require to the URL for tools that read query params."""
    if not resolve_ssl_mode(url, ssl_setting):
        return url

    parsed = urlparse(url)
    query = dict(parse_qsl(parsed.query, keep_blank_values=True))
    if "ssl" not in query and "sslmode" not in query:
        query["ssl"] = "require"
    return urlunparse(parsed._replace(query=urlencode(query)))
