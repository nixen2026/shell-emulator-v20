@echo off
rem Stages 4-5: run startup scripts that test the emulator commands.
setlocal
for %%I in ("%~dp0..\..") do set "ROOT_DIR=%%~fI"
set "RUN=%ROOT_DIR%\run.bat"
set "VFS_DIR=%ROOT_DIR%\build\vfs"
set "STARTUP=%ROOT_DIR%\scripts\startup"

python "%ROOT_DIR%\scripts\make_vfs.py" "%VFS_DIR%"

echo === Stage 4: ls, cd, clear, uname ===
call "%RUN%" --vfs "%VFS_DIR%\deep.zip" --script "%STARTUP%\stage4.txt"
echo exit code: %ERRORLEVEL%
