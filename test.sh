#!/bin/sh
# Run the unit tests of the shell emulator.
ROOT_DIR=$(cd "$(dirname "$0")" && pwd)
cd "$ROOT_DIR" || exit 1
PYTHONPATH="$ROOT_DIR/src:$ROOT_DIR/tests" \
    exec "${PYTHON:-python3}" -m unittest discover -s tests -v
