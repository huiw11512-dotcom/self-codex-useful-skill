#!/usr/bin/env python
"""Synthesize microstrip width and guided quarter-wave length from impedance."""

from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path


def microstrip_eff_eps(width_mm: float, h_mm: float, epsr: float) -> float:
    u = max(width_mm / h_mm, 1e-12)
    correction = 0.04 * (1.0 - u) ** 2 if u < 1.0 else 0.0
    return (epsr + 1.0) / 2.0 + (epsr - 1.0) / 2.0 * (
        1.0 / math.sqrt(1.0 + 12.0 / u) + correction
    )


def microstrip_z0(width_mm: float, h_mm: float, epsr: float) -> float:
    u = max(width_mm / h_mm, 1e-12)
    eeff = microstrip_eff_eps(width_mm, h_mm, epsr)
    if u <= 1.0:
        return 60.0 / math.sqrt(eeff) * math.log(8.0 / u + 0.25 * u)
    return 120.0 * math.pi / (
        math.sqrt(eeff) * (u + 1.393 + 0.667 * math.log(u + 1.444))
    )


def width_for_impedance(z_ohm: float, h_mm: float, epsr: float) -> float:
    # IPC-style calculator-compatible expression used in the xdld_20230913 work.
    return 5.98 * h_mm / (0.8 * math.exp(z_ohm * math.sqrt(epsr + 1.41) / 87.0))


def parse_impedances(text: str) -> list[tuple[str, float]]:
    out: list[tuple[str, float]] = []
    for item in text.split(","):
        item = item.strip()
        if not item:
            continue
        if "=" in item:
            name, value = item.split("=", 1)
        else:
            name, value = f"Z{len(out)}", item
        out.append((name.strip(), float(value)))
    return out


def synthesize(args: argparse.Namespace) -> list[dict[str, float | str]]:
    rows = []
    for name, z_ohm in parse_impedances(args.impedances):
        width = width_for_impedance(z_ohm, args.h_mm, args.epsr) * args.width_scale
        eeff = microstrip_eff_eps(width, args.h_mm, args.epsr)
        qlen = 299.792458 / args.freq_ghz / math.sqrt(eeff) / 4.0 * args.length_scale
        rows.append(
            {
                "name": name,
                "target_z_ohm": z_ohm,
                "width_mm": width,
                "eps_eff": eeff,
                "quarter_wave_mm": qlen,
                "z0_check_ohm": microstrip_z0(width, args.h_mm, args.epsr),
                "epsr": args.epsr,
                "h_mm": args.h_mm,
                "freq_ghz": args.freq_ghz,
            }
        )
    return rows


def write_csv(rows: list[dict[str, float | str]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "name",
        "target_z_ohm",
        "width_mm",
        "eps_eff",
        "quarter_wave_mm",
        "z0_check_ohm",
        "epsr",
        "h_mm",
        "freq_ghz",
    ]
    with path.open("w", newline="") as fp:
        writer = csv.DictWriter(fp, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--epsr", type=float, default=2.2)
    parser.add_argument("--h-mm", type=float, default=2.2)
    parser.add_argument("--freq-ghz", type=float, default=10.0)
    parser.add_argument("--impedances", default="Z0=50,Z1=70.7,Z2=90,Z3=100")
    parser.add_argument("--width-scale", type=float, default=1.0)
    parser.add_argument("--length-scale", type=float, default=1.0)
    parser.add_argument("--csv", type=Path)
    parser.add_argument("--json", type=Path)
    args = parser.parse_args()

    rows = synthesize(args)
    if args.csv:
        write_csv(rows, args.csv)
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(json.dumps(rows, indent=2), encoding="utf-8")
    if not args.csv and not args.json:
        print(json.dumps(rows, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
