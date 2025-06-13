import cyclopts

import y2

app = cyclopts.App(
    name="y2",
    help="Why have two when one will do?",
    version=y2.__version__,
)


if __name__ == "__main__":
    app()
