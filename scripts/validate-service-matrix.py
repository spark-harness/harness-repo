#!/usr/bin/env python3
import argparse
import pathlib
import sys

import yaml


ALLOWED_PLACEHOLDERS = {
    "business-repo",
    "business-repo-name",
    "idl-repo",
    "idl-repo-name",
    "project-name",
    "requirement-id",
    "module-name",
    "service-name",
}


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Harness service matrix.")
    parser.add_argument("--root", default=".", help="harness-repo root")
    args = parser.parse_args()

    root = pathlib.Path(args.root).resolve()
    matrix_path = root / ".service-matrix" / "dependencies.yaml"
    problems = []

    if not matrix_path.exists():
        print(f"missing file: {matrix_path}", file=sys.stderr)
        return 1

    with matrix_path.open("r", encoding="utf-8") as file:
        matrix = yaml.safe_load(file) or {}

    workspace = root / matrix.get("workspace", "..")
    business_repo = workspace / matrix.get("business_repo", "")
    idl_repo = workspace / matrix.get("idl_repo", "")
    services = matrix.get("services") or {}
    libraries = matrix.get("libraries") or {}
    modules = matrix.get("modules") or {}
    dependencies = matrix.get("dependencies") or {}

    if not modules:
        problems.append("modules must not be empty")
    if not services:
        problems.append("services must not be empty")
    if not business_repo.exists():
        problems.append(f"business_repo does not exist: {business_repo}")
    if not idl_repo.exists():
        problems.append(f"idl_repo does not exist: {idl_repo}")

    for service_name, service in services.items():
        module = service.get("module")
        if module not in modules:
            problems.append(f"services.{service_name}.module is not defined in modules: {module}")

        repo_path = service.get("repo_path")
        if not repo_path:
            problems.append(f"services.{service_name}.repo_path is required")
        else:
            check_placeholders(problems, f"services.{service_name}.repo_path", repo_path)
            resolved = resolve_path(root, workspace, business_repo, idl_repo, repo_path)
            if not resolved.exists():
                problems.append(f"services.{service_name}.repo_path does not exist: {resolved}")

        if service.get("idl_required"):
            proto_path = service.get("proto_path")
            if not service.get("idl_repo"):
                problems.append(f"services.{service_name}.idl_repo is required when idl_required is true")
            if not proto_path:
                problems.append(f"services.{service_name}.proto_path is required when idl_required is true")
            else:
                check_placeholders(problems, f"services.{service_name}.proto_path", proto_path)
                resolved_proto = resolve_path(root, workspace, business_repo, idl_repo, proto_path)
                if not resolved_proto.exists():
                    problems.append(f"services.{service_name}.proto_path does not exist: {resolved_proto}")
            if not (idl_repo / "buf.yaml").exists():
                problems.append("idl_repo is missing buf.yaml")
            if not (idl_repo / "buf.gen.yaml").exists():
                problems.append("idl_repo is missing buf.gen.yaml")

    for library_name, library in libraries.items():
        module = library.get("module")
        if module not in modules:
            problems.append(f"libraries.{library_name}.module is not defined in modules: {module}")
        repo_path = library.get("repo_path")
        if not repo_path:
            problems.append(f"libraries.{library_name}.repo_path is required")
        else:
            check_placeholders(problems, f"libraries.{library_name}.repo_path", repo_path)
            resolved = resolve_path(root, workspace, business_repo, idl_repo, repo_path)
            if not resolved.exists():
                problems.append(f"libraries.{library_name}.repo_path does not exist: {resolved}")

    for source, dependency in dependencies.items():
        if source not in services:
            problems.append(f"dependencies.{source} is not defined in services")
        for library_name in dependency.get("libraries", []) or []:
            if library_name not in libraries:
                problems.append(f"dependencies.{source}.libraries references unknown library: {library_name}")
        for upstream in dependency.get("upstream", []) or []:
            if upstream not in services:
                problems.append(f"dependencies.{source}.upstream references external or unknown service: {upstream}")
        for downstream in dependency.get("downstream", []) or []:
            if downstream not in services:
                problems.append(f"dependencies.{source}.downstream references external or unknown service: {downstream}")

    if problems:
        for problem in problems:
            print(f"- {problem}", file=sys.stderr)
        return 1

    print("service matrix valid")
    return 0


def check_placeholders(problems, field: str, value: str) -> None:
    start = 0
    while True:
        open_at = value.find("{", start)
        if open_at == -1:
            return
        close_at = value.find("}", open_at)
        if close_at == -1:
            problems.append(f"{field} has an unclosed placeholder")
            return
        name = value[open_at + 1 : close_at]
        if name not in ALLOWED_PLACEHOLDERS:
            problems.append(f"{field} uses unsupported placeholder: {{{name}}}")
        start = close_at + 1


def resolve_path(root: pathlib.Path, workspace: pathlib.Path, business_repo: pathlib.Path, idl_repo: pathlib.Path, value: str) -> pathlib.Path:
    replacements = {
        "{business-repo}": str(business_repo),
        "{business-repo-name}": business_repo.name,
        "{idl-repo}": str(idl_repo),
        "{idl-repo-name}": idl_repo.name,
    }
    resolved = value
    for placeholder, replacement in replacements.items():
        resolved = resolved.replace(placeholder, replacement)
    path = pathlib.Path(resolved)
    if path.is_absolute():
        return path
    return root / path


if __name__ == "__main__":
    sys.exit(main())
