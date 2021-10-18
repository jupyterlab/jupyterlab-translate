# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.
"""
Constants
"""
from functools import partial
from itertools import chain
from typing import List


COOKIECUTTER_URL = "https://github.com/goanpeca/jupyterlab-language-pack-cookiecutter"
COOKIECUTTER_REF = "master"
EXTENSIONS_FOLDER = "extensions"
JUPYTERLAB = "jupyterlab"
LANG_PACKS_FOLDER = "language-packs"
LC_MESSAGES = "LC_MESSAGES"
LOCALE_FOLDER = "locale"
TRANSLATIONS_FOLDER = "translations"


def __build_parsers() -> List[dict]:

    roots = {"trans", "this.trans", "this._trans", "this.props.trans", "props.trans"}
    functions = [
        {"expression": "__", "arguments": {"text": 0}},
        {"expression": "gettext", "arguments": {"text": 0}},
        {"expression": "_n", "arguments": {"text": 0, "textPlural": 1}},
        {"expression": "ngettext", "arguments": {"text": 0, "textPlural": 1}},
        {"expression": "_p", "arguments": {"context": 0, "text": 1}},
        {"expression": "pgettext", "arguments": {"context": 0, "text": 1}},
        {"expression": "_np", "arguments": {"context": 0, "text": 1, "textPlural": 2}},
        {
            "expression": "npgettext",
            "arguments": {"context": 0, "text": 1, "textPlural": 2},
        },
    ]

    def build_parser(root: str, func: dict) -> dict:
        f = func.copy()
        f["expression"] = ".".join((root, f["expression"]))
        return f

    return list(chain(*[map(partial(build_parser, root), functions) for root in roots]))


GETTEXT_CONFIG = {
    "js": {
        "parsers": __build_parsers(),
        "glob": {
            "pattern": "**/*.ts*(x)",
            "options": {
                "ignore": "{examples/**/*.ts*(x),**/*.spec.ts,node_modules/**/*.ts*(x)}"
            },
        },
        "comments": {"otherLineLeading": True},
    },
    "headers": {"Language": ""},
    "output": None,
}
