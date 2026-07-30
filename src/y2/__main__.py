import cyclopts

import y2
from y2 import asc, clean, gh, hig, pv, xcode

app = cyclopts.App(
    name="y2",
    help="Why have two when one will do?",
    version=y2.__version__,
)
app.command(asc.app)
app.command(gh.app)
app.command(hig.app)
app.command(xcode.app)
app.command(clean.clean)
app.command(pv.pv)


if __name__ == "__main__":
    app()
