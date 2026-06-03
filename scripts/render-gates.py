#!/usr/bin/env python3
import argparse
import os
import pathlib
import subprocess
import sys


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate and render Janus gate reports.")
    parser.add_argument("requirement_id", help="requirement id")
    parser.add_argument("--root", default=".", help="harness-repo root")
    parser.add_argument("--check", action="store_true", help="check rendered Markdown instead of writing it")
    args = parser.parse_args()

    root = pathlib.Path(args.root).resolve()
    gate_dir = root / "requirements" / args.requirement_id / "gates"
    gate_files = sorted(gate_dir.glob("*.gate.json"))
    janus = os.environ.get("JANUS_BIN", "janus")

    if not gate_files:
        print(f"missing gate reports: {gate_dir}/*.gate.json", file=sys.stderr)
        return 1

    for gate_file in gate_files:
        markdown = gate_file.with_suffix("").with_suffix(".md")
        run([janus, "gate", "validate", str(gate_file.relative_to(root))], root)
        command = [
            janus,
            "gate",
            "render",
            "--input",
            str(gate_file.relative_to(root)),
            "--output",
            str(markdown.relative_to(root)),
        ]
        if args.check:
            command.append("--check")
        run(command, root)

    return 0


def run(command, cwd: pathlib.Path) -> None:
    subprocess.run(command, cwd=str(cwd), check=True)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except subprocess.CalledProcessError as error:
        sys.exit(error.returncode)
