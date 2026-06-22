#!/usr/bin/env python3
"""Lightweight HFSS/PyAEDT port-pattern linter.

This does not prove a model is correct. It catches common script patterns that
caused bad HFSS port placement in antenna/feed models.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path


PATTERNS = [
    (
        re.compile(r"CreateRectangle\([\s\S]{0,900}?PortSheet", re.IGNORECASE),
        "PortSheet is created from a rectangle. Verify this is a microstrip/lumped reference-plane port, not a fake coax/monopole excitation.",
    ),
    (
        re.compile(r"AssignLumpedPort\([\s\S]{0,1400}?ground_t/2", re.IGNORECASE),
        "Lumped port appears near the top ground plane. For coax/probe feeds, prefer the coax end or a true microstrip reference plane.",
    ),
    (
        re.compile(r"AssignWavePort\(", re.IGNORECASE),
        "Wave port found. Verify the face is on a valid exterior coax/microstrip cross-section and touches both conductors.",
    ),
    (
        re.compile(r"coax_outer[\s\S]{0,900}?ground", re.IGNORECASE),
        "Coax outer/ground relationship found. Verify the shield touches or is united with ground without overlapping volumes.",
    ),
]


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: lint_hfss_ports.py <hfss_generation_script.py>")
        return 2

    path = Path(sys.argv[1])
    if not path.exists():
        print(f"File not found: {path}")
        return 2

    text = path.read_text(encoding="utf-8", errors="ignore")
    warnings = []
    for pattern, message in PATTERNS:
        for match in pattern.finditer(text):
            line = text.count("\n", 0, match.start()) + 1
            warnings.append((line, message))

    if not warnings:
        print("No suspicious HFSS port patterns found.")
        return 0

    print(f"{len(warnings)} HFSS port checks need review:")
    for line, message in warnings:
        print(f"- line {line}: {message}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
