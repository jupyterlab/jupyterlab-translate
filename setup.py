# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.
import ast
import os

from setuptools import find_packages
from setuptools import setup

# Constants
HERE = os.path.abspath(os.path.dirname(__file__))


def get_version(module="jupyterlab_translate"):
    """Get version."""
    with open(os.path.join(HERE, module, "__init__.py"), "r") as f:
        data = f.read()

    lines = data.split("\n")
    for line in lines:
        if line.startswith("__version__"):
            version = ast.literal_eval(line.split("=")[-1].strip())
            break

    return version


def get_description():
    """Get long description."""
    with open(os.path.join(HERE, "README.md"), "r") as f:
        data = f.read()

    return data


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
    install_requires=["babel", "click", "cookiecutter", "polib"],
    keywords=["localization", "translation", "jupyterlab", "jupyter", "i18n", "i10n"],
    packages=find_packages(),
    include_package_data=True,
    entry_points={
        "console_scripts": [
            "jupyterlab-translate = jupyterlab_translate.cli:main",
            "gettext-extract = jupyterlab_translate.gettext_extract:main",
        ]
    },
)
