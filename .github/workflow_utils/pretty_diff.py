#!/usr/bin/env python
import difflib
import os
import sys
from glob import glob
from itertools import chain
from pathlib import Path
from typing import Iterable

import httpx


def main() -> None:
    diffs = _generate_diffs()

    github_repository = os.getenv("GITHUB_REPOSITORY")
    github_sha = os.getenv("GITHUB_SHA")
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"token {os.getenv('GITHUB_TOKEN')}",
    }

    if os.getenv("GITHUB_EVENT_NAME") == "pull_request":
        return  # TODO
    else:
        github_url = (
            f"https://api.github.com/repos/{github_repository}"
            f"/commits/{github_sha}/comments"
        )
        if not diffs:
            workflow_name = os.getenv("GITHUB_WORKFLOW", "report template changes")
            url = (
                f"https://github.com/{github_repository}"
                "/actions/workflows/template_changes.yml"
            )
            diffs.append(
                [f"The [`{workflow_name}`]({url}) workflow detected no changes."]
            )

    failed = False
    with httpx.Client() as client:
        for comment in _split_into_github_comments("".join(diff) for diff in diffs):
            response = client.post(github_url, json={"body": comment}, headers=headers)
            print(response)
            if response.status_code != 201:
                failed = True
                print("Payload length:", len(comment))
                print("Payload (first 256 characters):", comment[:256])

    if failed:
        sys.exit(2)


def _generate_diffs() -> list[list[str]]:
    base_dir = Path("templates")

    # Python 3.10: Use glob's new kwarg `root_dir`
    filenames = {
        Path(filepath).name.replace(".old.", ".")
        for filepath in chain(glob(f"{base_dir}/*.yaml"), glob(f"{base_dir}/*.json"))
    }

    diffs = []
    for filename in sorted(filenames):
        old_file = base_dir / filename.replace(".yaml", ".old.yaml").replace(
            ".json", ".old.json"
        )
        new_file = base_dir / filename
        try:
            old_content = old_file.read_text().splitlines(keepends=True)
        except FileNotFoundError:
            old_content = []
        try:
            new_content = new_file.read_text().splitlines(keepends=True)
        except FileNotFoundError:
            new_content = []

        cdk_diff_file = base_dir / f"{new_file.stem}.diff"
        try:
            cdk_diff_content = cdk_diff_file.read_text().splitlines(keepends=True)
        except FileNotFoundError:
            cdk_diff_content = []
        else:
            if cdk_diff_content and "There were no differences" in cdk_diff_content[0]:
                cdk_diff_content = []
            while cdk_diff_content and not cdk_diff_content[-1].strip():
                cdk_diff_content = cdk_diff_content[:-1]

        if not old_content and not new_content:
            diffs.append([f"File {filename!r} does not exist."])
            continue
        if diff := list(
            difflib.unified_diff(old_content, new_content, old_file.name, new_file.name)
        ):
            diffs.append(["```\n", *cdk_diff_content, "```\n\n"])
            diffs.append(["```diff\n", *diff, "```\n\n"])
    return diffs


def _split_into_github_comments(diffs: Iterable[str]) -> Iterable[str]:
    assert diffs

    comments = [""]
    mix_allowed = True
    for diff in diffs:
        if mix_allowed and len(comments[-1]) + len(diff) < 65_000:
            comments[-1] += diff
        elif len(diff) > 65_000:
            comments.extend(_split_long_diff(diff))
            mix_allowed = False
        else:
            comments.append(diff)
            mix_allowed = True

    yield from comments


def _split_long_diff(diff: str) -> Iterable[str]:
    stack_name = "unknown"

    class SubDiff:
        def __init__(self, first_line: str) -> None:
            self._lines = [first_line]

        def __len__(self) -> int:
            return sum(len(line) for line in self._lines)

        def append(self, line, /) -> None:
            self._lines.append(line)

        def extend(self, other: "SubDiff", /) -> None:
            self._lines.extend(other._lines)

        def as_comment(self, *, part: int, total: int) -> str:
            return "\n".join(
                [
                    f"**Part {part}/{total} of {stack_name}**",
                    "```diff",
                    f"+++ {stack_name}",
                    *self._lines,
                    "```\n\n",
                ]
            )

    # 1. Split the diff into single pieces.
    sub_diffs: list[SubDiff] = []
    for line in diff.splitlines():
        if line.startswith("@@") and line.endswith("@@"):
            sub_diffs.append(SubDiff(line))
        elif not sub_diffs:
            if line.startswith("+++"):
                stack_name = line.removeprefix("+++").strip()
        else:
            sub_diffs[-1].append(line)

    # 2. Try to build larger diffs that stay well below the 65_000 char limit
    merged_sub_diffs: list[SubDiff] = []
    for sub_diff in sub_diffs:
        if merged_sub_diffs and len(merged_sub_diffs[-1]) + len(sub_diff) < 60_000:
            merged_sub_diffs[-1].extend(sub_diff)
        else:
            merged_sub_diffs.append(sub_diff)

    # 3. Return the result
    for index, merged_sub_diff in enumerate(merged_sub_diffs, start=1):
        yield merged_sub_diff.as_comment(part=index, total=len(merged_sub_diffs))


def _print_help() -> None:
    print("Usage: python ./pretty_diff.py")


if __name__ == "__main__":
    if "-h" in sys.argv or "--help" in sys.argv:
        _print_help()
        sys.exit(0)

    if len(sys.argv) != 1:
        _print_help()
        sys.exit(1)

    main()
