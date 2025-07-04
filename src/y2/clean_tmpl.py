import shutil

from y2._config import console, get_tempdir_root


def clean() -> None:
    root = get_tempdir_root()
    if not root.exists():
        return
    console.print(f"Deleting {root!s}")
    shutil.rmtree(root)
