# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.
"""
Command line interface.
"""
import os
import sys
from pathlib import Path

import click

from .api import compile_language_pack
from .api import compile_package
from .api import extract_language_pack
from .api import extract_package
from .api import update_language_pack
from .api import update_package
from .contributors import CONTRIBUTORS
from .contributors import get_contributors_report

# --- Common arguments
# ----------------------------------------------------------------------------
lang_packs_repo_dir_arg = click.argument(
    "language_packs_repo_dir", type=click.Path(exists=True)
)
package_repo_dir_arg = click.argument(
    "package_repo_dir", type=click.Path(exists=True, path_type=Path)
)
project_arg = click.argument("project")


# --- Common options
# ----------------------------------------------------------------------------
locales_opt = click.option(
    "--locales", "-l", default=None, multiple=True, help="Locale languages to use"
)


@click.group(
    help=(
        "Jupyter Translate provides functionality to extract "
        "localizable strings from Jupyterlab extensions. "
        "Extensions can update the `jupyterlab-language-packs` repository "
        "or provide localization files in the extension package."
    )
)
def main():
    pass


# --- Localization for standalone packages
# ----------------------------------------------------------------------------
@main.command(
    help=("Extract localizable strings and create catalog for a Jupyterlab extension.")
)
@package_repo_dir_arg
@project_arg
def extract(package_repo_dir, project):
    click.echo("Updating for stand alone package")
    extract_package(package_repo_dir, project)


@main.command(
    help=("Update localizable strings in language catalogs for a Jupyterlab extension.")
)
@package_repo_dir_arg
@project_arg
@locales_opt
def update(package_repo_dir, project, locales):
    click.echo("Updating for stand alone package")
    update_package(package_repo_dir, project, locales)


@main.command(
    help=("Update contributors list for a language package from Crowdin report.")
)
@package_repo_dir_arg
def update_contributors(package_repo_dir):

    CROWDIN_API_KEY = os.environ.get("CROWDIN_API_KEY")

    if CROWDIN_API_KEY is None:
        click.echo(
            "Unable to update the contributors list as 'CROWDIN_API_KEY' env variable is not provided"
        )
        sys.exit(1)
    else:
        click.echo("Updating the contributors list.")
        package_folder = Path(package_repo_dir)
        python_folder = next(
            package_folder.glob("jupyterlab_language_pack_??_??"), None
        )
        if python_folder is None:
            click.echo(f"Unable to get the Python folder name in {package_folder!s}")
            sys.exit(1)
        else:
            locale_name = python_folder.name[-5:]
        contributors = package_repo_dir / CONTRIBUTORS
        content = get_contributors_report(
            locale=locale_name.replace("_", "-"), crowdin_key=CROWDIN_API_KEY
        )
        contributors.write_text(content)


@main.command(help=("Compile catalogs for a Jupyterlab extension."))
@package_repo_dir_arg
@project_arg
@locales_opt
def compile(package_repo_dir, project, locales):
    click.echo("Compiling for stand alone package")
    compile_package(package_repo_dir, project, locales)


# --- Localization for language packs
# ----------------------------------------------------------------------------
@main.command(
    help=(
        "Extract localizable strings and create catalog for a jupyterlab-language-pack."
    )
)
@package_repo_dir_arg
@lang_packs_repo_dir_arg
@project_arg
def extract_pack(package_repo_dir, language_packs_repo_dir, project):
    click.echo("Extracting for language pack")
    extract_language_pack(package_repo_dir, language_packs_repo_dir, project)


@main.command(
    help=(
        "Update localizable strings in language catalogs for a jupyterlab-language-pack."
    )
)
@package_repo_dir_arg
@lang_packs_repo_dir_arg
@project_arg
@locales_opt
def update_pack(package_repo_dir, language_packs_repo_dir, project, locales):
    click.echo("Updating for language pack")
    update_language_pack(package_repo_dir, language_packs_repo_dir, project, locales)


@main.command(help=("Compile catalogs for a jupyterlab-language-pack."))
@lang_packs_repo_dir_arg
@project_arg
@locales_opt
def compile_pack(language_packs_repo_dir, project, locales):
    click.echo("Compiling for Jupyterlab Language Pack")

    compile_language_pack(language_packs_repo_dir, project, locales)
