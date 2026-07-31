import pathlib

import cyclopts


app = cyclopts.App(
    name="xcode",
    help="Manage Xcode project.",
)


# Laid out by hand, so opt out of the default reStructuredText rendering, which
# reflows it into paragraphs.
_BUMP_HELP = """\
Bump app versions.

Versions live in two user-defined build settings that the app target's Debug and
Release configurations both carry, with the same values in each:

    CURRENT_PROJECT_VERSION = "$(VERSION_BUILD)";
    MARKETING_VERSION = "$(VERSION_STORE)";
    VERSION_BUILD = 1;
    VERSION_STORE = 2026.1;

To add them in Xcode, select the app target, then under Build Settings use the +
button ("Add User-Defined Setting") for VERSION_BUILD and VERSION_STORE, and
point the two built-in settings at them.

Set them on the app target only. A target-level setting is invisible to other
targets, so test targets keep their own literal versions, and each name has to
appear exactly twice in project.pbxproj for bump to run.

VERSION_BUILD is the build number, bumped on every upload. VERSION_STORE is the
version the App Store shows, written as <year>.<release> and bumped only when
you ship:

    y2 xcode bump                              VERSION_BUILD 1 to 2
    y2 xcode bump --store-version              VERSION_STORE 2026.1 to 2026.2
    y2 xcode bump --store-version \\
                  --store-version-bump-year    VERSION_STORE 2026.2 to 2027.1\
"""


@app.command(help=_BUMP_HELP, help_format="plaintext")
def bump(
    xcode_project: pathlib.Path | None = None,
    store_version: bool = False,
    store_version_bump_year: bool = False,
    commit: bool = False,
):
    """Bump app versions.

    Parameters
    ----------
    xcode_project
        The .xcodeproj directory. Defaults to the one in the current directory.
    store_version
        Also bump VERSION_STORE, for a release that reaches the App Store.
    store_version_bump_year
        With --store-version, bump the year instead of the release number.
        Never lands on a year earlier than the current one.
    commit
        Commit the bump. Requires a clean working tree.
    """
    from . import xcode_impl

    return xcode_impl.bump(
        xcode_project=xcode_project,
        store_version=store_version,
        store_version_bump_year=store_version_bump_year,
        commit=commit,
    )


@app.command
def build_and_upload(project_dir: pathlib.Path | None = None):
    """Build and upload the project using fastlane."""
    from . import xcode_impl

    return xcode_impl.build_and_upload(project_dir=project_dir)
