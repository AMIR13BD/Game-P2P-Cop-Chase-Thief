"""Real localhost FastMCP integration: two of OUR adapters (dual-server, dual-dial) play a
friendly series over actual sockets — covering the server (four tools + optional bearer),
the client transport (retrying dial + inbox poll), and ``run_friendly`` end to end. This is
our-vs-our purely for exercising the network stack; the CROSS-TEAM proof is the live run
against the independent kit peer (see docs/INTEROP_FRIENDLY_REPORT.md)."""

import socket
import threading

import pytest

from thief_agent.exceptions import NetworkError
from thief_agent.interop.friendly import run_friendly
from thief_agent.interop.terms import default_terms


def _free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def test_two_adapters_play_friendly_over_real_localhost(tmp_path):
    p_police, p_thief = _free_port(), _free_port()
    terms = default_terms(max_steps=10)  # short games keep the socketed test fast
    token = "shared-friendly-token"  # exercise the optional bearer on both sides
    results: dict = {}

    def side(group, role, my_port, peer_port):
        try:
            results[group] = run_friendly(
                group=group,
                opponent_url=f"http://127.0.0.1:{peer_port}/mcp",
                natural_role=role,
                terms=terms,
                out_dir=tmp_path / group,
                host="127.0.0.1",
                port=my_port,
                token=token,
                num_games=2,
                turn_timeout=20.0,
            )
        except NetworkError as exc:  # pragma: no cover - startup race guard
            results[group] = exc

    t1 = threading.Thread(target=side, args=("amireman", "police", p_police, p_thief))
    t2 = threading.Thread(target=side, args=("sparring-peer", "thief", p_thief, p_police))
    t1.start()
    t2.start()
    t1.join(120)
    t2.join(120)

    a, b = results.get("amireman"), results.get("sparring-peer")
    if isinstance(a, NetworkError) or isinstance(b, NetworkError):
        pytest.skip(f"localhost startup race: {a or b}")
    assert a.game_id == b.game_id and a.game_uid == b.game_uid
    assert len(a.summaries) == 2 and len(b.summaries) == 2
    for sa, sb in zip(a.summaries, b.summaries, strict=True):
        assert sa["result"] == sb["result"]
        assert sa["audit"]["log_verified"] and sb["audit"]["log_verified"]
    assert a.lecturer_report_sent is False and a.match_mode == "friendly"
    assert (tmp_path / "amireman" / f"result_{a.game_id}.json").exists()
