# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.
import ast
from pathlib import Path

from setuptools import find_packages
from setuptools import setup

# Constants
HERE = Path(__file__).parent.resolve()


def get_version(module="jupyterlab_translate"):
    """Get version."""
    data = (HERE / module / "__init__.py").read_text()

    for line in data.splitlines():
        if line.startswith("__version__"):
            version = ast.literal_eval(line.split("=")[-1].strip())
            break

    return version


def get_description():
    """Get long description."""
    return (HERE / "README.md").read_text()


run_requirements = [
    p for p in (HERE / "requirements" / "run.txt").read_text().splitlines() if p
]
test_requirements = [
    p for p in (HERE / "requirements" / "run.txt").read_text().splitlines() if p
]
release_requirements = [
    p for p in (HERE / "requirements" / "run.txt").read_text().splitlines() if p
]

setup(
    name="jupyterlab-translate",
    version=get_version(),
    description="Jupyterlab Language Pack Translations Helper",
    long_description=get_description(),
    long_description_content_type="text/markdown",
    author="Project Jupyter Contributors",
    author_email="jupyter@googlegroups.com",
    license="BSD-3-Clause",
    platforms="Linux, Mac OS X, Windows",
    url="https://github.com/jupyterlab/jupyterlab-translate",
    install_requires=run_requirements,
    keywords=["localization", "translation", "jupyterlab", "jupyter", "i18n", "i10n"],
    packages=find_packages(),
    include_package_data=True,
    entry_points={
        "console_scripts": [
            "jupyterlab-translate = jupyterlab_translate.cli:main",
            "gettext-extract = jupyterlab_translate.gettext_extract:main",
        ]
    },
    extras_requires={"test": test_requirements, "release": release_requirements},
)
