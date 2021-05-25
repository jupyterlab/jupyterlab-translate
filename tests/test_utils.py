# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.
import json
import shutil
from pathlib import Path

import pytest

from jupyterlab_translate.utils import extract_schema_strings


HERE = Path(__file__).parent.resolve()


def test_extract_schema_strings(tmp_path):
    # Given
    extension_path = tmp_path / "extension"

    shutil.copytree(HERE / "data" / "testext", extension_path)

    # When
    trans = extract_schema_strings(str(extension_path))

    assert len(trans) == 9
    assert trans == [
        {
            "msgctxt": "schema",
            "msgid": "CodeMirror",
            "occurrences": [("/schema/schema.json", "21")],
        },
        {
            "msgctxt": "schema",
            "msgid": "Text editor settings for all CodeMirror editors.",
            "occurrences": [("/schema/schema.json", "22")],
        },
        {
            "msgctxt": "schema",
            "msgid": "Theme",
            "occurrences": [("/schema/schema.json", "32")],
        },
        {
            "msgctxt": "schema",
            "msgid": "CSS file defining the corresponding</br/>.cm-s-[name] styles is loaded",
            "occurrences": [("/schema/schema.json", "33")],
        },
        {
            "msgctxt": "schema",
            "msgid": "CodeMirror",
            "occurrences": [("/schema/schema.json", "3")],
        },
        {
            "msgctxt": "schema",
            "msgid": "Text Editor Syntax Highlighting",
            "occurrences": [("/schema/schema.json", "13")],
        },
        {
            "msgctxt": "schema",
            "msgid": "Key Map",
            "occurrences": [("/schema/schema.json", "26")],
        },
        {
            "msgctxt": "schema",
            "msgid": "Configures the keymap to use",
            "occurrences": [("/schema/schema.json", "27")],
        },
        {
            "msgctxt": "schema",
            "msgid": "Translated string",
            "occurrences": [("/schema/schema.json", "38")],
        },
    ]


def test_extract_schema_strings_jinja2_error(tmp_path):
    # Given
    extension_path = tmp_path / "extension"

    shutil.copytree(HERE / "data" / "testext", extension_path)

    ## Introduce format
    schema_file = extension_path / "schema" / "schema.json"
    schema = json.loads(schema_file.read_bytes())
    schema["title"] = r"{{ _('Hello, %(user)s!', user='w') }}"
    schema_file.write_text(json.dumps(schema, indent=2))

    # When
    with pytest.raises(ValueError, match=r'Got "\(\'Hello, %\(user\)s!\', None\)" line 21'):
        extract_schema_strings(str(extension_path))