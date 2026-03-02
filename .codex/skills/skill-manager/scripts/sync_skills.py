#!/usr/bin/env python3
"""Install or update Codex skills from a GitHub repository."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


@dataclass
class SkillTarget:
    source_path: str
    local_name: str


@dataclass
class SkillResult:
    source_path: str
    local_name: str
    status: str
    detail: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Install/update Codex skills from GitHub")
    parser.add_argument("--repo", required=True, help="GitHub repository in owner/repo format")
    parser.add_argument("--ref", default="main", help="Git ref (branch/tag/sha), default: main")
    parser.add_argument("--path", dest="paths", action="append", default=[], help="Skill path in repo (repeatable)")
    parser.add_argument("--collection", help="Collection manifest path in repo, e.g. collections/backend-testing.json")
    parser.add_argument(
        "--dest",
        default=str(Path(os.environ.get("CODEX_HOME", str(Path.home() / ".codex"))) / "skills"),
        help="Destination skills directory",
    )
    parser.add_argument("--update", action="store_true", help="Update existing installed skills")
    return parser.parse_args()


def run(cmd: list[str], cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=cwd, text=True, capture_output=True)


def check_call(cmd: list[str], cwd: Path | None = None, context: str = "command") -> None:
    result = run(cmd, cwd=cwd)
    if result.returncode != 0:
        err = (result.stderr or result.stdout).strip()
        raise RuntimeError(f"{context} failed: {' '.join(cmd)}\n{err}")


def validate_repo(repo: str) -> None:
    parts = repo.split("/")
    if len(parts) != 2 or not all(parts):
        raise ValueError("--repo must be in owner/repo format")


def load_collection(clone_dir: Path, collection_path: str, default_repo: str, default_ref: str) -> tuple[list[str], str, str]:
    manifest_file = clone_dir / collection_path
    if not manifest_file.is_file():
        raise FileNotFoundError(f"Collection file not found: {collection_path}")

    with manifest_file.open("r", encoding="utf-8") as fh:
        payload = json.load(fh)

    skills = payload.get("skills", [])
    if not isinstance(skills, list):
        raise ValueError("Collection field 'skills' must be an array")

    paths: list[str] = []
    for item in skills:
        if not isinstance(item, dict) or "path" not in item:
            raise ValueError("Each collection skill entry must be an object with a 'path' field")
        paths.append(str(item["path"]))

    manifest_repo = str(payload.get("repo") or default_repo)
    manifest_ref = str(payload.get("ref") or default_ref)
    validate_repo(manifest_repo)
    return paths, manifest_repo, manifest_ref


def derive_local_name(source_path: str) -> str:
    clean = source_path.strip().strip("/")
    if not clean:
        raise ValueError("Skill path cannot be empty")
    return clean.split("/")[-1]


def resolve_targets(paths: Iterable[str]) -> list[SkillTarget]:
    by_name: dict[str, str] = {}
    targets: list[SkillTarget] = []
    for p in paths:
        local_name = derive_local_name(p)
        if local_name in by_name and by_name[local_name] != p:
            raise ValueError(
                f"Conflicting skill targets map to the same local name '{local_name}': "
                f"'{by_name[local_name]}' and '{p}'"
            )
        if local_name in by_name:
            continue
        by_name[local_name] = p
        targets.append(SkillTarget(source_path=p, local_name=local_name))

    if not targets:
        raise ValueError("No skill paths were provided. Use --path or --collection.")
    return targets


def clone_repo(repo: str, ref: str, clone_dir: Path) -> None:
    url = f"https://github.com/{repo}.git"
    check_call(["git", "init", str(clone_dir)], context="git init")
    check_call(["git", "remote", "add", "origin", url], cwd=clone_dir, context="git remote add")
    check_call(["git", "fetch", "--depth", "1", "origin", ref], cwd=clone_dir, context=f"git fetch {repo}@{ref}")
    check_call(["git", "checkout", "--detach", "FETCH_HEAD"], cwd=clone_dir, context="git checkout")


def install_targets(clone_dir: Path, dest_dir: Path, targets: list[SkillTarget], update: bool) -> list[SkillResult]:
    results: list[SkillResult] = []
    for target in targets:
        src_dir = clone_dir / target.source_path
        skill_file = src_dir / "SKILL.md"
        out_dir = dest_dir / target.local_name

        if not src_dir.is_dir() or not skill_file.is_file():
            results.append(SkillResult(target.source_path, target.local_name, "failed", "Missing SKILL.md at source path"))
            continue

        if out_dir.exists() and not update:
            results.append(
                SkillResult(
                    target.source_path,
                    target.local_name,
                    "failed",
                    "Destination exists (use --update to overwrite)",
                )
            )
            continue

        if out_dir.exists() and update:
            shutil.rmtree(out_dir)

        shutil.copytree(src_dir, out_dir)
        action = "updated" if update else "installed"
        results.append(SkillResult(target.source_path, target.local_name, action, "ok"))

    return results


def print_report(repo: str, ref: str, results: list[SkillResult]) -> int:
    print(f"Source: {repo}@{ref}")
    print("Skill results:")
    for r in results:
        print(f"- {r.local_name}: {r.status} ({r.source_path}) - {r.detail}")

    ok_status = {"installed", "updated"}
    success = [r.local_name for r in results if r.status in ok_status]
    if success:
        print("Installed/updated skills:", ", ".join(success))
    else:
        print("Installed/updated skills: none")

    print("Restart Codex to pick up new skills.")
    return 0 if all(r.status in ok_status for r in results) else 1


def main() -> int:
    args = parse_args()
    validate_repo(args.repo)

    with tempfile.TemporaryDirectory(prefix="codex-skill-sync-") as tmpdir:
        clone_dir = Path(tmpdir) / "repo"
        clone_repo(args.repo, args.ref, clone_dir)

        path_list = list(args.paths)
        repo = args.repo
        ref = args.ref

        if args.collection:
            collection_paths, manifest_repo, manifest_ref = load_collection(clone_dir, args.collection, args.repo, args.ref)
            if manifest_repo != args.repo or manifest_ref != args.ref:
                clone_dir = Path(tmpdir) / "manifest_repo"
                clone_repo(manifest_repo, manifest_ref, clone_dir)
            path_list.extend(collection_paths)
            repo, ref = manifest_repo, manifest_ref

        targets = resolve_targets(path_list)
        dest_dir = Path(args.dest).expanduser()
        dest_dir.mkdir(parents=True, exist_ok=True)
        results = install_targets(clone_dir, dest_dir, targets, args.update)
        return print_report(repo, ref, results)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(1)
