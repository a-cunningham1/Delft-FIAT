@echo off

call activate fiat_build
pyinstaller "pybuild_debug.spec" --distpath ../../bin/core --workpath ../../bin/core/intermediates

pause