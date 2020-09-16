# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.
"""
"""
import importlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from collections import OrderedDict

import babel
import polib
from cookiecutter.main import cookiecutter

from .constants import COOKIECUTTER_URL
from .constants import EXTENSIONS_FOLDER
from .constants import JUPYTERLAB
from .constants import LANG_PACKS_FOLDER
from .constants import LC_MESSAGES
from .constants import LOCALE_FOLDER
from .constants import TRANSLATIONS_FOLDER

# Constants
HERE = os.path.abspath(os.path.dirname(__file__))

# --- Helpers
# ----------------------------------------------------------------------------
def get_version(repo_root_path, project):
    """
    FIXME:

    Parameters
    ----------
    repo_root_path: str
        FIXME:
    project: str
        FIXME:

    Returns
    -------
    str
        Version string for project.
    """
    version_path = os.path.join(repo_root_path, project, "_version.py")
    init_path = os.path.join(repo_root_path, project, "__init__.py")
    pkg_path = os.path.join(repo_root_path, project, "package.json")

    version = ""
    # TODO: This is probably not robust enough, due to versioneer and friends
    if os.path.isfile(version_path) and not version:
        # Try `project/_version.py`
        sys.path.append(repo_root_path)
        try:
            spec = importlib.util.spec_from_file_location(project, version_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            version = module.__version__
        except Exception:
            pass

        sys.path.pop()

    if os.path.isfile(init_path) and not version:
        # Try `project/__init__.py`
        sys.path.append(repo_root_path)
        try:
            spec = importlib.util.spec_from_file_location(project, init_path)
            init_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(init_module)
            version = init_module.__version__
        except Exception:
            pass

        sys.path.pop()

    if os.path.isfile(pkg_path) and not version:
        # Try `package.json`
        with open(pkg_path, "r") as fh:
            data = json.load(fh)

        version = data.get("version", "")

    return version


def create_new_language_pack(output_dir, locale, cookiecutter_url=COOKIECUTTER_URL):
    """
    Creates a new language pack python package with cookiecutter.

    Parameters
    ----------
    output_dir: str
        FIXME:
    locale: str
        FIXME:
    """
    if not check_locale(locale):
        raise Exception("Invalid locale!")

    loc = babel.Locale.parse(locale)
    options = {"locale": locale.replace("_", "-"), "language": loc.english_name}
    cookiecutter(
        COOKIECUTTER_URL, extra_context=options, no_input=True, output_dir=output_dir
    )


def check_locale(locale):
    """Check if a locale is a valid value."""
    value = False
    try:
        val = babel.Locale.parse(locale)
        value = True
    except Exception as e:
        print(str(e))
        value = False

    return value


def find_locales(output_dir):
    """
    Find available locales on the `output_dir` folder.

    Parameters
    ----------
    output_dir: str
        FIXME:

    Returns
    -------
    tuple
        Sorted locales found in the Jupyter language packs repository.
    """
    locales = set()
    locale_path = os.path.join(output_dir, LOCALE_FOLDER)
    folders = os.listdir(locale_path) if os.path.isdir(locale_path) else []
    for locale_folder in folders:
        if locale_folder not in locales and check_locale(locale_folder):
            locales.add(locale_folder)

    return tuple(sorted(locales))


# --- Find source files
# ----------------------------------------------------------------------------
def find_packages_source_files(packages_path):
    """
    FIXME:

    Parameters
    ----------
    packages_path: str
        FIXME:

    Returns
    -------
    dict
        FIXME:
    """
    package_files = OrderedDict()
    for pkg_name in os.listdir(packages_path):
        files = find_source_files(os.path.join(packages_path, pkg_name))
        if files:
            package_files[pkg_name] = files

    return package_files


def find_source_files(
    path,
    extensions=(".ts", ".py"),
    skip_folders=("tests", "test", "node_modules", "lib", ".git", ".ipynb_checkpoints"),
):
    """
    Find source files in given `path`.

    Parameters
    ----------
    extensions: sequence
        FIXME:
    skip_folders: sequence
        FIXME:

    Returns
    -------
    list
        FIXME:
    """
    all_files = []
    for root, _dirs, files in os.walk(path, topdown=False):
        for name in files:
            fpath = os.path.join(root, name)
            if any(
                "{sep}{skip_folder}{sep}".format(sep=os.sep, skip_folder=skip_folder)
                in fpath
                for skip_folder in skip_folders
            ):
                continue

            if fpath.endswith(extensions):
                all_files.append(fpath)

    return all_files


# --- .pot and .po generation
# ----------------------------------------------------------------------------
def extract_tsx_strings(input_path):
    """
    Use gettext-extract to extract strings from TSX files.

    Parameters
    ----------
    temp_output_path: str
        FIXME:

    Returns
    -------
    str
        FIXME:
    """
    __, output_path = tempfile.mkstemp(suffix=".pot")
    if "~" in input_path:
        input_path = os.path.expanduser(input_path)

    config = {
        "js": {
            "parsers": [
                {"expression": "trans.__", "arguments": {"text": 0}},
                {"expression": "this._trans.__", "arguments": {"text": 0}},
                {"expression": "trans.gettext", "arguments": {"text": 0}},
                {"expression": "this._trans.gettext", "arguments": {"text": 0}},
                {"expression": "trans._n", "arguments": {"text": 0, "textPlural": 1}},
                {
                    "expression": "this._trans._n",
                    "arguments": {"text": 0, "textPlural": 1},
                },
                {
                    "expression": "trans.ngettext",
                    "arguments": {"text": 0, "textPlural": 1},
                },
                {
                    "expression": "this._trans.ngettext",
                    "arguments": {"text": 0, "textPlural": 1},
                },
                {"expression": "trans._p", "arguments": {"context": 0, "text": 1}},
                {
                    "expression": "this._trans._p",
                    "arguments": {"context": 0, "text": 1},
                },
                {
                    "expression": "trans.pgettext",
                    "arguments": {"context": 0, "text": 1},
                },
                {
                    "expression": "this._trans.pgettext",
                    "arguments": {"context": 0, "text": 1},
                },
                {
                    "expression": "trans._np",
                    "arguments": {"context": 0, "text": 1, "textPlural": 2},
                },
                {
                    "expression": "this._trans._np",
                    "arguments": {"context": 0, "text": 1, "textPlural": 2},
                },
                {
                    "expression": "trans.npgettext",
                    "arguments": {"context": 0, "text": 1, "textPlural": 2},
                },
                {
                    "expression": "this._trans.npgettext",
                    "arguments": {"context": 0, "text": 1, "textPlural": 2},
                },
            ],
            "glob": {
                "pattern": "packages/**/*.ts*(x)",
                "options": {"ignore": "packages/**/*.spec.ts"},
            },
            "comments": {"otherLineLeading": True},
        },
        "headers": {"Language": ""},
        "output": output_path,
    }
    __, config_path = tempfile.mkstemp(suffix=".json")
    with open(config_path, "w") as fh:
        fh.write(json.dumps(config))

    cmd = ["gettext-extract", "--config", config_path]
    p = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=input_path
    )
    stderr, stdout = p.communicate()
    if p.returncode != 0:
        raise Exception("`gettext-extract` error!")

    # Fix the missing format
    with open(output_path, "r") as fh:
        lines = ["#, fuzzy"] + fh.read().split("\n")

    with open(output_path, "w") as fh:
        fh.write("\n".join(lines))

    entries = []
    pot = polib.pofile(output_path, wrapwidth=100000)
    for entry in pot:
        occurrences = []
        for (string_fpath, line) in entry.occurrences:
            # Convert absolute paths to relative paths
            occurrences.append((string_fpath, line))

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

    try:
        os.remove(config_path)
    except Exception:
        pass

    try:
        os.remove(input_path)
    except Exception:
        pass

    return entries


