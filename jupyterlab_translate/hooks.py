# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.
from hatchling.plugin import hookimpl

from jupyterlab_translate.plugin import JupyterLanguageBuildHook


@hookimpl
def hatch_register_build_hook():
    return JupyterLanguageBuildHook
