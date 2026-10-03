#!/usr/bin/env python3
"""Build a link-free, allowlisted Omnigent agent image tarball."""

from __future__ import annotations

import argparse
import gzip
import io
import os
import shutil
import tarfile
from pathlib import Path


ROOT_FILES = (
    "config.yaml",
    "AGENTS.md",
    "SKILLS.md",
    "README_OMNIGENT.md",
    "README.md",
    "pyproject.toml",
    "requirements-lock.txt",
)
ROOT_DIRECTORIES = (
    "agents",
    "skills",
    "tools",
    "references",
    "configs",
    "research",
    "logs",
    "src",
)
EXCLUDED_PARTS = {
    ".DS_Store",
    ".git",
    ".pytest_cache",
    ".venv",
    "__pycache__",
    "artifacts",
    "build",
    "dist",
    "private_oracle",
    "runs",
}
EXCLUDED_SUFFIXES = (".pyc", ".pyo", ".sqlite", ".sqlite3")
SENSITIVE_NAME_FRAGMENTS = ("lab_token", "gb1_wu2016_oracle")


def _allowed_files(root: Path) -> list[Path]:
    candidates: list[Path] = []
    for name in ROOT_FILES:
        path = root / name
        if not path.is_file() or path.is_symlink():
            raise SystemExit(f"required regular file is missing: {path}")
        candidates.append(path)
    for name in ROOT_DIRECTORIES:
        directory = root / name
        if not directory.is_dir() or directory.is_symlink():
            raise SystemExit(f"required regular directory is missing: {directory}")
        candidates.extend(path for path in directory.rglob("*") if path.is_file())

    output: list[Path] = []
    for path in candidates:
        relative = path.relative_to(root)
        if path.is_symlink():
            raise SystemExit(f"agent bundle refuses symbolic link: {relative}")
        if any(part in EXCLUDED_PARTS or part.endswith(".egg-info") for part in relative.parts):
            continue
        if path.suffix.lower() in EXCLUDED_SUFFIXES:
            continue
        lowered = relative.as_posix().lower()
        if any(fragment in lowered for fragment in SENSITIVE_NAME_FRAGMENTS):
            raise SystemExit(f"agent bundle refuses sensitive-looking path: {relative}")
        output.append(path)
    return sorted(set(output), key=lambda item: item.relative_to(root).as_posix())


def build_bundle(root: Path, destination: Path) -> tuple[int, int]:
    files = _allowed_files(root)
    destination.parent.mkdir(parents=True, exist_ok=True)
    buffer = io.BytesIO()
    with gzip.GzipFile(filename="", fileobj=buffer, mode="wb", mtime=0) as compressed:
        with tarfile.open(fileobj=compressed, mode="w") as archive:
            for path in files:
                relative = path.relative_to(root).as_posix()
                data = path.read_bytes()
                info = tarfile.TarInfo(relative)
                info.size = len(data)
                info.mode = 0o755 if os.access(path, os.X_OK) else 0o644
                info.mtime = 0
                archive.addfile(info, io.BytesIO(data))
    destination.write_bytes(buffer.getvalue())

    with tarfile.open(destination, "r:gz") as archive:
        members = archive.getmembers()
        if any(not member.isfile() for member in members):
            raise SystemExit("built bundle contains a non-regular archive member")
        names = {member.name for member in members}
        if "config.yaml" not in names or "AGENTS.md" not in names:
            raise SystemExit("built bundle is missing required agent files")
    return len(files), destination.stat().st_size


def stage_directory(root: Path, destination: Path) -> tuple[int, int]:
    if destination.exists():
        raise SystemExit(f"staging destination already exists: {destination}")
    files = _allowed_files(root)
    total_size = 0
    for source in files:
        relative = source.relative_to(root)
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target, follow_symlinks=False)
        target.chmod(0o755 if os.access(source, os.X_OK) else 0o644)
        total_size += target.stat().st_size
    if any(path.is_symlink() for path in destination.rglob("*")):
        raise SystemExit("staged agent directory unexpectedly contains a symbolic link")
    return len(files), total_size


def main() -> int:
    parser = argparse.ArgumentParser()
    output = parser.add_mutually_exclusive_group(required=True)
    output.add_argument("--output", help="write a deterministic .tar.gz bundle")
    output.add_argument("--directory", help="write a clean directory for Omnigent 0.16")
    args = parser.parse_args()
    root = Path(__file__).resolve().parent.parent
    if args.directory:
        destination = Path(args.directory).expanduser().resolve()
        count, size = stage_directory(root, destination)
        print(f"Staged link-free Omnigent image: {count} files, {size} bytes")
    else:
        destination = Path(args.output).expanduser().resolve()
        count, size = build_bundle(root, destination)
        print(f"Built link-free Omnigent bundle: {count} files, {size} bytes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
