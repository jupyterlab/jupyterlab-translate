# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.
"""
"""
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from collections import OrderedDict
from itertools import chain
from pathlib import Path
from typing import Dict
from typing import List
from typing import Optional
from typing import Pattern
from typing import Set
from typing import Tuple
from typing import Union

import babel
import polib
from cookiecutter.main import cookiecutter

from .constants import COOKIECUTTER_REF
from .constants import COOKIECUTTER_URL
from .constants import GETTEXT_CONFIG
from .constants import LC_MESSAGES
from .constants import LOCALE_FOLDER

# Constants
HERE = Path(__file__).parent

# --- Helpers
# ----------------------------------------------------------------------------
def get_version(repo_root_path: Path, project: str) -> str:
    """
    Get the version of a language pack

    Args:
        repo_root_path: Path to the language pack
        project: Project name

    Returns:
        Version string for project
    """
    package = repo_root_path / project

    version = ""
    # Look for python version
    try:
        output = (
            subprocess.check_output(
                [sys.executable, "setup.py", "--version"], cwd=repo_root_path
            )
            .decode("utf8")
            .strip()
        )
    except subprocess.CalledProcessError as e:
        print(f"Failed to get the Python package version for '{package!s}.")
        print(e)
    else:
        version = output.splitlines()[-1]

    # Look for npm version
    if not version:
        pkg_path = package / "package.json"

        if pkg_path.is_file():
            data = json.loads(pkg_path.read_text())
            version = data.get("version", "")

    # Look for git version
    if not version and repo_root_path.exists():
        args = ["git", "describe", "--tags", "--abbrev=0"]
        try:
            version = (
                subprocess.check_output(args, cwd=repo_root_path)
                .decode("utf-8")
                .strip()
            )
            if version.startswith("v"):
                version = version[1:]
        except Exception:
            pass

    return version


def create_new_language_pack(
    output_dir: Union[str, Path],
    locale: str,
    cookiecutter_url: str = COOKIECUTTER_URL,
    cookiecutter_ref: str = COOKIECUTTER_REF,
    version: str = "0.1.post0",
) -> None:
    """
    Creates a new language pack python package with cookiecutter.

    Args:
        output_dir: Ouput directory for the language pack
        locale: Locale
        cookiecutter_url: Language pack template
        cookiecutter_ref: Template git reference
    """
    if not check_locale(locale):
        raise Exception("Invalid locale!")

    loc = babel.Locale.parse(locale)
    options = {
        "locale": locale.replace("_", "-"),
        "locale_underscore": locale,
        "language": loc.english_name,
        "version": version,
    }
    cookiecutter(
        cookiecutter_url,
        checkout=cookiecutter_ref,
        extra_context=options,
        no_input=True,
        output_dir=str(output_dir),
    )


def check_locale(locale: str) -> bool:
    """Check if a locale is a valid value."""
    value = False
    try:
        babel.Locale.parse(locale)
        value = True
    except Exception as e:
        print(str(e))

    return value


def find_locales(output_dir: Path) -> Tuple[str]:
    """
    Find available locales on the `output_dir` folder.

    Args:
        output_dir: Output folder

    Returns:
        Sorted locales found in the Jupyter language packs repository.
    """
    locales = set()
    locale_path = output_dir / LOCALE_FOLDER
    folders = locale_path.iterdir() if locale_path.is_dir() else []
    for locale_folder in folders:
        locale_name = locale_folder.name
        if locale_name not in locales and check_locale(locale_name):
            locales.add(locale_name)

    return tuple(sorted(locales))


# --- Find source files
# ----------------------------------------------------------------------------
def find_packages_source_files(
    packages_path: Union[str, Path]
) -> Dict[str, List[Path]]:
    """
    List packages source files.

    Args:
        packages_path: Path to the packages root directory

    Returns:
        Mapping (package name, source files list)
    """
    package_files = OrderedDict()
    for pkg in Path(packages_path).iterdir():
        files = find_source_files(pkg)
        if files:
            package_files[pkg.name] = files

    return package_files


