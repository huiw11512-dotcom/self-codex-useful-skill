---
name: hfss-control
description: Use when launching, cleaning, building, editing, solving, validating, or exporting HFSS/AEDT projects via PyAEDT on Windows; covers project hygiene, parameterized geometry, physical ports, setup/sweep control, and result extraction.
---

# HFSS Control

## Overview

Use this skill to control HFSS/AEDT projects on this Windows machine from Python/PyAEDT. It covers project cleanup, fresh rebuilds, geometry edits, port setup, adaptive solves, and result checks.

## Default Flow

1. Inspect the current project, script, result folder, and AEDT logs before changing anything.
2. Decide whether to edit in place or rebuild from a clean project.
3. Close AEDT before deleting stale `.aedt`, `.aedtresults`, `.pyaedt`, `.lock`, `.auto`, or `.autotemp` files.
4. Build geometry from parameters first; redraw only when the existing model is unrecoverable.
5. Assign physically valid ports and boundaries before solving.
6. Run one coarse adaptive setup first, then widen the sweep after the port and mesh behavior are stable.
7. Read exact S-parameter points and the HFSS log before tuning dimensions.

## Port And Solve Rules

- Coax-fed antennas need a real coax stack: inner conductor, dielectric, outer conductor, and a port on the coax end face.
- The coax outer conductor must tie to the reference ground.
- Wave ports should be on an exterior solve boundary unless the internal-port construction is explicitly valid.
- For antenna work, keep the feed family consistent; do not silently switch coax feeds to microstrip or lumped gap feeds.
- Use `validate_simple()` or the closest available AEDT validation call before solving.
- If the solve fails immediately, inspect `batch.log` and the PyAEDT log for port, face, mesh, or duplicate-geometry errors.

## Parameterization And Optimetrics

- Only put variables into Optimetrics if changing the variable actually changes the AEDT geometry or setup history. Project variables that merely document numeric geometry are not valid optimization inputs.
- Keep coax port faces and integration lines numerically stable when possible. If a variable-driven integration line is rejected as zero length, keep the port at a fixed numeric feed radius and connect it to the variable radiator with a parameterized transition.
- For helical/ribbon antennas, prefer variable-driven faceted sheet vertices or robust polylines over equation surfaces when the equation surfaces make AEDT geometry creation slow or brittle.
- Create an Optimetrics setup with at least one goal at insertion time, then add remaining variations and goals. Some AEDT versions reject empty optimization setups.
- Use compact initial ranges based on physics and the current model. Start with radius, height, turns, strip/transition width, and ground radius only when those parameters are truly bound to the model.
- If AEDT-native parametric geometry is too slow for structure exploration, fall back to a single-project external loop: rebuild the same project from script for each candidate, solve coarsely, export exact metrics, and keep only useful report images/artifacts.

## Project Hygiene

- Delete only artifacts belonging to the target HFSS project.
- Preserve source scripts, notes, PDFs, images, and raw data unless the user explicitly asks to remove them.
- If a project is polluted by repeated geometry creation, rebuild it fresh instead of trying to patch every duplicate object.
- Save the project after a clean rebuild and before launching the solve.

## References

- Read `references/workflow.md` for the local HFSS/PyAEDT workflow and failure handling.
- Run `scripts/cleanup_hfss_project.py` when a project's generated artifacts need to be deleted safely.
- For RF-specific port policy and antenna modeling checks, also apply `$hfss-rf-modeling`.
