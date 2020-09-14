# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.
"""
Command line interface.
"""
import click

from .api import compile_language_pack
from .api import compile_package
from .api import extract_language_pack
from .api import extract_package
from .api import update_language_pack
from .api import update_package

# --- Common arguments
# ----------------------------------------------------------------------------
lang_packs_repo_dir_arg = click.argument(
    "language_packs_repo_dir", type=click.Path(exists=True)
)
package_repo_dir_arg = click.argument("package_repo_dir", type=click.Path(exists=True))
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


# Rinse and repeat
# Not working!!! :-p
# jlab-trans extract-pack ~/develop/quansight/jupyterlab ~/develop/quansight/language-packs jupyterlab
# jlab-trans update-pack ~/develop/quansight/jupyterlab ~/develop/quansight/jupyterlab-language-packs jupyterlab -l es
# jlab-trans compile-pack ~/develop/quansight/jupyterlab-language-packs jupyterlab -l es

# Jupyterlab example language packs
# jlab-trans update-pack ~/develop/quansight/jupyterlab ~/develop/quansight/jupyterlab-language-packs jupyterlab -l es
# jlab-trans compile-pack ~/develop/quansight/language-packs jupyterlab -l zh_CN
# jlab-trans update-pack ~/develop/quansight/jupyterlab ~/develop/quansight/jupyterlab-language-packs jupyterlab -l pt_BR
# jlab-trans update-pack ~/develop/quansight/jupyterlab ~/develop/quansight/jupyterlab-language-packs jupyterlab -l fr
# jlab-trans compile-pack ~/develop/quansight/jupyterlab-language-packs jupyterlab -l fr
# jlab-trans compile-pack ~/develop/quansight/jupyterlab-language-packs jupyterlab -l pt_BR

# Extension example language packs
# jlab-trans update-pack ~/develop/quansight/jupyterlab-git ~/develop/quansight/jupyterlab-language-packs jupyterlab_git -l es
# jlab-trans compile-pack ~/develop/quansight/jupyterlab-git jupyterlab_git -l es

# Extension example stand alone package
# jlab-trans update ~/develop/quansight/jupyterlab-git jupyterlab_git -l es
# jlab-trans compile ~/develop/quansight/jupyterlab-git jupyterlab_git -l es
