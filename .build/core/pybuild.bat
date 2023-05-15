@echo off

call activate fiat_build
pyinstaller "pybuild.spec" --distpath ../../bin/core/Release --workpath ../../bin/core/intermediates

pause