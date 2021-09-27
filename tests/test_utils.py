# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.
import json
import shutil
import subprocess
from pathlib import Path

import polib
import pytest

from jupyterlab_translate.utils import _extract_schema_strings
from jupyterlab_translate.utils import create_catalog


@pytest.fixture
def dummy_pkg(tmp_path):
    pkg_name = tmp_path / "dummy_pkg"
    shutil.copytree(Path(__file__).parent / pkg_name.name, pkg_name)

    yield pkg_name


@pytest.fixture
def updated_dummy_pkg(dummy_pkg):
    patch_file = Path(__file__).parent / dummy_pkg.with_suffix(".patch").name

    with patch_file.open() as f:
        subprocess.check_call(["patch", "-p1"], stdin=f, cwd=dummy_pkg.parent)

    yield dummy_pkg


def test_create_catalog_with_merge(updated_dummy_pkg):
    pot_file, _ = create_catalog(
        updated_dummy_pkg,
        updated_dummy_pkg / "locale",
        updated_dummy_pkg.name,
        "0.1.0",
        True,
    )
    pot = polib.pofile(str(pot_file), wrapwidth=100000, check_for_duplicates=False)

    assert len(pot) == 3
    assert list(map(lambda p: p.msgid, pot)) == [
        "Fit columns width",
        "Insert a column at the end",
        "Remove the last row",
    ]


def test_create_catalog_without_merge(updated_dummy_pkg):
    pot_file, _ = create_catalog(
        updated_dummy_pkg,
        updated_dummy_pkg / "locale",
        updated_dummy_pkg.name,
        "0.1.0",
        False,
    )
    pot = polib.pofile(str(pot_file), wrapwidth=100000, check_for_duplicates=False)

    assert len(pot) == 2
    assert list(map(lambda p: p.msgid, pot)) == [
        "Fit columns width",
        "Remove the last row",
    ]


def test_extract_from_settings():
    with open("tests/example.json") as f:
        data = f.read()

    schema = json.loads(data)

    entries = {
        entry["msgid"]: entry
        for entry in _extract_schema_strings(schema, "example.json")
    }
    assert set(entries.keys()) == {
        "The configuration for all text editors.\nIf `fontFamily`, `fontSize` or `lineHeight` are `null`,\nvalues from current theme are used.",
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
