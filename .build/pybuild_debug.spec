import os
import sys

sys.setrecursionlimit(5000)

env_path =  os.path.dirname(sys.executable)
dlls = os.path.join(env_path, 'DLLs')
bins = os.path.join(env_path, 'Library', 'bin')
share = os.path.join(env_path, 'Library', 'share')

paths = [
    os.getcwd(),
    env_path,
    dlls,
    bins,
]

binaries = [
    (os.path.join(bins,'geos.dll'),'.'),
    (os.path.join(bins,'geos_c.dll'),'.'),
    (os.path.join(bins,'spatialindex_c-64.dll'),'.'),
    (os.path.join(bins,'spatialindex-64.dll'),'.'),
	(os.path.join(share,'proj','proj.db'),'.')
]

block_cipher = None

a = Analysis(
    ['path_to_python_file'],
    pathex=['path_to_folder', 'path_to_env_packages', bins],
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
    [('v', None, 'OPTION')],
    exclude_binaries=True,
    name='fiat_core',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=True
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