def find_source_files(
    path: Path,
    extensions: Set[str] = {".ts", ".tsx", ".py"},
    skip_folders: Set[str] = {
        "tests",
        "test",
        "node_modules",
        "lib",
        ".git",
        ".ipynb_checkpoints",
    },
):
    """
    Find source files in given `path`.

    Args:
        path: Path to introspect
        extensions: Set of extensions to list
        skip_folders: Set of folders to ignore

    Returns
        List of files found
    """
    all_files = []
    for ext in extensions:
        for f in path.rglob(f"*{ext}"):
            parents = set(map(lambda p: p.name, f.parents))
            if len(parents.intersection(skip_folders)) > 0:
                continue

            all_files.append(f)

    return all_files


# --- .pot and .po generation
# ----------------------------------------------------------------------------
def extract_tsx_strings(input_path: Union[str, Path]) -> List[Dict]:
    """
    Use gettext-extract to extract strings from TS(X) files.

    Args:
        input_path: path to look for strings.

    Returns:
        List of translatable strings
    """
    input_path = Path(input_path).expanduser()

    with tempfile.NamedTemporaryFile("w+", suffix=".pot") as output:
        config = GETTEXT_CONFIG.copy()
        config["output"] = output.name

        with tempfile.NamedTemporaryFile("w+", suffix=".json") as config_file:
            json.dump(config, config_file)
            config_file.seek(0)  # Rewind to file beginning

            subprocess.run(["cat", config_file.name])
            cmd = ["gettext-extract", "--config", config_file.name]
            subprocess.check_call(cmd, cwd=input_path)

        # Fix the missing format
        output_path = Path(output.name)
        output_path.write_text("#, fuzzy\n" + output_path.read_text())

        entries = []
        pot = polib.pofile(str(output_path), wrapwidth=100000)
        for entry in pot:
            occurrences = entry.occurrences

            data = {"msgid": entry.msgid, "occurrences": occurrences}

            if entry.msgid_plural:
                data["msgid_plural"] = entry.msgid_plural
                data["msgstr_plural"] = entry.msgstr_plural

            if entry.msgctxt:
                data["msgctxt"] = entry.msgctxt

            if entry.comment:
                data["comment"] = entry.comment

            if entry.encoding:
                data["encoding"] = entry.encoding

            if entry.obsolete:
                data["obsolete"] = entry.obsolete

            entries.append(data)

    return entries


def get_line(lines: List[str], value: str) -> str:
    """Get the line position of the last ``value`` occurrence in ``lines``.

    Args:
        lines: Lines to inspect
        value: Value searched for
    Returns:
        Position of ``value`` converted to string
    """
    value1 = '"' + value + '"'
    value2 = "'" + value + "'"
    line_count = 0
    for idx, line in enumerate(lines):
        # TODO: Might be needed for other escaped chars?
        line = line.replace(r"\n", "\n")
        if value1 in line or value2 in line:
            line_count = idx + 1

    return str(line_count)


_default_schema_context = "schema"
_default_settings_context = "settings"

# mapping of selector to translation context
DEFAULT_SCHEMA_SELECTORS = {
    "title": _default_schema_context,
    "description": _default_schema_context,
    "properties/.*/title": _default_settings_context,
    "properties/.*/description": _default_settings_context,
    "definitions/.*/properties/.*/title": _default_settings_context,
    "definitions/.*/properties/.*/description": _default_settings_context,
    # JupyterLab-specific
    "jupyter\.lab\.setting-icon-label": _default_settings_context,
    "jupyter\.lab\.menus/.*/label": "menu",
    "jupyter\.lab\.toolbars/.*/label": "toolbar",
}


def _prepare_schema_patterns(schema: dict) -> Dict[Pattern, str]:
    selectors = {
        **DEFAULT_SCHEMA_SELECTORS,
        **{
            selector: _default_schema_context
            for selector in schema.get("jupyter.lab.internationalization", {}).get(
                "selectors", []
            )
        },
    }
    return {
        re.compile("^/" + pattern + "$"): context
        for pattern, context in selectors.items()
    }


