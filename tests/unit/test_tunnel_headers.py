"""Optional public-tunnel headers (PT_TUNNEL_HEADERS): supply a provider warning-bypass
header (e.g. Localtonet's 'localtonet-skip-warning: true') to the FastMCP HTTP transport
without hardcoding a host, weakening bearer auth, or changing default behavior. The header
is opt-in via env only, so ngrok/localhost opponents are unaffected."""

import pytest

from thief_agent.exceptions import ConfigError
from thief_agent.infra.tunnel import tunnel_headers
from thief_agent.peer.net_driver import default_connect


def _headers(monkeypatch, url="https://x.example/mcp", token="TOK"):
    monkeypatch.delenv("PT_TUNNEL_HEADERS", raising=False)
    return default_connect(url, token).transport.headers


def test_no_env_is_unchanged_default_behavior(monkeypatch):
    assert tunnel_headers({}) == {}
    assert _headers(monkeypatch) == {"Authorization": "Bearer TOK"}  # bearer only, unchanged


def test_configured_header_is_attached_with_bearer(monkeypatch):
    monkeypatch.setenv("PT_TUNNEL_HEADERS", "localtonet-skip-warning: true")
    h = default_connect("https://fczkntxaua.localto.net/mcp", "TOK").transport.headers
    assert h["localtonet-skip-warning"] == "true"  # attached to the transport
    assert h["Authorization"] == "Bearer TOK"  # bearer auth still present


def test_multiple_headers_newline_and_semicolon():
    hs = tunnel_headers({"PT_TUNNEL_HEADERS": "a-b: 1\n c-d: 2 ; e-f: 3"})
    assert hs == {"a-b": "1", "c-d": "2", "e-f": "3"}


def test_value_may_contain_colon():
    assert tunnel_headers({"PT_TUNNEL_HEADERS": "x-url: https://h/p"}) == {"x-url": "https://h/p"}


def test_localhost_and_ordinary_public_still_work(monkeypatch):
    assert _headers(monkeypatch, "http://127.0.0.1:8813/mcp") == {"Authorization": "Bearer TOK"}
    assert _headers(monkeypatch, "https://foo.ngrok-free.dev/mcp") == {
        "Authorization": "Bearer TOK"
    }


def test_authorization_override_is_rejected():
    with pytest.raises(ConfigError):
        tunnel_headers({"PT_TUNNEL_HEADERS": "Authorization: Bearer EVIL"})
    with pytest.raises(ConfigError):
        tunnel_headers({"PT_TUNNEL_HEADERS": "authorization: x"})  # case-insensitive


def test_malformed_config_is_rejected():
    for bad in ("no-colon-here", "bad name: v", ": emptyname", "x-y:   "):
        with pytest.raises(ConfigError):
            tunnel_headers({"PT_TUNNEL_HEADERS": bad})


def test_control_char_injection_rejected():
    with pytest.raises(ConfigError):
        tunnel_headers({"PT_TUNNEL_HEADERS": "x-y: a\rb"})
