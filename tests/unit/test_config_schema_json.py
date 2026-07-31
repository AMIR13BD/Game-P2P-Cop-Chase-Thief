"""FR-ARTIFACT-01: the config artifact conforms to schemas/config.schema.json."""

import json
import pathlib

import jsonschema

from thief_agent.report.artifacts import build_config
from thief_agent.shared.defaults import DEFAULT_GAME_CONFIG


def test_config_artifact_conforms_to_json_schema():
    schema_path = pathlib.Path(__file__).resolve().parents[2] / "schemas" / "config.schema.json"
    with open(schema_path, encoding="utf-8") as fh:
        schema = json.load(fh)
    art = build_config("gid", 1, {**DEFAULT_GAME_CONFIG, "agreed_between": ["a", "b"]})
    jsonschema.validate(art, schema)  # raises jsonschema.ValidationError if non-conformant
