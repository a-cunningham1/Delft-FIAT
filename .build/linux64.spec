from fiat.util import generic_folder_check

import os
import shutil
import subprocess
import sys
import PyInstaller.config
from pathlib import Path

#Pre build event setup
app_name = "fiat"
sys.setrecursionlimit(5000)
generic_folder_check("../../bin/core")

cwd = Path.cwd()
env_path =  os.path.dirname(sys.executable)
mode = "Release"

bin = Path(env_path, 'Library', 'bin')
dlls = Path(env_path, 'DLLs')
osgeo = Path(env_path, 'Lib\site-packages\osgeo')
proj = Path(os.environ["PROJ_LIB"])

paths = [
    cwd,
    env_path,
    dlls,
    bin,
]

binaries = [

]

block_cipher = None

# Build event
a = Analysis(
    ["../../src/fiat/cli/main_old.py"],
    pathex=["../../src", Path(env_path, "lib/site-packages")],
    binaries=binaries,
    datas=[],
    hiddenimports=[],
    hookspath=[],
    runtime_hooks=['runtime_hooks.py'],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(
    a.pure,
    a.zipped_data,
    cipher=block_cipher,
)

exe = EXE(
    pyz,
    a.scripts,
    [],
    icon="NONE",
    exclude_binaries=True,
    name=app_name,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=True,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name=mode,
)

# Post build event
sys.stdout.write("1E10 INFO: Moving libraries to seperatate lib folder...\n")
app_path = Path(DISTPATH, mode)
lib_path = Path(app_path, "lib")
if not lib_path.is_dir():
    os.makedirs(lib_path)
for item in Path(app_path).iterdir():
    if (item.is_file() and item.suffix in [".pyd", ".so", ".a", ".db"]
        and item.name not in ["python311", "zlib"]):
        shutil.move(item, Path(lib_path, item.name))
        sp = subprocess.run([str(Path(app_path, f"{app_name}"))], capture_output=True)
        sys.stdout.write(f"1E10 INFO: Code: {sp.returncode} -> Binary: {item}\n")
        if sp.returncode != 0:
            shutil.move(Path(lib_path, item.name), item)