def _extract_schema_strings(
    schema: dict,
    ref_path: str,
    prefix: str = "",
    to_translate: Dict[Pattern, str] = None,
):
    if to_translate is None:
        to_translate = _prepare_schema_patterns(schema)

    entries = []

    for key, value in schema.items():
        path = prefix + "/" + key

        if isinstance(value, str):
            matched = False
            for pattern, context in to_translate.items():
                if pattern.fullmatch(path):
                    matched = True
                    break
            if matched:
                entries.append(
                    dict(
                        msgctxt=context,
                        msgid=value,
                        occurrences=[(ref_path, path)],
                    )
                )
        elif isinstance(value, dict):
            entries.extend(
                _extract_schema_strings(
                    value, ref_path, prefix=path, to_translate=to_translate
                )
            )
        elif isinstance(value, list):
            for i, element in enumerate(value):
                if not isinstance(element, dict):
                    continue
                entries.extend(
                    _extract_schema_strings(
                        element,
                        ref_path,
                        prefix=path + "[" + str(i) + "]",
                        to_translate=to_translate,
                    )
                )
    return entries


def extract_schema_strings(input_path: Union[str, Path]) -> List[Dict]:
    """
    Use gettext-extract to extract strings from JSON schema files.
    Args:
        input_path:
    Returns
        List of translatable strings
    """
    input_paths = find_source_files(Path(input_path), extensions=("package.json",))
    schema_paths: List[Path] = []

    for path in input_paths:
        if path.is_file():
            data = json.loads(path.read_text())

            schema_dir = data.get("jupyterlab", {}).get("schemaDir", None)
            if schema_dir is not None:
                schema_path = path.parent / schema_dir
                if schema_path.is_dir():
                    for p in schema_path.rglob("*.json"):
                        schema_paths.append(p)

    entries = []
    for path in schema_paths:
        if path.is_file():
            data = path.read_text()
            schema = json.loads(data)
            ref_path = "/{!s}".format(path.relative_to(input_path))
            entries.extend(_extract_schema_strings(schema, ref_path))

    return entries


def extract_strings(
    input_paths: List[Path], output_path: Union[str, Path], project: str, version: str
) -> Path:
    """
    Extract localizable strings on input files.

    Args:
        input_paths: List of input folders
        output_path: Output folder relative to the current one
        project: Project name
        version: Version

    Returns
        Output path
    """
    mapping = HERE / "pybabel_config.cfg"
    cmd = [
        "pybabel",
        "extract",
        "--no-wrap",
        "--charset=utf-8",
        "-o",
        str(output_path),
        f"--project={project}",
        f"--version={version}",
        f"--mapping={mapping!s}",
    ] + list(str(i) for i in input_paths)

    subprocess.check_call(cmd)

    return Path.cwd() / output_path


def fix_location(
    path_to_remove: str,
    pot_path: Union[str, Path],
    append_entries: Optional[List[Dict]] = None,
) -> Dict[str, str]:
    """
    Remove any hardcoded paths on the pot file.

    Args:
        path: path to remove
        pot_file: pot file path
        append_entries: optional list of strings entries to append
    Returns:
        POT file metadata
    """
    # Do not add column wrapping by using a large value!
    pot = polib.pofile(str(pot_path), wrapwidth=100000, check_for_duplicates=False)

    for entry in pot:
        new_occurrences = []
        string_fpaths = []
        lines = []
        for (string_fpath, line) in entry.occurrences:
            # Convert absolute paths to relative paths
            string_fpaths.append(Path(string_fpath).resolve())
            lines.append(line)

            if line != "":
                string_fpath = " ".join(map(lambda p: str(p), string_fpaths)).replace(
                    path_to_remove, ""
                )

                # Normalize paths
                string_fpath = string_fpath.replace("\\", "/")

                new_occurrences.append((string_fpath, line))
                string_fpaths.clear()
                lines.clear()

        entry.occurrences = new_occurrences

    if append_entries:
        for entry in append_entries:
            entry = polib.POEntry(**entry)
            pot.append(entry)

    pot.save(str(pot_path))
    return pot.metadata.copy()


