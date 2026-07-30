# Changelog

## [Unreleased]

- New `y2 asc iap` commands to manage in-app purchase localizations on App Store Connect: `list`, `localizations`, `sync`, `submit`, `template` and `locales`.
- `y2` now depends on `pyjwt` to authenticate with the App Store Connect API.

## v2026.1

- New `y2 gh cleanup` command to cleanup unneeded branches.
- Improved startup time for commands other than `y2 hig`.
- Added a `--commit` flag to the `y2 xcode bump` command.

## v2025.4

- Added a new `y2 pv [PACKAGE]` command to print the installed PyPI package version.
- `y2` now supports running under Python 3.10-3.12.
- `y2` now depends on `yib`.

## v2025.3: Three in one

This release added three new commands:

- `y2 xcode build-and-upload`
- `y2 xcode bump`
- `y2 clean`

## v2025.2: A toast to Apple's Human Interface Guidelines

This release added the `y2 hig [download|extract]` commands, used for fetching data to feed the [Daily HIG bot](https://mastodon.social/@daily_hig).

## v2025.1

Initial release.
