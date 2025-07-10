import pathlib

import cyclopts


app = cyclopts.App(
    name="xcode",
    help="Manage Xcode project.",
)


@app.command
def bump(
    xcode_project: pathlib.Path | None = None,
    store_version: bool = False,
    store_version_bump_year: bool = False,
    commit: bool = False,
):
    """Bump app versions."""
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
