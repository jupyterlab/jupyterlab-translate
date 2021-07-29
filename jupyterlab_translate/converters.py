# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.
import ast
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

    nplurals_string = po.metadata["Plural-Forms"].split(";")[0]
    nplurals = ast.literal_eval(nplurals_string.replace("nplurals=", ""))
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

        if entry.msgstr:
            # result[key] = [None, entry.msgstr]
            result[key] = [entry.msgstr]
        elif entry.msgstr_plural:
            plural = [entry.msgid_plural]

            result[key] = plural
            ordered_plural = sorted(entry.msgstr_plural.items())

            for __, msgstr in ordered_plural:
                plural.append(msgstr)

            # If language has nplurals=1, then add the same translation
            if nplurals == 1:
                plural[0] = plural[-1]

    json_path.write_text(json.dumps(result, sort_keys=True, indent=4))

    return json_path
