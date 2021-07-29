# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.
"""
API interface.
"""
import os
import shutil
from pathlib import Path
from typing import List, Union

from .constants import EXTENSIONS_FOLDER, JUPYTERLAB, LANG_PACKS_FOLDER
from .converters import convert_catalog_to_json
from .utils import (
    check_locale,
    compile_to_mo,
    compile_translations,
    create_new_language_pack,
    extract_translations,
    update_translations,
)


def check_locales(locales: List[str]):
    """
    Check if a given list  of locale values is valid.

    Raises an exception if an invalid locale value is found.

    Args:
        locales: List of locales
    Raises:
        ValueError: if the local is not valid.
    """
    for locale in locales:
        if not check_locale(locale):
            raise ValueError(f"Invalid locale '{locale}'".format(locale=locale))


def normalize_project(project: str) -> str:
    """
    Normalize a project name

    Args:
        project: project name
    Returns:
        The normalized project name
    """
    return project.lower().replace("-", "_")


def extract_package(package_repo_dir, project):
    """
    FIXME:
    """
    raise NotImplementedError("extract_package")


def update_package(package_repo_dir, project, locales):
    """
    FIXME:
    """
    if locales:
        check_locales(locales)

    project = normalize_project(project)
    output_dir = os.path.join(package_repo_dir, project)

    if not os.path.isdir(output_dir):
        raise Exception(
            "Output dir `{output_dir}` not found!".format(output_dir=output_dir)
        )

    update_translations(package_repo_dir, output_dir, project, locales)


def compile_package(package_repo_dir, project, locales):
    """
    FIXME
    """
    if locales:
        check_locales(locales)

    project = normalize_project(project)
    output_dir = os.path.join(package_repo_dir, project)
    po_paths = compile_translations(output_dir, project, locales)
    for __, po_path in po_paths.items():
        output_path = os.path.dirname(po_path)
        convert_catalog_to_json(po_path, output_path, project)


def extract_language_pack(package_repo_dir, language_packs_repo_dir, project):
    """
    FIXME:
    """
    project = normalize_project(project)

    if project == JUPYTERLAB:
        output_dir = os.path.join(language_packs_repo_dir, project)
    else:
        output_dir = os.path.join(language_packs_repo_dir, EXTENSIONS_FOLDER, project)
        os.makedirs(output_dir, exist_ok=True)

    extract_translations(package_repo_dir, output_dir, project)


def update_language_pack(package_repo_dir, language_packs_repo_dir, project, locales):
    """
    FIXME
    """
    if locales:
        check_locales(locales)

    project = normalize_project(project)

    if project == JUPYTERLAB:
        output_dir = os.path.join(language_packs_repo_dir, project)
    else:
        output_dir = os.path.join(
            language_packs_repo_dir, "jupyterlab_extensions", project
        )
        os.makedirs(output_dir, exist_ok=True)

    update_translations(package_repo_dir, output_dir, project, locales)


def compile_language_pack(
    language_packs_repo_dir: Union[Path, str], project: str, locales: List[str]
) -> None:
    """
    FIXME:
    """
    language_packs_repo_dir = Path(language_packs_repo_dir)

    if locales:
        check_locales(locales)

    project = normalize_project(project)

    if project == JUPYTERLAB:
        output_dir = language_packs_repo_dir / project
    else:
        output_dir = language_packs_repo_dir / EXTENSIONS_FOLDER / project

    po_paths = compile_translations(output_dir, project, locales)
    for locale, po_path in po_paths.items():
        output_path = po_path.parent
        json_path = convert_catalog_to_json(po_path, output_path, project)
        mo_path = compile_to_mo(po_path)

        # Move to language pack folder
        language_packs_dir = language_packs_repo_dir / LANG_PACKS_FOLDER
        pkg_name = "jupyterlab-language-pack-{locale}".format(locale=locale).replace(
            "_", "-"
        )
        locale_language_pack_dir = (
            language_packs_dir / pkg_name / pkg_name.replace("-", "_")
        )

        # Check if it exists, otherwise create it
        if not locale_language_pack_dir.is_dir():
            create_new_language_pack(language_packs_dir, locale)

        if project == JUPYTERLAB:
            output_dir = locale_language_pack_dir
        else:
            output_dir = locale_language_pack_dir / EXTENSIONS_FOLDER

        shutil.rmtree(str(output_dir / mo_path.name), ignore_errors=True)
        shutil.rmtree(str(output_dir / json_path.name), ignore_errors=True)

        shutil.move(str(mo_path), str(output_dir / mo_path.name))
        shutil.move(str(json_path), str(output_dir / json_path.name))
