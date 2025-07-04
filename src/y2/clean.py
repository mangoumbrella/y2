def clean() -> None:
    """Clean up temp files used by 2."""
    from . import clean_tmpl

    return clean_tmpl.clean()
