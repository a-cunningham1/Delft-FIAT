@echo off

call activate fiat_build
pyinstaller "pybuild_debug.spec" --distpath ../../bin/core/Debug --workpath ../../bin/core/intermediates

pause