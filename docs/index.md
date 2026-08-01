# y2

Why have two when one will do?

`y2` is a command line tool that collects the small chores that come up while
shipping an app: talking to App Store Connect, bumping Xcode versions, tidying
up merged branches, and a few odds and ends.

## Install

`y2` is on [PyPI](https://pypi.org/project/y2) and needs Python 3.10 or newer.

Run it without installing anything:

```console
uvx y2 --help
```

Or install it as a tool:

```console
uv tool install y2
```

```console
pipx install y2
```

## A quick tour

Publish in-app purchase localizations from a file you keep in your repo:

```console
y2 asc iap template --locales en-US,ja > iap.json
y2 asc iap sync iap.json          # shows what would change
y2 asc iap sync iap.json --yes    # sends it
```

Bump the build number of an Xcode project, and commit it:

```console
y2 xcode bump --commit
```

Delete the local branches whose pull request has already been merged:

```console
y2 gh cleanup --dry-run
```

Print the version of an installed package:

```console
y2 pv y2
```

Every command, flag and environment variable is listed under
[Commands](commands.md), generated from `y2` itself.

## Source

`y2` lives at [github.com/mangoumbrella/y2](https://github.com/mangoumbrella/y2)
and is licensed under the Apache License 2.0.
