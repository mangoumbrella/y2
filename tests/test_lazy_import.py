import sys
import subprocess
import textwrap


def test_lazy_import():
    code = textwrap.dedent(
        """
        import contextlib
        import io
        import sys
        import cyclopts

        def show_help(target):
            with contextlib.redirect_stdout(io.StringIO()):
                with contextlib.suppress(SystemExit):
                    target(["--help"])

        # There is not much help when the modules are imported after running --help by cyclopts.
        dummy_app = cyclopts.App()
        show_help(dummy_app)
        modules_before = set(sys.modules)

        from y2.__main__ import app
        show_help(app)
        # Exclude modules from y2 itself.
        modules_after = set(
            m
            for m in sys.modules
            if m != "y2" and not m.startswith("y2.")
        )

        if modules_before != modules_after:
            print("The following modules could be lazily imported:")
            for m in sorted(modules_after - modules_before):
                print(f"  {m}")
            sys.stdout.flush()
            sys.exit(1)
        """
    )
    process = subprocess.run(
        [sys.executable, "-c", code],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    assert not process.returncode, process.stdout
