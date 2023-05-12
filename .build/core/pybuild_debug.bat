@echo off

call activate fiat_build
pyinstaller "pybuild_debug.spec"

pause