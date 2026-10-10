#!/bin/sh
# Stage 2: run the emulator with every supported command-line option.
ROOT_DIR=$(cd "$(dirname "$0")/../.." && pwd)
RUN="$ROOT_DIR/run.sh"
STARTUP="$ROOT_DIR/scripts/startup"

echo "=== 1. No options: parameters are not set ==="
echo "conf-dump" | "$RUN"

echo "=== 2. --vfs only ==="
echo "conf-dump" | "$RUN" --vfs "$ROOT_DIR/build/vfs/minimal.zip"

echo "=== 3. --script only (script ends with exit 0) ==="
"$RUN" --script "$STARTUP/stage2.txt"
echo "exit code: $?"

echo "=== 4. --vfs and --script together ==="
"$RUN" --vfs "$ROOT_DIR/build/vfs/minimal.zip" \
    --script "$STARTUP/stage2.txt"

echo "=== 5. Help ==="
"$RUN" --help

echo "=== 6. Unknown option (error, exit code 2) ==="
"$RUN" --unknown
echo "exit code: $?"

echo "=== 7. Missing option value (error, exit code 2) ==="
"$RUN" --script
echo "exit code: $?"
