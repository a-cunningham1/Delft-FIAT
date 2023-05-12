import os
import sys
from pathlib import Path

sys.setrecursionlimit(5000)

env_path =  os.path.dirname(sys.executable)
dlls = Path(env_path, 'DLLs')
bin = Path(env_path, 'Library', 'bin')
proj = Path(os.environ["PROJ_LIB"])

paths = [
    os.getcwd(),
    env_path,
    dlls,
    bin,
]

binaries = [
    (Path(bin,'geos.dll'),'.'),
    (Path(bin,'geos_c.dll'),'.'),
    (Path(bin,'spatialindex_c-64.dll'),'.'),
    (Path(bin,'spatialindex-64.dll'),'.'),
	(Path(proj,'proj.db'),'.')
]

block_cipher = None

a = Analysis(
    ['path_to_python_file'],
    pathex=['path_to_folder', 'path_to_env_packages', bin],
    binaries=binaries,
    datas=[],
    hiddenimports=[],
    hookspath=[],
    runtime_hooks=['runtime_hooks.py'],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False
)

pyz = PYZ(
    a.pure,
    a.zipped_data,
    cipher=block_cipher
)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='fiat_core',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='fiat_core'
)
