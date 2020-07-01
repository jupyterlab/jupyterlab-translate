from setuptools import setup

setup(
    name="jupyterlab-translate",
    version="0.1.0",
    author="Gonzalo Peña-Castellanos",
    author_email="goanpeca@gmail.com",
    url="https://github.com/goanpeca/jupyterlab-translate",
    description="Jupyterlab Language Pack Translations Helper",
    install_requires=["click", "cookiecutter", "polib", "babel"],
    keywords=["localization", "translation", "jupyterlab", "jupyter", "i18n"],
    packages=["jupyterlab_translate"],
    package_dir={"jupyterlab_translate": "jupyterlab_translate"},
    package_data={"": ["*.cfg"]},
    entry_points={"console_scripts": ["jlab-trans = jupyterlab_translate.cli:main"]},
)
