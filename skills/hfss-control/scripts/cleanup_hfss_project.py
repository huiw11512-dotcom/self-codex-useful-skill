#!/usr/bin/env python
"""Safely delete generated HFSS project artifacts for one project base name."""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path


def project_base(path: Path) -> Path:
    path = path.resolve()
    if path.suffix.lower() == ".aedt":
        return path.with_suffix("")
    return path


def artifact_paths(base: Path) -> list[Path]:
    return [
        base.with_suffix(".aedt"),
        Path(str(base) + ".aedtresults"),
        Path(str(base) + ".pyaedt"),
        Path(str(base) + ".aedt.auto"),
        Path(str(base) + ".aedt.autotemp"),
        Path(str(base) + ".aedt.lock"),
    ]


def remove_path(path: Path) -> bool:
    if path.is_dir():
        shutil.rmtree(path)
        return True
    if path.exists():
        path.unlink()
        return True
    return False


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project", help="Path to a .aedt file or project base name.")
    parser.add_argument("--dry-run", action="store_true", help="List artifacts without deleting them.")
    args = parser.parse_args()

    base = project_base(Path(args.project))
    if not base.name:
        raise SystemExit("Refusing to operate on an empty project name.")

    targets = artifact_paths(base)
    for target in targets:
        if args.dry_run:
            print(target)
        elif remove_path(target):
            print(f"removed {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
