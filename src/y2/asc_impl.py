import json
import os
import pathlib
import time
import urllib.error
import urllib.request

from y2._config import console


_HOST = "https://api.appstoreconnect.apple.com"

# App Store Connect rejects longer values.
_NAME_LIMIT = 30
_DESCRIPTION_LIMIT = 45

# App Store metadata locales, used to catch typos before they reach the API.
# Apple adds to this occasionally, so an unknown code only warns.
_LOCALES = {
    "ar-SA": "Arabic",
    "ca": "Catalan",
    "cs": "Czech",
    "da": "Danish",
    "de-DE": "German",
    "el": "Greek",
    "en-AU": "English (Australia)",
    "en-CA": "English (Canada)",
    "en-GB": "English (U.K.)",
    "en-US": "English (U.S.)",
    "es-ES": "Spanish (Spain)",
    "es-MX": "Spanish (Mexico)",
    "fi": "Finnish",
    "fr-CA": "French (Canada)",
    "fr-FR": "French",
    "he": "Hebrew",
    "hi": "Hindi",
    "hr": "Croatian",
    "hu": "Hungarian",
    "id": "Indonesian",
    "it": "Italian",
    "ja": "Japanese",
    "ko": "Korean",
    "ms": "Malay",
    "nl-NL": "Dutch",
    "no": "Norwegian",
    "pl": "Polish",
    "pt-BR": "Portuguese (Brazil)",
    "pt-PT": "Portuguese (Portugal)",
    "ro": "Romanian",
    "ru": "Russian",
    "sk": "Slovak",
    "sv": "Swedish",
    "th": "Thai",
    "tr": "Turkish",
    "uk": "Ukrainian",
    "vi": "Vietnamese",
    "zh-Hans": "Chinese (Simplified)",
    "zh-Hant": "Chinese (Traditional)",
}
_KNOWN_LOCALES = frozenset(_LOCALES)

_TEMPLATE_COMMENT = (
    f"name is at most {_NAME_LIMIT} characters, description at most "
    f"{_DESCRIPTION_LIMIT}. Run `y2 asc iap locales` for the locale codes."
)

_TEMPLATE_LOCALIZATIONS = {
    "en-US": {"name": "Remove ads", "description": "One-time purchase."},
    "zh-Hans": {"name": "移除广告", "description": "一次性付费。"},
}


def iap_list(*, bundle_id: str, key_path: pathlib.Path | None) -> None:
    token = _bearer_token(key_path)
    app_id = _find_app_id(token, bundle_id)
    purchases = _get(token, f"/v1/apps/{app_id}/inAppPurchasesV2?limit=200")["data"]
    if not purchases:
        console.print(f"No in-app purchases found for [cyan]{bundle_id}[/cyan].")
        return
    for purchase in purchases:
        attributes = purchase["attributes"]
        console.print(
            f"[cyan]{attributes['productId']}[/cyan] "
            f"id={purchase['id']} "
            f"state={attributes.get('state')} "
            f"name={attributes.get('name')!r}"
        )


def iap_localizations(
    *,
    config: pathlib.Path | None,
    bundle_id: str | None,
    product_id: str | None,
    key_path: pathlib.Path | None,
) -> None:
    bundle_id, product_id, _ = _resolve_target(config, bundle_id, product_id)
    token = _bearer_token(key_path)
    purchase = _find_purchase(token, bundle_id, product_id)
    current = _current_localizations(token, purchase["id"])
    console.print(
        f"[cyan]{product_id}[/cyan] id={purchase['id']} "
        f"state={purchase['attributes'].get('state')}"
    )
    if not current:
        console.print("No localizations yet.")
        return
    for locale in sorted(current):
        attributes = current[locale]["attributes"]
        console.print(
            f"  {locale:<8} {attributes['name']!r} {attributes.get('description')!r}"
        )


