#!/bin/sh
# Run the shell emulator. All arguments are passed to the emulator.
ROOT_DIR=$(cd "$(dirname "$0")" && pwd)
PYTHONPATH="$ROOT_DIR/src" exec "${PYTHON:-python3}" -m emulator "$@"
