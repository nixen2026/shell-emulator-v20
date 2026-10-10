@echo off
rem Run the shell emulator. All arguments are passed to the emulator.
setlocal
set "PYTHONPATH=%~dp0src"
python -m emulator %*
exit /b %ERRORLEVEL%
