# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.
import json
import os

import pkg_resources

from .utils import check_locale


JUPYTERLAB_LANGUAGEPACK_ENTRY = "jupyterlab.languagepack"
JUPYTERLAB_LOCALE_ENTRY = "jupyterlab.locale"


def merge_data():
    """
    Merge language pack data with locale data bundled in packages.
    """


def get_installed_packages_locale(locale: str) -> dict:
    """
    Get all jupyterlab extensions installed that contain locale data.

    Returns
    -------
    dict
        Ordered list of available language packs.
        >>>{"package-name": locale_data, ...}

    Examples
    --------
    - `entry_points={"jupyterlab.locale": "package-name = package_module"}`
    - `entry_points={"jupyterlab.locale": "jupyterlab-git = jupyterlab_git"}`
    """
    packages_locale_data = {}
    for entry_point in pkg_resources.iter_entry_points(JUPYTERLAB_LOCALE_ENTRY):
        name = entry_point.name.replace("-", "_").lower()
        locales = []
        try:
            package_root_path = os.path.dirname(entry_point.load().__file__)
            locale_path = os.path.join(package_root_path, "locale")
            locales = [loc for loc in os.listdir(locales) if os.path.isdir(loc)]
        except Exception as e:
            print(e)
            continue

        data = {}
        if locale in locales:
            locale_json_path = os.path.join(
                locale_path, locale, "LC_MESSAGES", "{name}.json".format(name=name)
            )
            if os.path.isfile(locale_json_path):
                with open(locale_json_path, "r") as fh:
                    data[locale] = json.loads(fh)

        if data:
            packages_locale_data[name] = data

    return packages_locale_data


def get_installed_language_packs() -> list:
    """
    Get all installed language packs.

    Returns
    -------
    list
        Ordered list of available language packs.
    """
    return [
        entry_point.name
        for entry_point in pkg_resources.iter_entry_points(
            JUPYTERLAB_LANGUAGEPACK_ENTRY
        )
    ]


def get_language_pack(locale: str) -> dict:
    """
    Get a language pack for a given `locale`.

    Returns
    -------
    dict
        Dictionary with language pack information in Jed format.
    """
    if check_locale(locale):
        for entry_point in pkg_resources.iter_entry_points(
            JUPYTERLAB_LANGUAGEPACK_ENTRY
        ):
            if locale == entry_point.name:
                return entry_point.load()
        else:
            return {}
    else:
        print("Locale '{locale}' not valid!".format(locale=locale))
        return {}


if __name__ == "__main__":
    print(get_installed_language_packs())
    print(get_language_pack("es"))