def get_line(lines, value):
    value1 = '"' + value + '"'
    value2 = "'" + value + "'"
    line_count = 0
    for idx, line in enumerate(lines):
        # TODO: Might be needed for other escaped chars?
        line = line.replace(r"\n", "\n")
        if value1 in line or value2 in line:
            line_count = idx + 1

    return str(line_count)


def extract_schema_strings(input_path):
    """
    Use gettext-extract to extract strings from TSX files.

    Parameters
    ----------
    temp_output_path: str
        FIXME:

    Returns
    -------
    str
        FIXME:
    """
    input_paths = find_source_files(input_path, extensions=("package.json",))
    schema_paths = []
    message_context = "schema"

    for path in input_paths:
        if os.path.isfile(path):
            with open(path, "r") as fh:
                data = json.load(fh)

            schema_dir = data.get("jupyterlab", {}).get("schemaDir", None)
            if schema_dir is not None:
                schema_path = os.path.join(os.path.dirname(path), schema_dir)
                if os.path.isdir(schema_path):
                    for p in os.listdir(schema_path):
                        if p.endswith(".json"):
                            schema_paths.append(os.path.join(schema_path, p))

    entries = []
    for path in schema_paths:
        if os.path.isfile(path):
            with open(path, "r") as fh:
                data = fh.read()
                schema = json.loads(data)
                schema_lines = data.split("\n")

            ref_path = path.replace(input_path, "")
            title = schema["title"].replace("\n", "</br/>")
            entries.append(
                dict(
                    msgctxt=message_context,
                    msgid=title,
                    occurrences=[(ref_path, get_line(schema_lines, schema["title"]))],
                )
            )
            desc = schema["description"].replace("\n", "</br/>")
            entries.append(
                dict(
                    msgctxt=message_context,
                    msgid=desc,
                    occurrences=[
                        (ref_path, get_line(schema_lines, schema["description"]))
                    ],
                )
            )
            for __, values in schema.get("properties", {}).items():
                title = values.get("title", None)
                if title is not None:
                    entries.append(
                        dict(
                            msgid=title.replace("\n", "</br/>"),
                            occurrences=[(ref_path, get_line(schema_lines, title))],
                        )
                    )
                description = values.get("description", "")
                entries.append(
                    dict(
                        msgctxt=message_context,
                        msgid=description.replace("\n", "</br/>"),
                        occurrences=[(ref_path, get_line(schema_lines, description))],
                    )
                )

    return entries


