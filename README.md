# jupyterlab-translate

![Linux tests](https://github.com/jupyterlab/jupyterlab-translate/workflows/Run%20tests/badge.svg)
[![Code Style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Join the chat at https://gitter.im/jupyterlab/jupyterlab](https://badges.gitter.im/jupyterlab/jupyterlab.svg)](https://gitter.im/jupyterlab/jupyterlab?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)

Jupyterlab Language Pack Translations Helper.

This package is used to generate [language packs](https://github.com/jupyterlab/language-packs) for the JupyterLab ecosystem.

## Installation

### Pip

```bash
pip install jupyterlab-translate
```

You will also need to install an npm package to be able to extract strings from `*.tsx` files.

```bash
npm install gettext-extract -g
```

### Conda

```bash
conda install jupyterlab-translate -c conda-forge
```

## Usage

```bash
jlab-trans extract-pack ~/develop/quansight/jupyterlab ~/develop/quansight/language-packs jupyterlab
jlab-trans update-pack ~/develop/quansight/jupyterlab ~/develop/quansight/jupyterlab-language-packs jupyterlab -l es
jlab-trans compile-pack ~/develop/quansight/jupyterlab-language-packs jupyterlab -l es
```

### Jupyterlab example language packs

```bash
jlab-trans update-pack ~/develop/quansight/jupyterlab ~/develop/quansight/jupyterlab-language-packs jupyterlab -l es
jlab-trans compile-pack ~/develop/quansight/language-packs jupyterlab -l zh_CN
jlab-trans update-pack ~/develop/quansight/jupyterlab ~/develop/quansight/jupyterlab-language-packs jupyterlab -l pt_BR
jlab-trans update-pack ~/develop/quansight/jupyterlab ~/develop/quansight/jupyterlab-language-packs jupyterlab -l fr
jlab-trans compile-pack ~/develop/quansight/jupyterlab-language-packs jupyterlab -l fr
jlab-trans compile-pack ~/develop/quansight/jupyterlab-language-packs jupyterlab -l pt_BR
```

### Extension example language packs

```bash
jlab-trans update-pack ~/develop/quansight/jupyterlab-git ~/develop/quansight/jupyterlab-language-packs jupyterlab_git -l es
jlab-trans compile-pack ~/develop/quansight/jupyterlab-git jupyterlab_git -l es
```

### Extension example stand alone package

```bash
jlab-trans update ~/develop/quansight/jupyterlab-git jupyterlab_git -l es
jlab-trans compile ~/develop/quansight/jupyterlab-git jupyterlab_git -l es
```
