@echo off

call activate fiat_build
pyinstaller "win64.spec" --distpath ../bin --workpath ../bin/intermediates

pause