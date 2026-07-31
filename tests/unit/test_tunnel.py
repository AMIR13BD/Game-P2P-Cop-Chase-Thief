"""P23 tunnel adapter: provider-neutral selection, endpoint validation, TLS
enforcement for public counted matches, localhost support, and BLOCKED-EXTERNAL when
no public URL is configured (never fabricated)."""

import pytest

from thief_agent.infra.tunnel import (
    ConfiguredTunnel,
    LocalTunnel,
    make_tunnel,
    validate_endpoint,
    validate_public_endpoint,
)


def test_validate_endpoint_format():
    assert validate_endpoint("http://127.0.0.1:8000/mcp") is True
    assert validate_endpoint("https://x.ngrok.app/mcp") is True
    assert validate_endpoint("ftp://x/mcp") is False
    assert validate_endpoint("notaurl") is False


def test_public_endpoint_requires_tls():
    validate_public_endpoint("http://127.0.0.1:8000/mcp")  # localhost http OK
    validate_public_endpoint("https://team.ngrok.app/mcp")  # public https OK
    with pytest.raises(ValueError, match="https"):
        validate_public_endpoint("http://team.ngrok.app/mcp")  # public http rejected
    with pytest.raises(ValueError, match="malformed"):
        validate_public_endpoint("garbage")


def test_local_tunnel():
    t = LocalTunnel("127.0.0.1", 9)
    assert t.public_url() == "http://127.0.0.1:9/mcp"
    assert t.healthy() is False  # nothing listening on port 9


def test_make_tunnel_local_default():
    t = make_tunnel({})
    assert isinstance(t, LocalTunnel) and t.public_url().startswith("http://127.0.0.1")


def test_make_tunnel_configured_url():
    t = make_tunnel({"provider": "ngrok", "url": "https://team.ngrok.app/mcp"})
    assert isinstance(t, ConfiguredTunnel)
    assert t.public_url() == "https://team.ngrok.app/mcp"


def test_make_tunnel_blocked_external_without_url(monkeypatch):
    monkeypatch.delenv("PT_TUNNEL_URL", raising=False)
    with pytest.raises(RuntimeError, match="BLOCKED-EXTERNAL"):
        make_tunnel({"provider": "ngrok"})


def test_make_tunnel_reads_env_url(monkeypatch):
    monkeypatch.setenv("PT_TUNNEL_URL", "https://env.example/mcp")
    t = make_tunnel({"provider": "localtonet"})
    assert t.public_url() == "https://env.example/mcp"
