"""Normalize Postgres URLs for asyncpg + Supabase (SSL / pooler / IPv4)."""

from __future__ import annotations

import socket
import ssl
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

IPV6_UNREACHABLE_HINT = (
    "Database host is unreachable over the network (often IPv6-only DNS on an "
    "IPv4-only host). If you use Supabase, set DATABASE_URL to the Session "
    "pooler URI from Dashboard → Connect (host like "
    "aws-0-REGION.pooler.supabase.com, port 5432) — not db.PROJECT.supabase.co. "
    "For local Docker Compose, use postgresql+asyncpg://portfolio:portfolio@db:5432/portfolio."
)


class DatabaseNetworkError(ConnectionError):
    """Raised when the DB host cannot be reached from this environment."""


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


def _is_supabase_direct_host(hostname: str | None) -> bool:
    """Direct db.<ref>.supabase.co hosts are IPv6-only without the IPv4 add-on."""
    if not hostname:
        return False
    host = hostname.lower().strip()
    return host.startswith("db.") and host.endswith(".supabase.co")


def _is_transaction_pooler(hostname: str | None, port: int | None) -> bool:
    """Supabase transaction pooler typically uses port 6543."""
    if port == 6543:
        return True
    if hostname and "pooler" in hostname.lower() and port == 6543:
        return True
    return False


def resolve_ssl_mode(url: str, ssl_setting: str = "auto") -> str | None:
    """
    Return libpq-style ssl mode for connect_args: require | verify-full | None.
    ssl_setting: auto | require | verify-full | disable
    """
    mode = (ssl_setting or "auto").strip().lower()
    if mode in {"disable", "false", "0", "off"}:
        return None
    if mode in {"verify-full", "verify_full", "full"}:
        return "verify-full"
    if mode in {"require", "true", "1", "on"}:
        return "require"

    # auto — match common cloud URIs (sslmode=require): encrypt, don't verify CA
    parsed = urlparse(url)
    if _host_is_local(parsed.hostname):
        return None
    return "require"


def _ssl_context_for_mode(mode: str) -> ssl.SSLContext | bool:
    """
    Map ssl mode to an asyncpg-compatible value.

    asyncpg's ssl=True uses verify-full. Supabase/Neon expect require
    (TLS on, no cert chain verification), which avoids CERTIFICATE_VERIFY_FAILED
    with pooler / intermediate self-signed chains.
    """
    if mode == "verify-full":
        return True
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    return ctx


def _resolve_ipv4(hostname: str | None, port: int | None = 5432) -> str | None:
    if not hostname or _host_is_local(hostname):
        return None
    # Already an IPv4 literal
    try:
        socket.inet_pton(socket.AF_INET, hostname)
        return hostname
    except OSError:
        pass
    try:
        infos = socket.getaddrinfo(
            hostname,
            port or 5432,
            family=socket.AF_INET,
            type=socket.SOCK_STREAM,
        )
    except socket.gaierror:
        return None
    if not infos:
        return None
    return infos[0][4][0]


def _has_ipv6_only(hostname: str | None, port: int | None = 5432) -> bool:
    if not hostname or _host_is_local(hostname):
        return False
    try:
        socket.inet_pton(socket.AF_INET6, hostname.strip("[]"))
        return True
    except OSError:
        pass
    has_v4 = _resolve_ipv4(hostname, port) is not None
    if has_v4:
        return False
    try:
        socket.getaddrinfo(
            hostname,
            port or 5432,
            family=socket.AF_INET6,
            type=socket.SOCK_STREAM,
        )
        return True
    except socket.gaierror:
        return False


def assert_database_host_reachable(url: str) -> None:
    """
    Fail fast with an actionable message for IPv6-only / Supabase direct hosts.
    Call before opening a connection (migrations, app startup).
    """
    parsed = urlparse(normalize_database_url(url))
    host = parsed.hostname
    port = parsed.port or 5432
    if not host or _host_is_local(host):
        return

    if _is_supabase_direct_host(host):
        raise DatabaseNetworkError(
            f"DATABASE_URL uses Supabase direct host '{host}', which is IPv6-only "
            f"on most plans. {IPV6_UNREACHABLE_HINT}"
        )

    if _has_ipv6_only(host, port):
        raise DatabaseNetworkError(
            f"DATABASE_URL host '{host}' resolves to IPv6 only, and this environment "
            f"cannot reach IPv6. {IPV6_UNREACHABLE_HINT}"
        )


def explain_db_connect_error(exc: BaseException, url: str = "") -> str | None:
    """Return a clearer message for classic unreachable / IPv6 failures."""
    text = f"{type(exc).__name__}: {exc}".lower()
    errno = getattr(exc, "errno", None)
    if errno in {101, 51} or "network is unreachable" in text or "no route to host" in text:
        host = urlparse(normalize_database_url(url)).hostname if url else None
        prefix = f"Cannot reach database host '{host}'. " if host else ""
        return prefix + IPV6_UNREACHABLE_HINT
    return None


def build_connect_args(url: str, ssl_setting: str = "auto") -> dict:
    """SQLAlchemy create_async_engine connect_args for asyncpg."""
    parsed = urlparse(url)
    port = parsed.port or 5432
    hostname = parsed.hostname
    args: dict = {}

    # Prefer IPv4 so dual-stack hosts do not fail on broken IPv6 routes.
    ipv4 = _resolve_ipv4(hostname, port)
    using_ip = bool(ipv4 and hostname and ipv4 != hostname)
    if using_ip:
        args["host"] = ipv4

    ssl_mode = resolve_ssl_mode(url, ssl_setting)
    if ssl_mode:
        # Connecting by IP cannot use verify-full (SNI/hostname mismatch).
        if using_ip and ssl_mode == "verify-full":
            ssl_mode = "require"
        args["ssl"] = _ssl_context_for_mode(ssl_mode)

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
