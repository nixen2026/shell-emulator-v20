#!/bin/sh
# Stages 4-5: run startup scripts that test the emulator commands.
ROOT_DIR=$(cd "$(dirname "$0")/../.." && pwd)
RUN="$ROOT_DIR/run.sh"
VFS_DIR="$ROOT_DIR/build/vfs"
STARTUP="$ROOT_DIR/scripts/startup"

"${PYTHON:-python3}" "$ROOT_DIR/scripts/make_vfs.py" "$VFS_DIR"

echo "=== Stage 4: ls, cd, clear, uname ==="
"$RUN" --vfs "$VFS_DIR/deep.zip" --script "$STARTUP/stage4.txt"
echo "exit code: $?"
