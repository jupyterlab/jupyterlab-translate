import subprocess
import sys
import tarfile
import zipfile
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

[tool.hatch.version]
path = "jupyterlab_language_pack_ko_KR/__init__.py"

[tool.hatch.build]
artifacts = [
    "CONTRIBUTORS.md"
]

[tool.hatch.build.hooks.jupyter-translate]
dependencies = ["jupyterlab-translate@{REPO_ROOT}"]

[tool.hatch.build.targets.wheel]
artifacts = [
    "jupyterlab_language_pack_ko_KR/**/*.json",
    "jupyterlab_language_pack_ko_KR/**/*.mo",
]
exclude = [
    "jupyterlab_language_pack_ko_KR/**/*.po",
]
"""


@pytest.fixture
def language_package(tmp_path):
    (tmp_path / "pyproject.toml").write_text(TOML_CONTENT)
    (tmp_path / "CONTRIBUTORS.md").write_text("# Contributors\n")

    pkg = tmp_path / "jupyterlab_language_pack_ko_KR"
    pkg.mkdir()
    messages = pkg / "locale" / "ko_KR" / "LC_MESSAGES"

    (pkg / "__init__.py").write_text(
        """__version__ = "1.0.post2"
"""
    )
    messages.mkdir(parents=True)
    (messages / "jupyterlab.po").write_text(
        """msgid ""
msgstr ""
"Project-Id-Version: jupyterlab\\n"
"MIME-Version: 1.0\\n"
"Content-Type: text/plain; charset=UTF-8\\n"
"Content-Transfer-Encoding: 8bit\\n"
"Plural-Forms: nplurals=1; plural=0;\\n"
"X-Crowdin-Project: jupyterlab\\n"
"X-Crowdin-Project-ID: 409874\\n"
"X-Crowdin-Language: ko\\n"
"X-Crowdin-File: /master/jupyterlab/locale/jupyterlab.pot\\n"
"X-Crowdin-File-ID: 93\\n"
"Language-Team: Korean\\n"
"Language: ko_KR\\n"
"PO-Revision-Date: 2021-11-19 10:57\\n"

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
msgid "The font family used to render markdown.\\n"
"If `null`, value from current theme is used."
msgstr "마크다운을 표시할 때 사용하는 글꼴.\\n"
"값이 `null`이면 현재 테마의 해당 값이 사용됩니다."

"""
    )
    (messages / "spellchecker.po").write_text(
        """msgid ""
msgstr ""
"Project-Id-Version: jupyterlab\\n"
"MIME-Version: 1.0\\n"
"Content-Type: text/plain; charset=UTF-8\\n"
"Content-Transfer-Encoding: 8bit\\n"
"Plural-Forms: nplurals=4; plural=(n==1 ? 0 : (n%10>=2 && n%10<=4) && (n%100<12 || n%100>14) ? 1 : n!=1 && (n%10>=0 && n%10<=1) || (n%10>=5 && n%10<=9) || (n%100>=12 && n%100<=14) ? 2 : 3);\\n"
"X-Crowdin-Project: jupyterlab\\n"
"X-Crowdin-Project-ID: 409874\\n"
"X-Crowdin-Language: pl\\n"
"X-Crowdin-File: /master/extensions/spellchecker/locale/spellchecker.pot\\n"
"X-Crowdin-File-ID: 103\\n"
"Language-Team: Polish\\n"
"Language: pl_PL\\n"
"PO-Revision-Date: 2021-08-26 21:28\\n"

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

"""
    )

    yield tmp_path


def test_hatch_build(language_package):
    subprocess.check_call(
        [sys.executable, "-m", "pip", "install", "build"], cwd=language_package
    )

    subprocess.check_call([sys.executable, "-m", "build", "."], cwd=language_package)

    # Check sdist
    with tarfile.open(
        (
            language_package
            / "dist"
            / "jupyterlab_language_pack_ko_kr-1.0.post2.tar.gz"
        ).as_posix(),
        "r:gz",
    ) as sdist:
        assert sdist.getnames() == [
            "jupyterlab_language_pack_ko_kr-1.0.post2/CONTRIBUTORS.md",
            "jupyterlab_language_pack_ko_kr-1.0.post2/jupyterlab_language_pack_ko_KR/__init__.py",
            "jupyterlab_language_pack_ko_kr-1.0.post2/jupyterlab_language_pack_ko_KR/locale/ko_KR/LC_MESSAGES/jupyterlab.po",
            "jupyterlab_language_pack_ko_kr-1.0.post2/jupyterlab_language_pack_ko_KR/locale/ko_KR/LC_MESSAGES/spellchecker.po",
            "jupyterlab_language_pack_ko_kr-1.0.post2/pyproject.toml",
            "jupyterlab_language_pack_ko_kr-1.0.post2/PKG-INFO",
        ]

    # Check wheel
    with zipfile.ZipFile(
        (
            language_package
            / "dist"
            / "jupyterlab_language_pack_ko_kr-1.0.post2-py2.py3-none-any.whl"
        ).as_posix()
    ) as wheel:
        assert wheel.namelist() == [
            "jupyterlab_language_pack_ko_KR/__init__.py",
            "jupyterlab_language_pack_ko_KR/locale/ko_KR/LC_MESSAGES/jupyterlab.json",
            "jupyterlab_language_pack_ko_KR/locale/ko_KR/LC_MESSAGES/jupyterlab.mo",
            "jupyterlab_language_pack_ko_KR/locale/ko_KR/LC_MESSAGES/spellchecker.json",
            "jupyterlab_language_pack_ko_KR/locale/ko_KR/LC_MESSAGES/spellchecker.mo",
            "jupyterlab_language_pack_ko_kr-1.0.post2.dist-info/METADATA",
            "jupyterlab_language_pack_ko_kr-1.0.post2.dist-info/WHEEL",
            "jupyterlab_language_pack_ko_kr-1.0.post2.dist-info/entry_points.txt",
            "jupyterlab_language_pack_ko_kr-1.0.post2.dist-info/RECORD",
        ]
        with wheel.open(
            "jupyterlab_language_pack_ko_KR/locale/ko_KR/LC_MESSAGES/jupyterlab.json"
        ) as myfile:
            myfile.read().decode(
                "utf-8"
            ) == """{
    "": {
        "domain": "jupyterlab",
        "language": "ko-KR",
        "plural_forms": "nplurals=1; plural=0;",
        "version": "jupyterlab"
    },
    "schema\u0004Markdown viewer settings.": [
        "\ub9c8\ud06c\ub2e4\uc6b4 \ubdf0\uc5b4 \uc124\uc815"
    ],
    "settings\u0004Markdown Viewer": [
        "\ub9c8\ud06c\ub2e4\uc6b4 \ubdf0\uc5b4"
    ],
    "settings\u0004The font family used to render markdown.\nIf `null`, value from current theme is used.": [
        "\ub9c8\ud06c\ub2e4\uc6b4\uc744 \ud45c\uc2dc\ud560 \ub54c \uc0ac\uc6a9\ud558\ub294 \uae00\uaf34.\n\uac12\uc774 `null`\uc774\uba74 \ud604\uc7ac \ud14c\ub9c8\uc758 \ud574\ub2f9 \uac12\uc774 \uc0ac\uc6a9\ub429\ub2c8\ub2e4."
    ]
}"""