def extract_strings(input_paths, output_path, project, version):
    """
    Extract localizable strings on input files.

    Parameters
    ----------
    input_paths: list
        FIXME:
    output_path: str
        FIXME:
    project: str
        FIXME:
    version: str
        FIXME:

    Returns
    -------
    str
        Output path.
    """
    mapping = os.path.join(HERE, "pybabel_config.cfg")
    cmd = [
        "pybabel",
        "extract",
        "--no-wrap",
        "--charset=utf-8",
        "-o",
        output_path,
        "--project={project}".format(project=project),
        "--version={version}".format(version=version),
        "--mapping={mapping}".format(mapping=mapping),
    ] + input_paths
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    p.communicate()
    return os.path.join(os.getcwd(), output_path)


def fix_location(path, pot_path, append_entries=None):
    """
    Remove any hardcoded paths on the pot file.

    Parameters
    ----------
    pot_file: str
        FIXME:
    append_entries: list of dict
        FIXME:
    """
    # Do not add column wrapping by using a large value!
    pot = polib.pofile(pot_path, wrapwidth=100000, check_for_duplicates=False)
    remove_path = path
    for entry in pot:
        new_occurrences = []
        string_fpaths = []
        lines = []
        for (string_fpath, line) in entry.occurrences:
            # Convert absolute paths to relative paths
            string_fpaths.append(os.path.abspath(string_fpath))
            lines.append(line)

            if line != "":
                string_fpath = " ".join(string_fpaths).replace(remove_path, "")

                # Normalize paths
                string_fpath = string_fpath.replace("\\", "/")

                new_occurrences.append((string_fpath, line))
                string_fpaths = []
                lines = []

        entry.occurrences = new_occurrences

    if append_entries:
        for entry in append_entries:
            entry = polib.POEntry(**entry)
            pot.append(entry)

    pot.save(pot_path)
    return pot.metadata.copy()


def remove_duplicates(pot_path, metadata):
    """
    FIXME:
    """
    old_pot_name = pot_path + ".bak"
    os.rename(pot_path, old_pot_name)
    pot = polib.pofile(old_pot_name, wrapwidth=100000, check_for_duplicates=False)
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

    po.save(pot_path)

    with open(pot_path, "r") as fh:
        data = fh.read()

    with open(pot_path, "w") as fh:
        fh.write(data.replace(r"</br/>", r"\n"))

    os.remove(old_pot_name)


