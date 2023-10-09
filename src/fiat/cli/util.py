"""Util for cli."""

from pathlib import Path


def file_path_check(path):
    """Cli friendly version of path checking."""
    root = Path.cwd()
    path = Path(path)
    if not path.is_absolute():
        path = Path(root, path)
    if not (path.is_file() | path.is_dir()):
        raise FileNotFoundError(f"{str(path)} is not a valid path")
    return path
