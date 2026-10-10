@echo off
rem Stage 2: startup scripts, comments and error reporting.
setlocal
for %%I in ("%~dp0..\..") do set "ROOT_DIR=%%~fI"
set "RUN=%ROOT_DIR%\run.bat"
set "STARTUP=%ROOT_DIR%\scripts\startup"

echo === 1. Script with commands, comments and errors ===
call "%RUN%" --script "%STARTUP%\stage2.txt"
echo exit code: %ERRORLEVEL%

echo === 2. Comments only, then interactive mode (input from pipe) ===
(echo ls piped& echo exit 7)| call "%RUN%" --script "%STARTUP%\comments_only.txt"
echo exit code: %ERRORLEVEL%

echo === 3. Script file does not exist (error, exit code 1) ===
call "%RUN%" --script "%STARTUP%\no_such_script.txt"
echo exit code: %ERRORLEVEL%
