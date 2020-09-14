from setuptools import find_packages, setup

setup(
    name="jupyterlab-translate",
    version="0.1.0",
    author="Gonzalo Peña-Castellanos",
    author_email="goanpeca@gmail.com",
    license="BSD-3-Clause",
    url="https://github.com/jupyterlab/jupyterlab-translate",
    description="Jupyterlab Language Pack Translations Helper",
    install_requires=["click", "cookiecutter", "polib", "babel"],
    keywords=["localization", "translation", "jupyterlab", "jupyter", "i18n", "i10n"],
    packages=find_packages(),
    include_package_data=True,
    entry_points={
        "console_scripts": [
            "jlab-trans = jupyterlab_translate.cli:main",
            "jlab-translate = jupyterlab_translate.cli:main",
            "jupyterlab-translate = jupyterlab_translate.cli:main",
        ],
    },
)