def remove_duplicates(pot_path: Path, metadata: Dict[str, str]) -> None:
    """
    Remove duplicate strings in POT file

    Args:
        pot_path: POT file path
        metadata: POT metadata
    """
    old_pot_name = pot_path.rename(f"{pot_path!s}.bak")

    pot = polib.pofile(str(old_pot_name), wrapwidth=100000, check_for_duplicates=False)

    entries = {}
    entries_data = {}
    duplicates = set()

    for entry in pot:
        # Remove empty msgid
        if not bool(entry.msgid):
            continue

        # Create a unique key using context, singular and plurals
        key = (entry.msgctxt, entry.msgid, entry.msgid_plural)
        if key in entries:
            entries[key].append(entry)
            duplicates.add(key)
        else:
            entry.occurrences = list(sorted(entry.occurrences))
            entries[key] = [entry]
            entries_data[key] = entry

    # Merge info from duplicate
    print("Merging duplicates...")
    for key in duplicates:
        items = entries[key]
        entry = entries_data[key]
        new_occurences = []
        for item in items:
            new_occurences.extend(item.occurrences)

        entry = polib.POEntry(
            msgid=entry.msgid,
            msgid_plural=entry.msgid_plural,
            msgctxt=entry.msgctxt,
            occurrences=list(sorted(new_occurences)),
        )

        entries[key] = [entry]

    po = polib.POFile(wrapwidth=100000)
    keys = [
        "Project-Id-Version",
        "MIME-Version",
        "Content-Type",
        "Content-Transfer-Encoding",
    ]
    new_metadata = {}
    for key in keys:
        new_metadata[key] = metadata[key]

    po.metadata = new_metadata
    for item in sorted(entries, key=lambda x: entries[x][0].occurrences):
        po.append(entries[item][0])

    po.save(str(pot_path))

    pot_path.write_text(pot_path.read_text())

    old_pot_name.unlink()


def create_catalog(
    repo_root_dir: Union[str, Path],
    locale_dir: Union[str, Path],
    project: str,
    version: str,
    merge: bool = True,
) -> Tuple[Path, Dict[str, str]]:
    """
    Create a catalog

    Args:
        repo_root_dir: Repository to extract translation from
        locale_dir: POT file folder
        project: project name
        version: version
        merge: Merge with existing POT file
    Returns:
        Tuple (POT file path, POT metadata)
    """
    pot_path = Path(locale_dir) / f"{project}.pot"
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        tmp_pot = tmp_path / f"{project}.pot"
        nested_files = find_packages_source_files(repo_root_dir)
        flat_files = list(chain(*nested_files.values()))
        extract_strings(flat_files, tmp_pot, project, version=version)
        append_entries = extract_tsx_strings(repo_root_dir) + extract_schema_strings(
            repo_root_dir
        )
        print("\nTotal entries: {}\n".format(len(append_entries)))
        metadata = fix_location(str(repo_root_dir), tmp_pot, append_entries)

        if merge and pot_path.exists():
            orig = tmp_path / "orig.pot"
            final_pot = tmp_path / "out.pot"
            shutil.copyfile(pot_path, orig)

            # Merge with existing
            subprocess.check_call(
                ["xgettext", str(orig), str(tmp_pot), "-s", "-o", str(final_pot)],
                cwd=tmp,
            )
        else:
            final_pot = tmp_pot

        shutil.copyfile(final_pot, pot_path)

    return pot_path, metadata


