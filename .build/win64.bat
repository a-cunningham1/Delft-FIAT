@echo off

REM set the current directory of the batch file
set CUR_DIR=%~dp0

REM Execute building
call activate fiat_build
pyinstaller "%CUR_DIR%/build.spec" --distpath %CUR_DIR%../bin --workpath %CUR_DIR%../bin/intermediates

pause
