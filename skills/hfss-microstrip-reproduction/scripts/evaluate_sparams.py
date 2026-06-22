#!/usr/bin/env python
"""Evaluate four-port sum-difference metrics from Touchstone or HFSS raw CSV."""

from __future__ import annotations

import argparse
import cmath
import csv
import json
import math
from pathlib import Path


def wrap_deg(value: float) -> float:
    return ((value + 180.0) % 360.0) - 180.0


def db(value: complex) -> float:
    return 20.0 * math.log10(max(abs(value), 1e-30))


def parse_touchstone(path: Path) -> list[dict]:
    tokens: list[str] = []
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("!") or line.startswith("#"):
            continue
        tokens.extend(line.split())

    nports = int(path.suffix.lower().lstrip(".s").rstrip("p"))
    per_freq = nports * nports
    records = []
    i = 0
    while i < len(tokens):
        freq = float(tokens[i])
        i += 1
        values = []
        for _ in range(per_freq):
            mag = float(tokens[i])
            phase_deg = float(tokens[i + 1])
            i += 2
            values.append(mag * cmath.exp(1j * math.radians(phase_deg)))
        s = [values[row * nports : (row + 1) * nports] for row in range(nports)]
        records.append({"freq": freq, "s": s})
    return records


def find_col(rows: list[dict[str, str]], prefix: str) -> list[float]:
    for key in rows[0]:
        if key.startswith(prefix):
            return [float(row[key]) for row in rows]
    raise KeyError(f"column starting with {prefix!r} not found")


def parse_hfss_csv(path: Path) -> list[dict]:
    rows = list(csv.DictReader(path.open(newline="")))
    freq = find_col(rows, "Freq")
    cols = {
        "s11": find_col(rows, "dB(S(P1,P1))"),
        "s22": find_col(rows, "dB(S(P2,P2))"),
        "s33": find_col(rows, "dB(S(P3,P3))"),
        "s44": find_col(rows, "dB(S(P4,P4))"),
        "s31": find_col(rows, "dB(S(P3,P1))"),
        "s32": find_col(rows, "dB(S(P3,P2))"),
        "s41": find_col(rows, "dB(S(P4,P1))"),
        "s42": find_col(rows, "dB(S(P4,P2))"),
        "ph31": find_col(rows, "ang_deg(S(P3,P1))"),
        "ph32": find_col(rows, "ang_deg(S(P3,P2))"),
        "ph41": find_col(rows, "ang_deg(S(P4,P1))"),
        "ph42": find_col(rows, "ang_deg(S(P4,P2))"),
    }
    records = []
    for idx, f in enumerate(freq):
        records.append(
            {
                "freq": f,
                "s11_db": cols["s11"][idx],
                "s22_db": cols["s22"][idx],
                "s33_db": cols["s33"][idx],
                "s44_db": cols["s44"][idx],
                "s31_db": cols["s31"][idx],
                "s32_db": cols["s32"][idx],
                "s41_db": cols["s41"][idx],
                "s42_db": cols["s42"][idx],
                "sum_phase_deg": abs(wrap_deg(cols["ph31"][idx] - cols["ph32"][idx])),
                "diff_phase_deg": abs(wrap_deg(cols["ph41"][idx] - cols["ph42"][idx] - 180.0)),
            }
        )
    return records


def records_from_touchstone(path: Path) -> list[dict]:
    out = []
    for item in parse_touchstone(path):
        s = item["s"]
        if len(s) < 4:
            raise ValueError("sum-difference evaluation requires at least 4 ports")
        ph31 = math.degrees(cmath.phase(s[2][0]))
        ph32 = math.degrees(cmath.phase(s[2][1]))
        ph41 = math.degrees(cmath.phase(s[3][0]))
        ph42 = math.degrees(cmath.phase(s[3][1]))
        out.append(
            {
                "freq": item["freq"],
                "s11_db": db(s[0][0]),
                "s22_db": db(s[1][1]),
                "s33_db": db(s[2][2]),
                "s44_db": db(s[3][3]),
                "s31_db": db(s[2][0]),
                "s32_db": db(s[2][1]),
                "s41_db": db(s[3][0]),
                "s42_db": db(s[3][1]),
                "sum_phase_deg": abs(wrap_deg(ph31 - ph32)),
                "diff_phase_deg": abs(wrap_deg(ph41 - ph42 - 180.0)),
            }
        )
    return out


def worst(records: list[dict], key: str, mode: str = "max") -> tuple[float, float]:
    fn = max if mode == "max" else min
    rec = fn(records, key=lambda item: item[key])
    return rec["freq"], rec[key]


def summarize(records: list[dict], args: argparse.Namespace) -> dict:
    summary = {
        "freq_start": min(item["freq"] for item in records),
        "freq_stop": max(item["freq"] for item in records),
        "points": len(records),
        "sumdiff_return_max_db": max(max(item["s33_db"], item["s44_db"]) for item in records),
        "branch_return_max_db": max(max(item["s11_db"], item["s22_db"]) for item in records),
        "insertion_min_db": min(
            min(item["s31_db"], item["s32_db"], item["s41_db"], item["s42_db"]) for item in records
        ),
        "insertion_max_db": max(
            max(item["s31_db"], item["s32_db"], item["s41_db"], item["s42_db"]) for item in records
        ),
        "sum_phase_max_deg": max(item["sum_phase_deg"] for item in records),
        "diff_phase_max_deg": max(item["diff_phase_deg"] for item in records),
    }
    summary["pass"] = (
        summary["sumdiff_return_max_db"] <= args.return_loss_db
        and summary["branch_return_max_db"] <= args.return_loss_db
        and summary["insertion_min_db"] >= -args.insertion_loss_db
        and summary["sum_phase_max_deg"] <= args.sum_phase_deg
        and summary["diff_phase_max_deg"] <= args.diff_phase_deg
    )
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("--format", choices=["auto", "touchstone", "hfss-csv"], default="auto")
    parser.add_argument("--return-loss-db", type=float, default=-10.0)
    parser.add_argument("--insertion-loss-db", type=float, default=15.0)
    parser.add_argument("--sum-phase-deg", type=float, default=10.0)
    parser.add_argument("--diff-phase-deg", type=float, default=15.0)
    parser.add_argument("--json", type=Path)
    parser.add_argument("--csv", type=Path)
    args = parser.parse_args()

    kind = args.format
    if kind == "auto":
        kind = "touchstone" if args.input.suffix.lower().startswith(".s") else "hfss-csv"
    records = records_from_touchstone(args.input) if kind == "touchstone" else parse_hfss_csv(args.input)
    summary = summarize(records, args)

    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    if args.csv:
        args.csv.parent.mkdir(parents=True, exist_ok=True)
        with args.csv.open("w", newline="") as fp:
            writer = csv.DictWriter(fp, fieldnames=list(summary.keys()))
            writer.writeheader()
            writer.writerow(summary)
    if not args.json and not args.csv:
        print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
