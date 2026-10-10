@echo off
rem Run the unit tests of the shell emulator.
setlocal
cd /d "%~dp0"
set "PYTHONPATH=%~dp0src;%~dp0tests"
python -m unittest discover -s tests -v
exit /b %ERRORLEVEL%
