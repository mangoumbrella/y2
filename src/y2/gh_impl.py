import json
import shutil
import subprocess

from y2._config import console


def cleanup(base_branch: str | None = None, dry_run: bool = False) -> None:
    _preflight()

    if not base_branch:
        base_branch = _get_default_branch()

    current_branch = _git(["rev-parse", "--abbrev-ref", "HEAD"]).strip()

    local_branches = _git(
        ["for-each-ref", "--format=%(refname:short)", "refs/heads/"]
    ).splitlines()
    candidates = [b for b in local_branches if b not in (base_branch, current_branch)]
    if not candidates:
        console.print("No local branches to clean up.")
        return

    merged_branches = _get_merged_pr_branches()
    to_delete = [b for b in candidates if b in merged_branches]
    if not to_delete:
        console.print("No local branches with merged PRs found.")
        return

    for branch in to_delete:
        if dry_run:
            console.print(f"Would delete [cyan]{branch}[/cyan] (PR merged)")
            continue

        result = subprocess.run(
            ["git", "branch", "-D", branch], capture_output=True, text=True, check=False
        )
        if result.returncode != 0:
            console.warning(f"Failed to delete {branch}: {result.stderr.strip()}")
        else:
            console.print(f"Deleted [cyan]{branch}[/cyan] (PR merged)")


def _preflight() -> None:
    if shutil.which("gh") is None:
        console.fatal(
            "The GitHub CLI (`gh`) is not installed. See https://cli.github.com."
        )

    result = subprocess.run(
        ["gh", "auth", "status"], capture_output=True, text=True, check=False
    )
    if result.returncode != 0:
        console.fatal(result.stderr.strip())


def _get_default_branch() -> str:
    result = subprocess.run(
        ["git", "symbolic-ref", "--short", "refs/remotes/origin/HEAD"],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode == 0 and result.stdout.strip():
        return result.stdout.strip().removeprefix("origin/")

    result = subprocess.run(
        [
            "gh",
            "repo",
            "view",
            "--json",
            "defaultBranchRef",
            "-q",
            ".defaultBranchRef.name",
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode == 0 and result.stdout.strip():
        return result.stdout.strip()

    return "main"


def _get_merged_pr_branches() -> set[str]:
    result = subprocess.run(
        [
            "gh",
            "pr",
            "list",
            "--state",
            "merged",
            "--limit",
            "1000",
            "--json",
            "headRefName",
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        console.fatal(f"Failed to list merged PRs via `gh`:\n{result.stderr}")
    return {item["headRefName"] for item in json.loads(result.stdout)}


def _git(args: list[str]) -> str:
    result = subprocess.run(["git", *args], capture_output=True, text=True, check=False)
    if result.returncode != 0:
        console.fatal(f"Failed to run `git {' '.join(args)}`:\n{result.stderr}")
    return result.stdout
