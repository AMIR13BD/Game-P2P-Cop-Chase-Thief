"""P7+P18+P19 end-to-end gate: a real responder process + a real driver process play
a full networked six-sub-game series, emit artifacts, and pass the final mutual audit."""

import json
import socket
import subprocess
import sys
import time

from thief_agent.report import ids
from thief_agent.report.verify import verify_series
from thief_agent.security.signer import DevTestSigner

PORT, TOKEN, GID = 8813, "E2ETOKEN", "amireman-thief-vs-selfnet"


def _wait(port, t=40):
    end = time.time() + t
    while time.time() < end:
        try:
            with socket.create_connection(("127.0.0.1", port), 0.5):
                return True
        except OSError:
            time.sleep(0.3)
    return False


def test_e2e_networked_series(tmp_path):
    srv = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "thief_agent",
            "serve",
            "--port",
            str(PORT),
            "--token",
            TOKEN,
            "--group",
            "opponent",
        ]
    )
    try:
        assert _wait(PORT), "responder did not start"
        out = str(tmp_path / "art")
        run = subprocess.run(
            [
                sys.executable,
                "-m",
                "thief_agent",
                "netplay",
                "--opponent-url",
                f"http://127.0.0.1:{PORT}/mcp",
                "--token",
                TOKEN,
                "--out",
                out,
                "--game-id",
                GID,
                "--opponent",
                "opponent",
            ],
            capture_output=True,
            text=True,
            timeout=240,
        )
        assert run.returncode == 0, run.stdout + run.stderr
        assert (
            "role_sequence=['thief', 'police', 'thief', 'police', 'thief', 'police']" in run.stdout
        )
        assert "audit_passed=True" in run.stdout
        v = verify_series(out, GID, DevTestSigner())
        assert v["passed"], v["failures"]
        with open(f"{out}/{ids.result_name(GID)}", encoding="utf-8") as fh:
            res = json.load(fh)
        assert res["num_sub_games"] == 6 and len(res["sub_games"]) == 6
    finally:
        srv.terminate()
        try:
            srv.wait(10)
        except subprocess.TimeoutExpired:
            srv.kill()
