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

    entries = {
        entry["msgid"]: entry
        for entry in _extract_schema_strings(schema, "example.json")
    }
    assert set(entries.keys()) == {
        "The configuration for all text editors.</br/>If `fontFamily`, `fontSize` or `lineHeight` are `null`,</br/>values from current theme are used.",
        "Text Editor Indentation",
        "Text Editor",
        "Editor",
        "Editor Configuration",
        "Text editor settings.",
        "Cursor blinking rate",
        "Half-period in milliseconds used for cursor blinking. The default blink rate is 530ms. By setting this to zero, blinking can be disabled. A negative value hides the cursor entirely.",
    }
    assert entries["Text Editor"]["occurrences"] == [("example.json", "/title")]
    assert entries["Text Editor"]["msgctxt"] == "schema"
    assert entries["Editor Configuration"]["occurrences"] == [
        ("example.json", "/properties/editorConfig/title")
    ]
    assert entries["Text Editor Indentation"]["msgctxt"] == "menu"
