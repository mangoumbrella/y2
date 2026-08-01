# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html


from pathlib import Path

from y2.__main__ import app as y2_app

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "y2"
copyright = "2025, Mango Umbrella LLC and the y2 authors"
author = "Mango Umbrella LLC and the y2 authors"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "myst_parser",
    "sphinx_rtd_theme",
]

templates_path = ["_templates"]
exclude_patterns = []

# The generated command reference links to its own headings, all the way down
# to `y2 asc iap template`.
myst_heading_anchors = 6


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_rtd_theme"


# -- Generated pages ---------------------------------------------------------

_DOCS = Path(__file__).parent
_ROOT = _DOCS.parent


def _write_generated_pages(_):
    """Write the pages that are derived from the repository.

    The command reference comes from the cyclopts app, so it cannot drift from
    the CLI, and the changelog is the one at the root rather than a copy of it.
    Both are written before Sphinx reads the source directory, and neither is
    checked in.
    """
    (_DOCS / "commands.md").write_text(y2_app.generate_docs(), encoding="utf-8")
    (_DOCS / "changelog.md").write_text(
        (_ROOT / "CHANGELOG.md").read_text(encoding="utf-8"), encoding="utf-8"
    )


def setup(app):
    app.connect("builder-inited", _write_generated_pages)
