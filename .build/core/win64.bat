@echo off

call activate fiat_build
pyinstaller "pybuild.spec" --distpath ../../bin/core --workpath ../../bin/core/intermediates

pause