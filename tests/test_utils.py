# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.
import json
from jupyterlab_translate.utils import _extract_schema_strings


def test_todo():
    assert True


def test_extract_from_settings():
    with open("tests/example.json") as f:
        data = f.read()
    lines = data.splitlines()
    schema = json.loads(data)

    entries = _extract_schema_strings(schema, lines, "example.json")
    strings = {entry["msgid"] for entry in entries}
    assert strings == {
        "The configuration for all text editors.</br/>If `fontFamily`, `fontSize` or `lineHeight` are `null`,</br/>values from current theme are used.",
        "Text Editor Indentation",
        "Text Editor",
        "Editor",
        "Editor Configuration",
        "Text editor settings.",
    }
