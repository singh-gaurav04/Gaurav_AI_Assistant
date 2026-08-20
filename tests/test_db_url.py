import socket

import pytest

from app.core.db_url import (
    DatabaseNetworkError,
    assert_database_host_reachable,
    build_connect_args,
    explain_db_connect_error,
    normalize_database_url,
    resolve_ssl_mode,
)


def test_normalize_postgres_scheme():
    assert normalize_database_url("postgres://u:p@h/db").startswith("postgresql+asyncpg://")


def test_ssl_off_for_docker_db_host():
    url = "postgresql+asyncpg://portfolio:portfolio@db:5432/portfolio"
    assert resolve_ssl_mode(url, "auto") is None
    assert build_connect_args(url, "auto") == {}


def test_supabase_direct_host_rejected():
    url = "postgresql+asyncpg://postgres:secret@db.abc123.supabase.co:5432/postgres"
    with pytest.raises(DatabaseNetworkError, match="Session pooler"):
        assert_database_host_reachable(url)


def test_explain_network_unreachable():
    url = "postgresql+asyncpg://u:p@db.abc123.supabase.co:5432/postgres"
    msg = explain_db_connect_error(OSError(101, "Network is unreachable"), url)
    assert msg is not None
    assert "pooler" in msg.lower()


def test_prefer_ipv4_when_available(monkeypatch):
    url = "postgresql+asyncpg://u:p@example.com:5432/postgres"

    def fake_getaddrinfo(host, port, family=0, type=0, proto=0, flags=0):
        if family == socket.AF_INET:
            return [(socket.AF_INET, socket.SOCK_STREAM, 0, "", ("93.184.216.34", port))]
        raise socket.gaierror("no v6")

    monkeypatch.setattr("app.core.db_url.socket.getaddrinfo", fake_getaddrinfo)
    args = build_connect_args(url, "require")
    assert args["host"] == "93.184.216.34"
    assert args["ssl"].check_hostname is False
