from delft_fiat.util import generic_folder_check

import os
import sys
import PyInstaller.config
from pathlib import Path

sys.setrecursionlimit(5000)
generic_folder_check("../../bin/core")

cwd = Path.cwd()
env_path =  os.path.dirname(sys.executable)

# PyInstaller.config.CONF["DISTPATH"] = Path(cwd,"../../bin/core/dist")
# PyInstaller.config.CONF["workpath"] = Path(cwd,"../../bin/core/build")

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
    (Path(osgeo,'geos.dll'),'.'),
    (Path(osgeo,'geos_c.dll'),'.'),
    # (Path(bin,'spatialindex_c-64.dll'),'.'),
    # (Path(bin,'spatialindex-64.dll'),'.'),
	(Path(proj,'proj.db'),'.'),
]

block_cipher = None

a = Analysis(
    ["../../src/delft_fiat/cli/main.py"],
    pathex=["../../src", Path(env_path, "lib/site-packages"), bin],
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
    name='fiat',
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
    name='fiat',
)
