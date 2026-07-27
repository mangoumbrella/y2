import cyclopts

app = cyclopts.App(
    name="gh",
    help="Utilities that wrap the GitHub CLI (`gh`).",
)


@app.command
def cleanup(base_branch: str | None = None, dry_run: bool = False):
    """Delete local branches whose pull request has already been merged."""
    from . import gh_impl

    return gh_impl.cleanup(base_branch=base_branch, dry_run=dry_run)