def update_catalogs(
    pot_path: Union[str, Path], output_dir: Union[str, Path], locale: str
):
    """
    Create new locale `.po` files or update and merge if they already exist.

    Args:
        pot_path: Path to `.pot` file.
        output_dir: Path to base output directory. The `.po` files will be placed in
            "{output_dir}/{locale}/LC_MESSAGES/{domain}.po".
            Domain will be inferred from the `pot_path`.
        locale: Locale
    """
    # Check if locale exists!
    if not check_locale(locale):
        return

    domain = Path(pot_path).stem
    po_path = f"{output_dir!s}/{locale}/LC_MESSAGES/{domain}.po"

    command = "update" if os.path.isfile(po_path) else "init"

    cmd = [
        "pybabel",
        command,
        f"--domain={domain}",
        f"--input-file={pot_path!s}",
        f"--output-dir={output_dir!s}",
        f"--locale={locale}",
    ]

    subprocess.check_call(cmd)


def compile_catalog(locale_dir: Path, domain: str, locale: str) -> Path:
    """
    Compile `*.po` files into `*.mo` files and saved them next to the
    original po files found.

    Args:
        locale_dir: Catalog output director
        domain: Catalog domain
        locale: locale
    Returns:
        Compile catalog file
    """
    # Check if locale exists!
    cmd = [
        "pybabel",
        "compile",
        f"--domain={domain}",
        f"--dir={locale_dir!s}",
        f"--locale={locale}",
    ]
    subprocess.check_call(cmd)

    return locale_dir / locale / LC_MESSAGES / f"{domain}.po"


def compile_to_mo(po_path: Path) -> Path:
    """Compile .po file into .mo file.

    Args:
        po_path: .po file to compile
    Returns:
        Path to the compiled .mo file
    """
    po = polib.pofile(str(po_path))
    mo_path = po_path.with_suffix(".mo")
    po.save_as_mofile(str(mo_path))
    return mo_path


# --- Global methods
# ----------------------------------------------------------------------------
def extract_translations(
    repo_root_dir: Union[str, Path],
    output_dir: Union[str, Path],
    project: str,
    merge: bool = True,
) -> Path:
    """
    Extract translations from a package folder

    Args:
        repo_root_dir: package folder to extract translation from
        output_dir: output folder
        project: project name
    Returns:
        Generated POT file path
    """
    # Load version from setup.py
    version = get_version(repo_root_dir, project)

    # Extract pot file
    locale_dir = Path(output_dir) / LOCALE_FOLDER
    locale_dir.mkdir(parents=True, exist_ok=True)

    pot_path, metadata = create_catalog(
        repo_root_dir, locale_dir, project, version, merge
    )
    remove_duplicates(pot_path, metadata)

    return pot_path


def update_translations(repo_root_dir, output_dir, project, locales=None):
    """
    FIXME:

    Parameters
    ----------
    repo_root_dir:
        FIXME:
    ouput_dir:
        FIXME:
    project:
        FIXME:
    locales: sequence
        FIXME:
    """
    raise NotImplementedError("update_translations not implemented")
    # # Find locales, if not there, error?
    # locale_dir = os.path.join(output_dir, LOCALE_FOLDER)
    # if locales is None:
    #     locales = find_locales(output_dir)

    # # Load version from setup.py
    # version = get_version(repo_root_dir, project)

    # # Extract pot file
    # os.makedirs(locale_dir, exist_ok=True)
    # pot_path = create_catalog(repo_root_dir, locale_dir, project, version)

    # Create or update po files
    for locale in locales:
        update_catalogs(pot_path, locale_dir, locale)


def compile_translations(
    output_dir: Path, project: str, locales: List[str] = None
) -> Dict[str, Path]:
    """
    Compile the translation for the given ``project`` in the provided output directory.

    Args:
        output_dir: Output directory
        project: Project name
        locales: Locale list
    Returns:
        Mapping (locale, catalog file)
    """
    if locales is None:
        locales = find_locales(output_dir)

    locale_dir = output_dir / LOCALE_FOLDER
    po_paths = {}
    for locale in locales:
        po_paths[locale] = compile_catalog(locale_dir, project, locale)

    return po_paths
