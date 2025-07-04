import shutil

from y2._console import console
from y2._tempdirs import get_tempdir_root


def clean() -> None:
    root = get_tempdir_root()
    if not root.exists():
        return
    console.print(f"Deleting {root!s}")
    shutil.rmtree(root)
