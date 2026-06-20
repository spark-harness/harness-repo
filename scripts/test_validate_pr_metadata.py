#!/usr/bin/env python3
import importlib.util
import pathlib
import unittest


SCRIPT = pathlib.Path(__file__).with_name("validate-pr-metadata.py")
SPEC = importlib.util.spec_from_file_location("validate_pr_metadata", SCRIPT)
validate_pr_metadata = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(validate_pr_metadata)


VALID_BODY = """## Task
TEAM-38

## What Changed
Add PR metadata policy validation.

## Key Decisions
Use [TEAM-38] title prefix and Conventional Commits summary.

## Validation
python3 scripts/test_validate_pr_metadata.py

## Gates / Evidence
N/A - metadata policy only.

## Risks / Follow-up
N/A

## Review Guidance
Check title, body, and commit diagnostics.
"""


class ValidatePrMetadataTest(unittest.TestCase):
    def test_valid_metadata_passes(self):
        problems = validate_pr_metadata.validate_metadata(
            title="[TEAM-38] docs(harness): add PR metadata policy",
            body=VALID_BODY,
            commits=[
                {
                    "sha": "abc123",
                    "commit": {
                        "message": (
                            "docs(harness): add PR metadata policy\n\n"
                            "Agent-Task: TEAM-38\n"
                            "Agent-Decision: enforce PR title prefix for traceability\n"
                        )
                    },
                    "author": {"login": "forest"},
                }
            ],
        )

        self.assertEqual([], problems)

    def test_title_requires_ticket_prefix(self):
        problems = validate_pr_metadata.validate_metadata(
            title="docs(harness): add PR metadata policy",
            body=VALID_BODY,
            commits=[],
        )

        self.assertTrue(any("PR title must start with [TICKET-ID]" in problem for problem in problems))

    def test_body_requires_template_sections(self):
        problems = validate_pr_metadata.validate_metadata(
            title="[TEAM-38] docs(harness): add PR metadata policy",
            body="## Task\nTEAM-38\n",
            commits=[],
        )

        self.assertTrue(any("PR body is missing section: ## Validation" in problem for problem in problems))

    def test_commit_subject_rejects_vague_summary(self):
        problems = validate_pr_metadata.validate_metadata(
            title="[TEAM-38] docs(harness): add PR metadata policy",
            body=VALID_BODY,
            commits=[
                {
                    "sha": "def456",
                    "commit": {"message": "update"},
                    "author": {"login": "forest"},
                }
            ],
        )

        self.assertTrue(any("def456" in problem and "Conventional Commits" in problem for problem in problems))

    def test_ticket_prefix_is_not_limited_to_len(self):
        problems = validate_pr_metadata.validate_metadata(
            title="[OPS_foo-123] chore(ci): tune PR metadata policy",
            body=VALID_BODY.replace("TEAM-38", "OPS_foo-123"),
            commits=[],
        )

        self.assertEqual([], problems)

    def test_conventional_type_is_not_limited_to_common_examples(self):
        problems = validate_pr_metadata.validate_metadata(
            title="[TEAM-38] ci(harness): tune PR metadata policy",
            body=VALID_BODY,
            commits=[
                {
                    "sha": "ci123",
                    "commit": {"message": "build(harness): update action pin"},
                    "author": {"login": "forest"},
                }
            ],
        )

        self.assertEqual([], problems)

    def test_bot_commit_is_exempt_from_subject_policy(self):
        problems = validate_pr_metadata.validate_metadata(
            title="[TEAM-38] docs(harness): add PR metadata policy",
            body=VALID_BODY,
            commits=[
                {
                    "sha": "bot123",
                    "commit": {"message": "sync generated output"},
                    "author": {"login": "github-actions[bot]"},
                }
            ],
        )

        self.assertEqual([], problems)


if __name__ == "__main__":
    unittest.main()