def iap_sync(*, config: pathlib.Path, yes: bool, key_path: pathlib.Path | None) -> None:
    bundle_id, product_id, localizations = _resolve_target(config, None, None)
    _validate(localizations)

    token = _bearer_token(key_path)
    purchase = _find_purchase(token, bundle_id, product_id)
    current = _current_localizations(token, purchase["id"])

    creates, updates = [], []
    for locale, copy in sorted(localizations.items()):
        existing = current.get(locale)
        if existing is None:
            creates.append(locale)
        elif (
            existing["attributes"]["name"] != copy["name"]
            or existing["attributes"].get("description") != copy["description"]
        ):
            updates.append(locale)

    untouched = sorted(set(current) - set(localizations))
    console.print(
        f"create [green]{len(creates)}[/green], "
        f"update [yellow]{len(updates)}[/yellow], "
        f"unchanged {len(localizations) - len(creates) - len(updates)}"
    )
    if untouched:
        console.print(
            "[dim]on App Store Connect but not in the config: "
            f"{', '.join(untouched)}[/dim]"
        )

    if not creates and not updates:
        console.print("Nothing to do.")
        return

    console.print()
    for locale in creates:
        _print_change(locale, None, localizations[locale])
    for locale in updates:
        _print_change(locale, current[locale]["attributes"], localizations[locale])

    console.print()
    if not yes:
        console.print("Dry run. Re-run with [cyan]--yes[/cyan] to send these changes.")
        return

    for locale in creates:
        copy = localizations[locale]
        _post(
            token,
            "/v1/inAppPurchaseLocalizations",
            {
                "data": {
                    "type": "inAppPurchaseLocalizations",
                    "attributes": {
                        "locale": locale,
                        "name": copy["name"],
                        "description": copy["description"],
                    },
                    "relationships": {
                        "inAppPurchaseV2": {
                            "data": {"type": "inAppPurchases", "id": purchase["id"]}
                        }
                    },
                }
            },
        )
        console.print(f"created [cyan]{locale}[/cyan]")

    for locale in updates:
        copy = localizations[locale]
        localization_id = current[locale]["id"]
        _patch(
            token,
            f"/v1/inAppPurchaseLocalizations/{localization_id}",
            {
                "data": {
                    "type": "inAppPurchaseLocalizations",
                    "id": localization_id,
                    "attributes": {
                        "name": copy["name"],
                        "description": copy["description"],
                    },
                }
            },
        )
        console.print(f"updated [cyan]{locale}[/cyan]")

    console.print("\nRun [cyan]y2 asc iap submit[/cyan] to send it for review.")


def iap_submit(
    *,
    config: pathlib.Path | None,
    bundle_id: str | None,
    product_id: str | None,
    yes: bool,
    key_path: pathlib.Path | None,
) -> None:
    bundle_id, product_id, _ = _resolve_target(config, bundle_id, product_id)
    token = _bearer_token(key_path)
    purchase = _find_purchase(token, bundle_id, product_id)
    console.print(
        f"[cyan]{product_id}[/cyan] id={purchase['id']} "
        f"state={purchase['attributes'].get('state')}"
    )
    if not yes:
        console.print(
            "Dry run. Re-run with [cyan]--yes[/cyan] to submit this in-app purchase "
            "for App Store review."
        )
        return
    _post(
        token,
        "/v1/inAppPurchaseSubmissions",
        {
            "data": {
                "type": "inAppPurchaseSubmissions",
                "relationships": {
                    "inAppPurchaseV2": {
                        "data": {"type": "inAppPurchases", "id": purchase["id"]}
                    }
                },
            }
        },
    )
    console.print("Submitted for review.")


def iap_template(*, bundle_id: str, product_id: str, locales: str | None) -> None:
    if locales:
        wanted = [code.strip() for code in locales.replace(",", " ").split()]
        unknown = [code for code in wanted if code not in _KNOWN_LOCALES]
        if unknown:
            console.fatal(
                f"Not App Store locale codes: {', '.join(unknown)}\n"
                "Run `y2 asc iap locales` for the list."
            )
        # Empty values on purpose: `sync` refuses to run until they are filled in.
        body = {code: {"name": "", "description": ""} for code in wanted}
    else:
        body = _TEMPLATE_LOCALIZATIONS

    # Straight to stdout, not the shared stderr console: this output is meant to
    # be redirected into a file or piped.
    print(
        json.dumps(
            {
                "bundleId": bundle_id,
                "productId": product_id or f"{bundle_id}.premium",
                "_comment": _TEMPLATE_COMMENT,
                "localizations": body,
            },
            indent=2,
            ensure_ascii=False,
        )
    )


