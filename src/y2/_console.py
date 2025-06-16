import sys
from typing import Any, overload

import rich.console
from rich.console import JustifyMethod, OverflowMethod
from rich.style import Style


class Console(rich.console.Console):
    @overload
    def fatal(
        self,
        *objects: Any,
        sep: str = " ",
        end: str = "\n",
        style: str | Style | None = None,
        justify: JustifyMethod | None = None,
        overflow: OverflowMethod | None = None,
        no_wrap: bool | None = None,
        emoji: bool | None = None,
        markup: bool | None = None,
        highlight: bool | None = None,
        width: int | None = None,
        height: int | None = None,
        crop: bool = True,
        soft_wrap: bool | None = None,
        new_line_start: bool = False,
    ) -> None: ...
    def fatal(self, *args, **kwargs) -> None:
        self.print(*args, **kwargs)
        sys.exit(1)


console = Console(stderr=True)
