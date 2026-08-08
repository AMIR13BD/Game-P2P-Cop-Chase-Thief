"""The negotiated identity must advertise our public MCP address(es).

A peer that builds a pre-game declaration — sharNamr's Cop
(``p2p_cop_agent/protocol/declaration_groups.py`` @ e867eb4) — refuses a group whose
``mcp_servers`` is empty with ``group '<id>' must declare its MCP addresses``. The URL is
a RUNTIME value (Cloudflare quick-tunnel hostnames change), so it flows from
``--public-mcp-url`` through ``identity_for`` into the outgoing ``negotiate`` payload.
Omitting it keeps the prior empty shape, preserving the official reference and every
existing caller.
"""

import re

from thief_agent.interop import cli
from thief_agent.interop.friendly import FriendlyResult
from thief_agent.interop.negotiate import Negotiator
from thief_agent.interop.series import identity_for, mcp_servers_for
from thief_agent.interop.terms import default_terms

URL = "https://phrase-fisheries-fighters-calculations.trycloudflare.com/mcp"

# sharNamr's exact declaration guard, reproduced so this test fails if our payload would
# be refused: mcp_servers must be a non-empty mapping of role -> non-empty URL string
# carrying no embedded credential (declaration_groups.py `_CREDENTIAL_IN_URL`).
_CREDENTIAL_IN_URL = re.compile(
    r"://[^/@\s]+@|[?&][^=&]*(token|key|secret|password|passwd|auth)[^=&]*=", re.I
)


def _passes_sharnamr_declaration_guard(mcp_servers: object) -> bool:
    if not isinstance(mcp_servers, dict) or not mcp_servers:
        return False
    for url in mcp_servers.values():
        if not isinstance(url, str) or not url:
            return False
        if _CREDENTIAL_IN_URL.search(url):
            return False
    return True


def test_mcp_servers_for_builds_both_roles():
    assert mcp_servers_for(URL) == {"cop": URL, "thief": URL}


def test_mcp_servers_for_empty_when_unset():
    assert mcp_servers_for(None) == {}
    assert mcp_servers_for("") == {}


def test_identity_declares_mcp_servers_and_passes_peer_guard():
    ident = identity_for("amireman", mcp_servers=mcp_servers_for(URL))
    assert ident["mcp_servers"] == {"cop": URL, "thief": URL}
    assert _passes_sharnamr_declaration_guard(ident["mcp_servers"])


def test_outgoing_negotiate_payload_carries_mcp_address():
    ident = identity_for("amireman", mcp_servers=mcp_servers_for(URL))
    wire = Negotiator(default_terms(), ident, "amireman").signed("thief", 1).to_wire()
    assert wire["identity"]["mcp_servers"] == {"cop": URL, "thief": URL}
    assert _passes_sharnamr_declaration_guard(wire["identity"]["mcp_servers"])


def test_default_identity_stays_empty_backwards_compatible():
    # No URL configured => prior wire shape, which the official reference tolerates.
    wire = (
        Negotiator(default_terms(), identity_for("amireman"), "amireman")
        .signed("thief", 1)
        .to_wire()
    )
    assert wire["identity"]["mcp_servers"] == {}
    assert not _passes_sharnamr_declaration_guard(wire["identity"]["mcp_servers"])


def test_cli_exposes_public_mcp_url_and_forwards_it(monkeypatch):
    captured = {}

    def fake_run_friendly(**kwargs):
        captured.update(kwargs)
        return FriendlyResult(clean=True, summaries=[], result_doc={})

    monkeypatch.setattr(cli, "run_friendly", fake_run_friendly)
    rc = cli.main(["friendly", "--peer", "http://x/mcp", "--public-mcp-url", URL])
    assert rc == 0
    assert captured["public_mcp_url"] == URL


def test_cli_public_mcp_url_defaults_to_none(monkeypatch):
    captured = {}

    def fake_run_friendly(**kwargs):
        captured.update(kwargs)
        return FriendlyResult(clean=True, summaries=[], result_doc={})

    monkeypatch.setattr(cli, "run_friendly", fake_run_friendly)
    cli.main(["friendly", "--peer", "http://x/mcp"])
    assert captured["public_mcp_url"] is None
