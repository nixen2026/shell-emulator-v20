#!/bin/sh
# Stage 2: startup scripts, comments and error reporting.
ROOT_DIR=$(cd "$(dirname "$0")/../.." && pwd)
RUN="$ROOT_DIR/run.sh"
STARTUP="$ROOT_DIR/scripts/startup"

echo "=== 1. Script with commands, comments and errors ==="
"$RUN" --script "$STARTUP/stage2.txt"
echo "exit code: $?"

echo "=== 2. Comments only, then interactive mode (input from pipe) ==="
printf 'ls piped\nexit 7\n' | "$RUN" --script "$STARTUP/comments_only.txt"
echo "exit code: $?"

echo "=== 3. Script file does not exist (error, exit code 1) ==="
"$RUN" --script "$STARTUP/no_such_script.txt"
echo "exit code: $?"
