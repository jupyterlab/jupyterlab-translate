import subprocess
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).parent
REPO_ROOT = HERE.parent.as_uri()

TOML_CONTENT = f"""
[build-system]
requires = ["hatchling>=1.4.0"]
build-backend = "hatchling.build"

[project]
name = "jupyterlab_language_pack_ko_KR"
dynamic = ["version"]

[project.entry-points."jupyterlab.languagepack"]
    ko_KR = "jupyterlab_language_pack_ko_KR"

[projects.urls]
homepage = "https://github.com/jupyterlab/language-packs"

[tool.hatch.build.targets.wheel]
artifacts = [
    "jupyterlab_language_pack_ko_KR/**/*.json",
    "jupyterlab_language_pack_ko_KR/**/*.mo",
]

[tool.hatch.version]
path = "jupyterlab_language_pack_ko_KR/__init__.py"


[tool.hatch.build.hooks.jupyter-translate]
dependencies = ["jupyterlab-translate@{REPO_ROOT}"]
"""

@pytest.fixture
def language_package(tmp_path):
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text(TOML_CONTENT)

    pkg = tmp_path / "jupyterlab_language_pack_ko_KR"
    pkg.mkdir()
    messages = pkg / "locale" / "ko_KR" / "LC_MESSAGES"

    (pkg / "__init__.py").write_text("""__version__ = "1.0.post2"
""")
    messages.mkdir(parents=True)
    (messages / "jupyterlab.po").write_text("""msgid ""
msgstr ""
"Project-Id-Version: jupyterlab\n"
"MIME-Version: 1.0\n"
"Content-Type: text/plain; charset=UTF-8\n"
"Content-Transfer-Encoding: 8bit\n"
"Plural-Forms: nplurals=1; plural=0;\n"
"X-Crowdin-Project: jupyterlab\n"
"X-Crowdin-Project-ID: 409874\n"
"X-Crowdin-Language: ko\n"
"X-Crowdin-File: /master/jupyterlab/locale/jupyterlab.pot\n"
"X-Crowdin-File-ID: 93\n"
"Language-Team: Korean\n"
"Language: ko_KR\n"
"PO-Revision-Date: 2021-11-19 10:57\n"

#: /examples/federated/md_package/schema/plugin.json:/description /packages/markdownviewer-extension/schema/plugin.json:/description
msgctxt "schema"
msgid "Markdown viewer settings."
msgstr "마크다운 뷰어 설정"

#: /examples/federated/md_package/schema/plugin.json:/jupyter.lab.setting-icon-label /packages/markdownviewer-extension/schema/plugin.json:/jupyter.lab.setting-icon-label
msgctxt "settings"
msgid "Markdown Viewer"
msgstr "마크다운 뷰어"

#: /examples/federated/md_package/schema/plugin.json:/properties/fontFamily/description /packages/markdownviewer-extension/schema/plugin.json:/properties/fontFamily/description
msgctxt "settings"
msgid "The font family used to render markdown.\n"
"If `null`, value from current theme is used."
msgstr "마크다운을 표시할 때 사용하는 글꼴.\n"
"값이 `null`이면 현재 테마의 해당 값이 사용됩니다."

""")
    (messages / "spellchecker.po").write_text("""msgid ""
msgstr ""
"Project-Id-Version: jupyterlab\n"
"MIME-Version: 1.0\n"
"Content-Type: text/plain; charset=UTF-8\n"
"Content-Transfer-Encoding: 8bit\n"
"Plural-Forms: nplurals=4; plural=(n==1 ? 0 : (n%10>=2 && n%10<=4) && (n%100<12 || n%100>14) ? 1 : n!=1 && (n%10>=0 && n%10<=1) || (n%10>=5 && n%10<=9) || (n%100>=12 && n%100<=14) ? 2 : 3);\n"
"X-Crowdin-Project: jupyterlab\n"
"X-Crowdin-Project-ID: 409874\n"
"X-Crowdin-Language: pl\n"
"X-Crowdin-File: /master/extensions/spellchecker/locale/spellchecker.pot\n"
"X-Crowdin-File-ID: 103\n"
"Language-Team: Polish\n"
"Language: pl_PL\n"
"PO-Revision-Date: 2021-08-26 21:28\n"

#: /schema/plugin.json:/definitions/onlineDictionaries/items/properties/aff/title
msgctxt "settings"
msgid "URL address of the .aff file"
msgstr "Adres URL pliku .aff"

#: /schema/plugin.json:/definitions/onlineDictionaries/items/properties/dic/title
msgctxt "settings"
msgid "URL address of the .dic file"
msgstr "Adres URL pliku .dic"

#: /schema/plugin.json:/definitions/onlineDictionaries/items/properties/id/title
msgctxt "settings"
msgid "Unique identifier"
msgstr "Unikalny identyfikator"

""")

    yield tmp_path


def test_hatch_build(language_package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", "build"], cwd=language_package)

    subprocess.check_call([sys.executable, "-m", "build", "."], cwd=language_package)