def iap_locales() -> None:
    # Stdout too, so the list can be grepped.
    for code, language in _LOCALES.items():
        print(f"{code:<8} {language}")


_FIELDS = ("name", "description")


def _print_change(locale: str, before: dict | None, after: dict) -> None:
    """Report one localization the way `git diff` reports a hunk."""
    if before is None:
        console.print(f"[green]+ {locale}[/green]")
        for field in _FIELDS:
            console.print(f"[green]+     {field:<12} {_markup_safe(after[field])}[/green]")
        return

    console.print(f"[yellow]~ {locale}[/yellow]")
    for field in _FIELDS:
        old = before.get(field) or ""
        new = after[field]
        if old == new:
            console.print(f"[dim]      {field:<12} {_markup_safe(old)}[/dim]")
        else:
            console.print(f"[red]-     {field:<12} {_markup_safe(old)}[/red]")
            console.print(f"[green]+     {field:<12} {_markup_safe(new)}[/green]")


def _markup_safe(text: str) -> str:
    """Stop square brackets in the copy being read as console markup."""
    return text.replace("[", r"\[")


def _resolve_target(
    config: pathlib.Path | None, bundle_id: str | None, product_id: str | None
) -> tuple[str, str, dict]:
    localizations: dict = {}
    if config is not None:
        if not config.exists():
            console.fatal(f"Config file not found: {config}")
        try:
            parsed = json.loads(config.read_text(encoding="utf-8"))
        except json.JSONDecodeError as error:
            console.fatal(f"Config file is not valid JSON: {error}")
        bundle_id = bundle_id or parsed.get("bundleId")
        product_id = product_id or parsed.get("productId")
        localizations = parsed.get("localizations") or {}
        if not isinstance(localizations, dict):
            console.fatal('Config file field "localizations" must be an object.')
    if not bundle_id:
        console.fatal("Missing bundle id. Pass --bundle-id or a config file.")
    if not product_id:
        console.fatal("Missing product id. Pass --product-id or a config file.")
    return bundle_id, product_id, localizations


def _validate(localizations: dict) -> None:
    if not localizations:
        console.fatal('Config file has no "localizations" entries.')
    problems = []
    for locale, copy in sorted(localizations.items()):
        if locale not in _KNOWN_LOCALES:
            console.warning(f"{locale}: not a known App Store locale, sending anyway.")
        if not isinstance(copy, dict):
            problems.append(f"{locale}: entry must be an object")
            continue
        name = copy.get("name") or ""
        description = copy.get("description") or ""
        if not name:
            problems.append(f"{locale}: name is empty")
        if not description:
            problems.append(f"{locale}: description is empty")
        if len(name) > _NAME_LIMIT:
            problems.append(
                f"{locale}: name is {len(name)} characters, limit is {_NAME_LIMIT} ({name})"
            )
        if len(description) > _DESCRIPTION_LIMIT:
            problems.append(
                f"{locale}: description is {len(description)} characters, "
                f"limit is {_DESCRIPTION_LIMIT} ({description})"
            )
    if problems:
        console.fatal(
            f"{len(problems)} problem(s) found, nothing was sent:\n  "
            + "\n  ".join(problems)
        )


def _bearer_token(key_path: pathlib.Path | None) -> str:
    import jwt

    key_id, issuer_id, private_key = _load_credentials(key_path)
    now = int(time.time())
    return jwt.encode(
        {
            "iss": issuer_id,
            "iat": now,
            "exp": now + 900,
            "aud": "appstoreconnect-v1",
        },
        private_key,
        algorithm="ES256",
        headers={"kid": key_id, "typ": "JWT"},
    )


