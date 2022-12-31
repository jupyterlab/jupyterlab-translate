# jupyterlab-translate

![Linux tests](https://github.com/jupyterlab/jupyterlab-translate/workflows/Run%20tests/badge.svg)
[![license](https://img.shields.io/pypi/l/jupyterlab-translate.svg)](./LICENSE.txt)
[![pypi version](https://img.shields.io/pypi/v/jupyterlab-translate.svg)](https://pypi.org/project/jupyterlab-translate/)
[![conda version](https://img.shields.io/conda/vn/conda-forge/jupyterlab-translate.svg)](https://www.anaconda.org/conda-forge/jupyterlab-translate)
[![Code Style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Join the chat at https://gitter.im/jupyterlab/jupyterlab](https://badges.gitter.im/jupyterlab/jupyterlab.svg)](https://gitter.im/jupyterlab/jupyterlab)

This package is used to generate [language packs](https://github.com/jupyterlab/language-packs) for the JupyterLab ecosystem.

This package performs the following tasks common on JupyterLab core and external extensions:

* Extract strings from code in `*.py`, `*.ts`, `*.tsx` files.
* Extract strings from JSON schema files.
* Create gettext `*.pot` catalogs.
* Removes duplicate strings from catalogs.
* Create gettext `*.po` catalogs for specific languages.
* Compile catalogs to `*.mo` and `*.json` format to be consumed by the JupyterLab frontend.
* Provide a [Hatch Build Hook](https://hatch.pypa.io/latest/plugins/build-hook/reference/) to compile catalogs when building wheels.
* Update the list of contributors from Crowdin project.

## Installation

### Pip

```bash
pip install jupyterlab-translate
```

You will also need to install `nodejs` >= 14.

### Conda

```bash
conda install jupyterlab-translate -c conda-forge
```

## Usage

### Bundle catalogs as part of a language pack

This is the recommended way of distributing your localization catalogs.

Visit the [language packs repository](https://github.com/jupyterlab/language-packs).

### Bundle catalogs with packages

```bash
jupyterlab-translate extract <JLAB-EXTENSION-DIR> <JLAB-EXTENSION-NAME>
jupyterlab-translate update <JLAB-EXTENSION-DIR> <JLAB-EXTENSION-NAME> -l es-ES
jupyterlab-translate compile <JLAB-EXTENSION-DIR> <JLAB-EXTENSION-NAME>
```

## Development

### Typescript extractor

To extract translatable strings from typescript files, this package relies on
[`gettext-extract`](https://github.com/sinedied/gettext-extract). To ease its
installation and usage, that tool is packaged within the python package by
creating a monolithic JavaScript file using [`@vercel/ncc`](https://github.com/vercel/ncc)
_compiler_.

To update the monolithic file, have a look at the [release file](./RELEASE.md).
