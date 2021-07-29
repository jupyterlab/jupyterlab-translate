# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.
import subprocess
import sys
from pathlib import Path

# Constants
HERE = Path(__file__).parent.resolve()
INDEX_JS = HERE / "index.js"


def main():
    args = sys.argv[1:]
    subprocess.check_call(["node", str(INDEX_JS)] + args)


if __name__ == "__main__":
    main()
