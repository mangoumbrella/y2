import cyclopts

import y2
from y2 import hig

app = cyclopts.App(
    name="y2",
    help="Why have two when one will do?",
    version=y2.__version__,
)
app.command(hig.app)


if __name__ == "__main__":
    app()
