@echo off
rem Stage 2: run the emulator with every supported command-line option.
setlocal
for %%I in ("%~dp0..\..") do set "ROOT_DIR=%%~fI"
set "RUN=%ROOT_DIR%\run.bat"
set "STARTUP=%ROOT_DIR%\scripts\startup"

echo === 1. No options: parameters are not set ===
echo conf-dump| call "%RUN%"

echo === 2. --vfs only ===
echo conf-dump| call "%RUN%" --vfs "%ROOT_DIR%\build\vfs\minimal.zip"

echo === 3. --script only (script ends with exit 0) ===
call "%RUN%" --script "%STARTUP%\stage2.txt"
echo exit code: %ERRORLEVEL%

echo === 4. --vfs and --script together ===
call "%RUN%" --vfs "%ROOT_DIR%\build\vfs\minimal.zip" --script "%STARTUP%\stage2.txt"

echo === 5. Help ===
call "%RUN%" --help

echo === 6. Unknown option (error, exit code 2) ===
call "%RUN%" --unknown
echo exit code: %ERRORLEVEL%

echo === 7. Missing option value (error, exit code 2) ===
call "%RUN%" --script
echo exit code: %ERRORLEVEL%
