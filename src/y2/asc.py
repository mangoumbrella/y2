import pathlib

import cyclopts


# These help texts are laid out by hand, so both apps opt out of the default
# reStructuredText rendering, which reflows them into paragraphs.
_CREDENTIALS_HELP = """\
Every command needs an App Store Connect API key, taken from the first of:

    --key-path FILE

    $Y2_ASC_KEY_PATH   a JSON file holding "key_id", "issuer_id" and "key"
                       (the same format fastlane's api_key_path takes)

    $Y2_ASC_KEY_ID + $Y2_ASC_ISSUER_ID + $Y2_ASC_PRIVATE_KEY_PATH

Create the key under Users and Access > Integrations in App Store Connect.\
"""

_IAP_HELP = (
    """\
Manage in-app purchases.

Localizations are read from a JSON file that you own and keep in your repo:

    {
      "bundleId": "com.example.MyApp",
      "productId": "com.example.MyApp.premium",
      "localizations": {
        "en-US":   {"name": "Remove ads", "description": "One-time purchase."},
        "zh-Hans": {"name": "移除广告", "description": "一次性付费。"}
      }
    }

What each field means:

    bundleId       the app, as it appears in App Store Connect
    productId      the in-app purchase; `iap list` prints the ones you have
    localizations  keyed by locale code; `iap locales` prints every valid one
    name           at most 30 characters, surfaced as Product.displayName
    description    at most 45 characters, required by App Store Connect even
                   if your app never displays it

Both limits and every locale code are checked before anything is sent, so
mistakes surface locally. A locale that exists on App Store Connect but is
missing from your file is reported and left alone, so copy you would rather
edit by hand is never touched.

Start a file, fill it in, preview, then send:

    y2 asc iap list --bundle-id com.example.App
    y2 asc iap template --locales en-US,ja > iap.json
    y2 asc iap localizations iap.json
    y2 asc iap sync iap.json
    y2 asc iap sync iap.json --yes
    y2 asc iap submit iap.json --yes

`sync` and `submit` only report what they would do until you pass --yes.

"""
    + _CREDENTIALS_HELP
)

app = cyclopts.App(
    name="asc",
    help=f"Talk to the App Store Connect API.\n\n{_CREDENTIALS_HELP}",
    help_format="plaintext",
)

iap = cyclopts.App(
    name="iap",
    help=_IAP_HELP,
    help_format="plaintext",
)
app.command(iap)


@iap.command(name="list")
def iap_list(*, bundle_id: str, key_path: pathlib.Path | None = None):
    """List the in-app purchases of an app.

    Parameters
    ----------
    bundle_id
        Bundle identifier of the app, e.g. com.example.MyApp.
    key_path
        App Store Connect API key JSON. Defaults to $Y2_ASC_KEY_PATH.
    """
    from . import asc_impl

    return asc_impl.iap_list(bundle_id=bundle_id, key_path=key_path)


@iap.command(name="localizations")
def iap_localizations(
    config: pathlib.Path | None = None,
    *,
    bundle_id: str | None = None,
    product_id: str | None = None,
    key_path: pathlib.Path | None = None,
):
    """Show the App Store Connect localizations of an in-app purchase.

    Parameters
    ----------
    config
        Localization config file to read the app and product ids from.
    bundle_id
        Bundle identifier of the app. Overrides the config file.
    product_id
        Product identifier of the in-app purchase. Overrides the config file.
    key_path
        App Store Connect API key JSON. Defaults to $Y2_ASC_KEY_PATH.
    """
    from . import asc_impl

    return asc_impl.iap_localizations(
        config=config, bundle_id=bundle_id, product_id=product_id, key_path=key_path
    )


@iap.command(name="sync")
def iap_sync(
    config: pathlib.Path,
    *,
    yes: bool = False,
    key_path: pathlib.Path | None = None,
):
    """Create and update in-app purchase localizations from a config file.

    Shows what would change and stops there unless --yes is given.

    Parameters
    ----------
    config
        Localization config file. See `y2 asc iap template`.
    yes
        Actually send the changes instead of only reporting them.
    key_path
        App Store Connect API key JSON. Defaults to $Y2_ASC_KEY_PATH.
    """
    from . import asc_impl

    return asc_impl.iap_sync(config=config, yes=yes, key_path=key_path)


@iap.command(name="submit")
def iap_submit(
    config: pathlib.Path | None = None,
    *,
    bundle_id: str | None = None,
    product_id: str | None = None,
    yes: bool = False,
    key_path: pathlib.Path | None = None,
):
    """Submit an in-app purchase for App Store review.

    Parameters
    ----------
    config
        Localization config file to read the app and product ids from.
    bundle_id
        Bundle identifier of the app. Overrides the config file.
    product_id
        Product identifier of the in-app purchase. Overrides the config file.
    yes
        Actually submit instead of only reporting what would be submitted.
    key_path
        App Store Connect API key JSON. Defaults to $Y2_ASC_KEY_PATH.
    """
    from . import asc_impl

    return asc_impl.iap_submit(
        config=config,
        bundle_id=bundle_id,
        product_id=product_id,
        yes=yes,
        key_path=key_path,
    )


@iap.command(name="template")
def iap_template(
    *,
    bundle_id: str = "com.example.MyApp",
    product_id: str = "",
    locales: str | None = None,
):
    """Print a starter localization config file to redirect into a JSON file.

    Without --locales you get a filled-in two-locale example to copy from. With
    --locales you get those locales with empty name and description fields;
    `sync` refuses to run until you fill them in.

    Parameters
    ----------
    bundle_id
        Bundle identifier to put in the generated config.
    product_id
        Product identifier to put in the generated config. Defaults to
        "<bundle-id>.premium".
    locales
        Comma or space separated locale codes to scaffold, e.g. "en-US,ja,de-DE".
        Run `y2 asc iap locales` for the accepted codes.
    """
    from . import asc_impl

    return asc_impl.iap_template(
        bundle_id=bundle_id, product_id=product_id, locales=locales
    )


@iap.command(name="locales")
def iap_locales():
    """List the locale codes App Store Connect accepts, with their languages.

    These are the valid keys of "localizations" in a config file. App Store
    Connect rejects anything else, and a code outside this list gets a warning
    before it is sent.
    """
    from . import asc_impl

    return asc_impl.iap_locales()
