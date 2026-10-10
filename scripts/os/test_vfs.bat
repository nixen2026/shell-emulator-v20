@echo off
rem Stage 3: run the emulator with different VFS variants.
setlocal
for %%I in ("%~dp0..\..") do set "ROOT_DIR=%%~fI"
set "RUN=%ROOT_DIR%\run.bat"
set "VFS_DIR=%ROOT_DIR%\build\vfs"

python "%ROOT_DIR%\scripts\make_vfs.py" "%VFS_DIR%"

echo === 1. Minimal VFS (one file) ===
echo vfs-info| call "%RUN%" --vfs "%VFS_DIR%\minimal.zip"

echo === 2. VFS with several files ===
echo vfs-info| call "%RUN%" --vfs "%VFS_DIR%\several.zip"

echo === 3. VFS with 3+ levels of files and directories ===
echo vfs-info| call "%RUN%" --vfs "%VFS_DIR%\deep.zip"

echo === 4. Same VFS stored as base64 text (same sha256) ===
echo vfs-info| call "%RUN%" --vfs "%VFS_DIR%\deep.b64"

echo === 5. Startup script with all stage 1-3 commands ===
call "%RUN%" --vfs "%VFS_DIR%\deep.zip" --script "%ROOT_DIR%\scripts\startup\stage3.txt"

echo === 6. Error: VFS file not found (exit code 1) ===
call "%RUN%" --vfs "%VFS_DIR%\no_such.zip"
echo exit code: %ERRORLEVEL%

echo === 7. Error: invalid VFS format (exit code 1) ===
call "%RUN%" --vfs "%VFS_DIR%\broken.zip"
echo exit code: %ERRORLEVEL%

echo === 8. Error: directory instead of a VFS file (exit code 1) ===
call "%RUN%" --vfs "%VFS_DIR%"
echo exit code: %ERRORLEVEL%
