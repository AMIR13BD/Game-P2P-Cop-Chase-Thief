"""Fixtures for the counted netplay official-email test: a FULL internal counted result
(with our audit-only extras) plus a FakeSDK that writes it, and the reference key sets."""

import json
import os

from thief_agent.report import ids

G1, G2 = "amireman", "uoh-ay26"

TOP = {
    "final_result",
    "game_id",
    "game_uid",
    "groups",
    "links",
    "mutual_agreement",
    "num_sub_games",
    "report_type",
    "schema_version",
    "sub_games",
    "timezone",
}
LINKS = {"config", "declaration", "github", "log", "result"}
MA = {"confirmed", "sha256"}
SUB = {
    "audit",
    "ended_at",
    "github_commit",
    "log_files",
    "result",
    "roles",
    "score",
    "started_at",
    "steps",
    "sub_game_number",
    "tie",
    "tokens",
    "winner_group",
}

# A full internal counted result as a compact JSON template (kept on single lines so it is
# not exploded by the formatter). {G}=game id, {M}=mutual_agreement mode.
_SUB = (
    '{{"sub_game_number":{n},"roles":{{"amireman":"thief","uoh-ay26":"police"}},'
    '"result":"capture","winner_group":"uoh-ay26","tie":false,'
    '"github_commit":{{"amireman":"aaaa","uoh-ay26":"bbbb"}},"tokens":{{"amireman":0,"uoh-ay26":0}},'
    '"score":{{"amireman":5,"uoh-ay26":20}},'
    '"log_files":{{"amireman":"log_{G}_g0{n}.json","uoh-ay26":"log_{G}_g0{n}.json"}},'
    '"config_sha256":"c","log_sha256":"l","audit":{{"log_verified":true,"tampered":false}}}}'
)
_FULL = (
    '{{"schema_version":"1.2","report_type":"final_game_result","game_id":"{G}","game_uid":"u",'
    '"links":{{"declaration":"declaration_{G}.json","config":"config_{G}_g<NN>.json",'
    '"log":"log_{G}_g<NN>.json","result":"result_{G}.json"}},"timezone":"Asia/Jerusalem",'
    '"groups":["amireman","uoh-ay26"],'
    '"repos":{{"amireman":{{"cop":"u","thief":"v"}},"uoh-ay26":{{"cop":"x","thief":"y"}}}},'
    '"num_sub_games":6,"sub_games":[{SUBS}],'
    '"final_result":{{"series_tie":false,"sub_games_won":{{"amireman":0,"uoh-ay26":6}},"ties":0,'
    '"tokens_total_series":{{"amireman":0,"uoh-ay26":0}},'
    '"total_score":{{"amireman":30,"uoh-ay26":120}},"winner_group":"uoh-ay26"}},'
    '"mutual_agreement":{{"confirmed":true,"sha256":"h","mode":"{M}",'
    '"confirmations":{{"p":{{"group":"amireman","final_sha256":"x"}},'
    '"t":{{"group":"uoh-ay26","final_sha256":"x"}}}},"signatures":{{}}}}}}'
)


def full_result(gid, mode="counted-two-peer"):
    subs = ",".join(_SUB.format(n=i + 1, G=gid) for i in range(6))
    return json.loads(_FULL.format(G=gid, SUBS=subs, M=mode))


class FakeSDK:
    def __init__(self, mode="counted-two-peer", m_pass=True):
        self._mode, self._m = mode, m_pass

    async def networked_series(self, url, token, cfg, seed, terms):
        return {
            "sub_games": [
                {"sub_game": i + 1, "steps": 10 + i, "outcome": "capture"} for i in range(6)
            ],
            "role_sequence": [],
            "peer_commit": "b" * 40,
            "peer_ident": {},
        }

    def emit_and_verify(self, out, gid, opp, series, cfg, peer_commit=None, peer_ident=None):
        os.makedirs(out, exist_ok=True)
        with open(os.path.join(out, ids.result_name(gid)), "w", encoding="utf-8") as fh:
            json.dump(full_result(gid, self._mode), fh)  # emit_series writes the FULL result
        return {"passed": True, "failures": []}

    def verify_match(self, out, gid):
        return {"passed": self._m, "failures": []}
