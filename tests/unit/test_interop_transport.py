"""Transport / tunnel-independence for the interop client: the wire is provider-neutral.
No extra header by default; an OPTIONAL Localtonet bypass header applies when configured;
bearer Authorization is preserved SIMULTANEOUSLY and can never be overridden by a tunnel
header. Proves the protocol is identical across Localtonet<->ngrok and Localtonet<->Localtonet."""

import pytest

from thief_agent.exceptions import ConfigError
from thief_agent.interop.client import McpTransport
from thief_agent.interop.server import PeerInboxes


def _headers(token=None, env=None):
    return McpTransport("http://opp/mcp", PeerInboxes(), token=token, env=env)._headers


def test_no_token_no_tunnel_header_is_empty():
    assert _headers(token=None, env={}) == {}


def test_optional_localtonet_header_applies_when_configured():
    h = _headers(token=None, env={"PT_TUNNEL_HEADERS": "localtonet-skip-warning: true"})
    assert h == {"localtonet-skip-warning": "true"}  # no Authorization on a no-auth peer


def test_bearer_and_tunnel_header_coexist():
    h = _headers(token="secret-token", env={"PT_TUNNEL_HEADERS": "localtonet-skip-warning: true"})
    assert h["localtonet-skip-warning"] == "true"
    assert h["Authorization"] == "Bearer secret-token"  # preserved simultaneously


def test_bearer_only_for_ngrok_style_peer_needs_no_header():
    # opponent on ngrok: no special header unless their endpoint requires one
    assert _headers(token="t", env={}) == {"Authorization": "Bearer t"}


def test_tunnel_header_cannot_override_authorization():
    with pytest.raises(ConfigError):
        _headers(token="t", env={"PT_TUNNEL_HEADERS": "Authorization: Bearer evil"})
