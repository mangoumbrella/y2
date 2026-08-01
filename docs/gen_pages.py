"""Generate the documentation pages that are derived from the repository.

Run by mkdocs-gen-files during the build, so the command reference never drifts
from the CLI and the changelog is not duplicated.
"""

import pathlib

import mkdocs_gen_files

from y2.__main__ import app


_ROOT = pathlib.Path(__file__).parent.parent

with mkdocs_gen_files.open("commands.md", "w") as f:
    f.write(app.generate_docs())

with mkdocs_gen_files.open("changelog.md", "w") as f:
    f.write((_ROOT / "CHANGELOG.md").read_text(encoding="utf-8"))
