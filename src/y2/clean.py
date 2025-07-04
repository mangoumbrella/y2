def clean() -> None:
    """Clean up temp files used by 2."""
    from . import _clean

    return _clean.clean()
