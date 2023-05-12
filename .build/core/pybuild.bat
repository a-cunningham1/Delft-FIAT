@echo off

call activate fiat_build
pyinstaller "pybuild.spec"

pause