def create_catalog(repo_root_dir, locale_dir, project, version):
    """
    FIXME:

    Parameters
    ----------
    repo_root_dir: str
        FIXME:
    locale_dir: str
        FIXME:
    project: str
        FIXME:
    version: str
        FIXME:
    """
    pot_path = os.path.join(locale_dir, "{project}.pot".format(project=project))
    nested_files = find_packages_source_files(repo_root_dir)
    flat_files = [item for sublist in nested_files.values() for item in sublist]
    extract_strings(flat_files, pot_path, project, version=version)
    append_entries_tsx = extract_tsx_strings(repo_root_dir)
    append_entries_schemas = extract_schema_strings(repo_root_dir)
    print(
        "\nTotal entries: {}\n".format(
            len(append_entries_schemas) + len(append_entries_tsx)
        )
    )
    metadata = fix_location(
        repo_root_dir, pot_path, append_entries_tsx + append_entries_schemas
    )
    return pot_path, metadata


def update_catalogs(pot_path, output_dir, locale):
    """
    Create new locale `.po` files or update and merge if they already exist.

    Parameters
    ----------
    pot_path: str
        Path to `.pot` file.
    output_dir: str
        Path to base output directory. The `.po` files will be placed in
        "{output_dir}/{locale}/LC_MESSAGES/{domain}.po".
        Domain will be infered from the `pot_path`.
    locale: str
        FIXME:
    """
    if not check_locale(locale):
        return

    pot_path = pot_path.replace("\\", "/")
    domain = pot_path.rsplit("/")[-1].replace(".pot", "")

    # Check if locale exists!
    po_path = "{output_dir}/{locale}/LC_MESSAGES/{domain}.po".format(
        output_dir=output_dir, locale=locale, domain=domain
    )
    command = "update" if os.path.isfile(po_path) else "init"
    cmd = [
        "pybabel",
        command,
        "--domain={domain}".format(domain=domain),
        "--input-file={pot_path}".format(pot_path=pot_path),
        "--output-dir={output_dir}".format(output_dir=output_dir),
        "--locale={locale}".format(locale=locale),
    ]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    p.communicate()


def compile_catalog(locale_dir, domain, locale):
    """
    Compile `*.po` files into `*.mo` files and saved them next to the
    original po files found.

    Parameters
    ----------
    output_dir: str
        FIXME:
    domain: str
        FIXME:
    locale: str, optional
        FIXME:
    """
    # Check if locale exists!
    cmd = [
        "pybabel",
        "compile",
        "--domain={domain}".format(domain=domain),
        "--dir={locale_dir}".format(locale_dir=locale_dir),
        "--locale={locale}".format(locale=locale),
    ]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    p.communicate()

    return os.path.join(
        locale_dir, locale, LC_MESSAGES, "{domain}.po".format(domain=domain)
    )


def compile_to_mo(po_path):
    po = polib.pofile(po_path)
    mo_path = po_path.replace(".po", ".mo")
    po.save_as_mofile(mo_path)
    return mo_path


# --- Global methods
# ----------------------------------------------------------------------------
def extract_translations(repo_root_dir, output_dir, project):
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
    """
    # Load version from setup.py
    version = get_version(repo_root_dir, project)

    # Extract pot file
    locale_dir = os.path.join(output_dir, LOCALE_FOLDER)
    os.makedirs(locale_dir, exist_ok=True)
    pot_path, metadata = create_catalog(repo_root_dir, locale_dir, project, version)
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


def compile_translations(output_dir, project, locales=None):
    """
    FIXME:

    Parameters
    ----------
    output_dir: str
        FIXME:
    project: str
        FIXME:
    locales: sequence
        FIXME:

    Returns
    -------
    dict
        FIXME:
    """
    if locales is None:
        locales = find_locales(output_dir)

    locale_dir = os.path.join(output_dir, LOCALE_FOLDER)
    po_paths = {}
    for locale in locales:
        po_path = compile_catalog(locale_dir, project, locale)
        po_paths[locale] = po_path

    return po_paths
