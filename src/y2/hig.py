import pathlib

import cyclopts


app = cyclopts.App(
    name="hig",
    help="Download and extract information from Apple's Human Interface Guidelines for the Daily HIG bot.",
)


@app.command()
def download(
    to: pathlib.Path | None = None,
    num_threads: int = 8,
    website_loading_wait_seconds: float = 5.0,
):
    """Download Apple's HIG to a directory."""
    from . import _hig

    return _hig.download(
        to=to,
        num_threads=num_threads,
        website_loading_wait_seconds=website_loading_wait_seconds,
    )


@app.command()
def extract(hig_directory: pathlib.Path):
    """Extract information from downloaded Apple's HIG."""
    from . import _hig

    return _hig.extract(hig_directory=hig_directory)
