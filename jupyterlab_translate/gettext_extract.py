# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.
import os
import subprocess
import sys

# Constants
HERE = os.path.abspath(os.path.dirname(__file__))
INDEX_JS = os.path.join(HERE, "index.js")


def main():
    args = sys.argv[1:]
    subprocess.Popen(["node", INDEX_JS] + args).communicate()


if __name__ == "__main__":
    main()
