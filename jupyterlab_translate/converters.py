# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.
import json
from pathlib import Path

import polib


def convert_catalog_to_json(po_path: Path, output_dir: Path, project: str) -> Path:
    """
    Convert the `.po` format to Jed json format merging any existing json files.

    Args:
        po_path: PO file path
        output_dir: output directory
        project: project name

    Returns:
        JSON file path
    """
    json_name = po_path.with_suffix(".json").name
    json_path = output_dir / json_name

    # Do not add column wrapping by using a large value!
    po = polib.pofile(str(po_path), wrapwidth=100000)

    # Add metadata
    result = {
        "": {
            "domain": project,
            "version": po.metadata["Project-Id-Version"].split(" ")[-1],
            "language": po.metadata["Language"].replace("_", "-"),
            "plural_forms": po.metadata["Plural-Forms"],
        }
    }

    # Load existing file in case some old strings need to remain
    if json_path.is_file():
        data = json.loads(json_path.read_text())

        data.pop("")  # Remove old metadata
        result.update(data)

    for entry in po:
        if entry.obsolete:
            continue

        if entry.msgctxt:
            key = "{0}\x04{1}".format(entry.msgctxt, entry.msgid)
        else:
            key = entry.msgid

        if entry.msgstr:  # will skip if no translation is available
            result[key] = [entry.msgstr]
        elif entry.msgid_plural and entry.msgstr_plural:
            plural = [v for _, v in sorted(entry.msgstr_plural.items()) if v]
            # If any plural form is not empty
            if any(plural):
                result[key] = plural
                if len(plural) == 1:
                    # We need to add a dummy element as JupyterLab checks
                    # there are multiple plural strings for the value to be valid
                    # But some languages don't have plural form.
                    plural.append("")

    json_path.write_text(json.dumps(result, sort_keys=True, indent=4))

    return json_path
