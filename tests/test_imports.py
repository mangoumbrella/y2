import pytest

from y2.__main__ import app


def test_help():
    with pytest.raises(SystemExit) as excinfo:
        app("--help")
    assert excinfo.value.code == 0
