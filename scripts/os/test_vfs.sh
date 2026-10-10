#!/bin/sh
# Stage 3: run the emulator with different VFS variants.
ROOT_DIR=$(cd "$(dirname "$0")/../.." && pwd)
RUN="$ROOT_DIR/run.sh"
VFS_DIR="$ROOT_DIR/build/vfs"

"${PYTHON:-python3}" "$ROOT_DIR/scripts/make_vfs.py" "$VFS_DIR"

echo "=== 1. Minimal VFS (one file) ==="
echo "vfs-info" | "$RUN" --vfs "$VFS_DIR/minimal.zip"

echo "=== 2. VFS with several files ==="
echo "vfs-info" | "$RUN" --vfs "$VFS_DIR/several.zip"

echo "=== 3. VFS with 3+ levels of files and directories ==="
echo "vfs-info" | "$RUN" --vfs "$VFS_DIR/deep.zip"

echo "=== 4. Same VFS stored as base64 text (same sha256) ==="
echo "vfs-info" | "$RUN" --vfs "$VFS_DIR/deep.b64"

echo "=== 5. Startup script with all stage 1-3 commands ==="
"$RUN" --vfs "$VFS_DIR/deep.zip" \
    --script "$ROOT_DIR/scripts/startup/stage3.txt"

echo "=== 6. Error: VFS file not found (exit code 1) ==="
"$RUN" --vfs "$VFS_DIR/no_such.zip"
echo "exit code: $?"

echo "=== 7. Error: invalid VFS format (exit code 1) ==="
"$RUN" --vfs "$VFS_DIR/broken.zip"
echo "exit code: $?"

echo "=== 8. Error: directory instead of a VFS file (exit code 1) ==="
"$RUN" --vfs "$VFS_DIR"
echo "exit code: $?"
