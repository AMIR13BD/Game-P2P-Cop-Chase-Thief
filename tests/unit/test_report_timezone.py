"""The counted/official reporting artifacts declare the local (Haifa) timezone,
matching the reference result schema. Reporting/export only — no gameplay/scoring."""

from thief_agent.report.artifacts import build_declaration
from thief_agent.report.report_writer import build_result

TZ = "Asia/Jerusalem"


def test_counted_result_timezone_is_local():
    res = build_result("G", ["a", "b"], [], {"a": "x" * 40, "b": "y" * 40}, {})
    assert res["timezone"] == TZ


def test_counted_declaration_timezone_is_local():
    assert build_declaration("G", {})["timezone"] == TZ