def _load_credentials(key_path: pathlib.Path | None) -> tuple[str, str, str]:
    """Resolve an API key from a fastlane-style JSON file or the environment."""
    path = key_path or (
        pathlib.Path(os.environ["Y2_ASC_KEY_PATH"]) if os.environ.get("Y2_ASC_KEY_PATH") else None
    )
    if path is not None:
        if not path.exists():
            console.fatal(f"App Store Connect key not found: {path}")
        try:
            key = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as error:
            console.fatal(f"App Store Connect key is not valid JSON: {error}")
        missing = [f for f in ("key_id", "issuer_id", "key") if not key.get(f)]
        if missing:
            console.fatal(f"Key file {path} is missing: {', '.join(missing)}")
        return key["key_id"], key["issuer_id"], key["key"]

    key_id = os.environ.get("Y2_ASC_KEY_ID")
    issuer_id = os.environ.get("Y2_ASC_ISSUER_ID")
    private_key = os.environ.get("Y2_ASC_PRIVATE_KEY")
    private_key_path = os.environ.get("Y2_ASC_PRIVATE_KEY_PATH")
    if private_key_path and not private_key:
        private_key = pathlib.Path(private_key_path).read_text(encoding="utf-8")
    if key_id and issuer_id and private_key:
        return key_id, issuer_id, private_key

    console.fatal(
        "No App Store Connect API key. Pass --key-path, or set $Y2_ASC_KEY_PATH to a JSON "
        'file with "key_id", "issuer_id" and "key", or set $Y2_ASC_KEY_ID, $Y2_ASC_ISSUER_ID '
        "and $Y2_ASC_PRIVATE_KEY_PATH."
    )


def _find_app_id(token: str, bundle_id: str) -> str:
    apps = _get(token, f"/v1/apps?filter[bundleId]={bundle_id}&limit=200")["data"]
    if not apps:
        console.fatal(f"No app found with bundle id {bundle_id}.")
    return apps[0]["id"]


def _find_purchase(token: str, bundle_id: str, product_id: str) -> dict:
    app_id = _find_app_id(token, bundle_id)
    purchases = _get(token, f"/v1/apps/{app_id}/inAppPurchasesV2?limit=200")["data"]
    for purchase in purchases:
        if purchase["attributes"]["productId"] == product_id:
            return purchase
    known = ", ".join(p["attributes"]["productId"] for p in purchases) or "(none)"
    console.fatal(
        f"No in-app purchase with product id {product_id}.\nAvailable: {known}"
    )


def _current_localizations(token: str, purchase_id: str) -> dict:
    # The localizations hang off the v2 in-app purchase resource, not v1.
    page = _get(
        token, f"/v2/inAppPurchases/{purchase_id}/inAppPurchaseLocalizations?limit=200"
    )
    return {entry["attributes"]["locale"]: entry for entry in page["data"]}


def _get(token: str, path: str) -> dict:
    return _request("GET", token, path, None)


def _post(token: str, path: str, body: dict) -> dict:
    return _request("POST", token, path, body)


def _patch(token: str, path: str, body: dict) -> dict:
    return _request("PATCH", token, path, body)


def _request(method: str, token: str, path: str, body: dict | None) -> dict:
    request = urllib.request.Request(
        _HOST + path,
        data=json.dumps(body).encode("utf-8") if body is not None else None,
        method=method,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(request) as response:
            raw = response.read()
    except urllib.error.HTTPError as error:
        console.fatal(
            f"{method} {path} returned {error.code}\n  " + _error_detail(error.read())
        )
    except urllib.error.URLError as error:
        console.fatal(f"{method} {path} failed: {error.reason}")
    return json.loads(raw) if raw else {}


def _error_detail(payload: bytes) -> str:
    try:
        errors = json.loads(payload).get("errors", [])
    except (json.JSONDecodeError, AttributeError):
        return payload.decode("utf-8", "replace")
    return "\n  ".join(
        f"{error.get('title')}: {error.get('detail')}" for error in errors
    )
