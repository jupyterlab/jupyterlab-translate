# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.
import itertools
import os
from pathlib import Path
from typing import Any

import polib
from hatchling.builders.hooks.plugin.interface import BuildHookInterface

from jupyterlab_translate.api import compile_po_file
from jupyterlab_translate.contributors import CONTRIBUTORS
from jupyterlab_translate.contributors import get_contributors_report


# Minimal percentage needed to compile a PO file
COMPILATION_THRESHOLD = 0


class JupyterLanguageBuildHook(BuildHookInterface):
    """Hatch build plugin to package Jupyter language pack."""

    PLUGIN_NAME = "jupyter-translate"

    def clean(self, versions: list[str]) -> None:
        """This occurs before the build process if the -c/--clean flag was
        passed to the build command, or when invoking the clean command.
        """

        package_folder = Path(self.root)
        python_folder = next(
            package_folder.glob("jupyterlab_language_pack_??_??"), None
        )
        if python_folder is None:
            self.app.display_error(
                f"Unable to get the Python folder name in {package_folder!s}"
            )
            return
        else:
            locale_name = python_folder.name[-5:]

        messages_folder = python_folder / "locale" / locale_name / "LC_MESSAGES"

        for bundle in itertools.chain(
            messages_folder.glob("*.json"), messages_folder.glob("*.mo")
        ):
            bundle.unlink()

    def initialize(self, version: str, build_data: dict[str, Any]) -> None:
        """This occurs immediately before each build.

        Any modifications to the build data will be seen by the build target.
        """

        package_folder = Path(self.root)
        python_folder = next(
            package_folder.glob("jupyterlab_language_pack_??_??"), None
        )
        if python_folder is None:
            self.app.display_error(
                f"Unable to get the Python folder name in {package_folder!s}"
            )
            return
        else:
            locale_name = python_folder.name[-5:]

        if self.target_name == "wheel":
            messages_folder = python_folder / "locale" / locale_name / "LC_MESSAGES"

            po_files = list(filter(lambda f: f.is_file(), messages_folder.glob("*.po")))
            for file in po_files:
                po = polib.pofile(str(file))
                percent_translated = po.percent_translated()

                if percent_translated >= COMPILATION_THRESHOLD:
                    self.app.display_info(
                        f"{locale_name} {file.stem} {percent_translated}% compiling...",
                    )
                    compile_po_file(file)
                else:
                    self.app.display_info(
                        f"{locale_name} {file.stem} {percent_translated}% < {COMPILATION_THRESHOLD}%",
                    )

            self.app.display_success("Language translation bundles generated.")
        else:
            CROWDIN_API_KEY = os.environ.get("CROWDIN_API_KEY")
            if CROWDIN_API_KEY is None:
                self.app.display_warning(
                    "Unable to update the contributors list as 'CROWDIN_API_KEY' env variable is not provided"
                )
            else:
                # Update the contributors file
                contributors = package_folder / CONTRIBUTORS
                content = get_contributors_report(
                    locale=locale_name.replace("_", "-"), crowdin_key=CROWDIN_API_KEY
                )
                contributors.write_text(content)

                self.app.display_success("Contributors list updated.")
