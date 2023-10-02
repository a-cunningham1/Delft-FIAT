from pathlib import Path


def file_path_check(ctx, _, path):
    """this is a cli friendly version of the method
    'generic_path_check' from fiat.util
    """

    root = Path.cwd()
    path = Path(path)
    if not path.is_absolute():
        path = Path(root, path)
    if not (path.is_file() | path.is_dir()):
        raise FileNotFoundError(f"{str(path)} is not a valid path")
    return path
