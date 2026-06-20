#!/usr/bin/env python3
from __future__ import annotations
import argparse
import json
import re
import sys
from pathlib import Path


TICKET_PREFIX = re.compile(r"^\[([^\]\s]+-[0-9]+)]\s+(.+)$")
CONVENTIONAL_SUBJECT = re.compile(r"^[a-z][a-z0-9-]*\([a-z0-9._-]+\): [^\s].+")
VAGUE_SUBJECTS = {"update", "fix bug", "wip"}
REQUIRED_BODY_SECTIONS = (
    "## Task",
    "## What Changed",
    "## Key Decisions",
    "## Validation",
    "## Gates / Evidence",
    "## Risks / Follow-up",
    "## Review Guidance",
)
ALLOWED_AGENT_TRAILERS = {
    "Agent-Task",
    "Agent-Decision",
    "Agent-Limitation",
}


def validate_metadata(title: str, body: str, commits: list[dict]) -> list[str]:
    problems: list[str] = []
    ticket_id = validate_title(title, problems)
    validate_body(body, ticket_id, problems)
    validate_commits(commits, problems)
    return problems


def validate_title(title: str, problems: list[str]) -> str | None:
    match = TICKET_PREFIX.match((title or "").strip())
    if not match:
        problems.append(
            "PR title must start with [TICKET-ID], for example: "
            "[TEAM-38] docs(harness): add PR metadata policy"
        )
        return None

    ticket_id = match.group(1)
    subject = match.group(2).strip()
    if not is_valid_subject(subject):
        problems.append(
            "PR title after [TICKET-ID] must use Conventional Commits, "
            "for example: [TEAM-38] docs(harness): add PR metadata policy"
        )
    return ticket_id


def validate_body(body: str, ticket_id: str | None, problems: list[str]) -> None:
    body = body or ""
    for section in REQUIRED_BODY_SECTIONS:
        if section not in body:
            problems.append(f"PR body is missing section: {section}")

    if ticket_id and ticket_id not in body:
        problems.append(f"PR body must reference ticket id: {ticket_id}")

    if "## Validation" in body and _section_is_empty(body, "## Validation"):
        problems.append("PR body ## Validation section must describe checks run or state N/A with reason")

    if "## Gates / Evidence" in body and _section_is_empty(body, "## Gates / Evidence"):
        problems.append("PR body ## Gates / Evidence section must describe evidence or state N/A with reason")


def validate_commits(commits: list[dict], problems: list[str]) -> None:
    for commit in commits or []:
        if is_bot_commit(commit):
            continue

        sha = (commit.get("sha") or "")[:12] or "<unknown>"
        message = ((commit.get("commit") or {}).get("message") or "").strip()
        subject = message.splitlines()[0].strip() if message else ""
        if not is_valid_subject(subject):
            problems.append(f"Commit {sha} subject must use Conventional Commits: {subject or '<empty>'}")

        validate_agent_trailers(sha, message, problems)


def validate_agent_trailers(sha: str, message: str, problems: list[str]) -> None:
    for line in message.splitlines()[1:]:
        stripped = line.strip()
        if not stripped.startswith("Agent-") or ":" not in stripped:
            continue
        key = stripped.split(":", 1)[0]
        if key not in ALLOWED_AGENT_TRAILERS:
            problems.append(
                f"Commit {sha} uses unsupported Agent trailer {key}; "
                f"allowed: {', '.join(sorted(ALLOWED_AGENT_TRAILERS))}"
            )


def is_valid_subject(subject: str) -> bool:
    normalized = (subject or "").strip().lower()
    if normalized in VAGUE_SUBJECTS or normalized.startswith("[wip]"):
        return False
    return bool(CONVENTIONAL_SUBJECT.match(subject or ""))


def is_bot_commit(commit: dict) -> bool:
    login = ((commit.get("author") or {}).get("login") or "").lower()
    if login.endswith("[bot]") or login == "github-actions":
        return True

    author = ((commit.get("commit") or {}).get("author") or {}).get("name") or ""
    return author.lower().endswith("[bot]")


def _section_is_empty(body: str, section: str) -> bool:
    start = body.find(section)
    if start == -1:
        return False
    start += len(section)
    next_section = body.find("\n## ", start)
    content = body[start:] if next_section == -1 else body[start:next_section]
    stripped = content.strip()
    return not stripped or stripped in {"-", "TBD", "TODO"}


def load_json(path: str) -> object:
    if path == "-":
        return json.load(sys.stdin)
    with Path(path).open("r", encoding="utf-8") as file:
        return json.load(file)


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Spark PR metadata policy.")
    parser.add_argument("--title", required=True, help="Pull request title")
    parser.add_argument("--body-file", required=True, help="File containing pull request body")
    parser.add_argument("--commits-file", required=True, help="JSON file containing pull request commits")
    args = parser.parse_args()

    body = Path(args.body_file).read_text(encoding="utf-8")
    commits = load_json(args.commits_file)
    if not isinstance(commits, list):
        print("--commits-file must contain a JSON array", file=sys.stderr)
        return 1

    problems = validate_metadata(args.title, body, commits)
    if problems:
        print("PR metadata policy failed:", file=sys.stderr)
        for problem in problems:
            print(f"- {problem}", file=sys.stderr)
        return 1

    print("PR metadata policy passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
