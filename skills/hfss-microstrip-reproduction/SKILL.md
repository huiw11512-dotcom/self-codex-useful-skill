---
name: hfss-microstrip-reproduction
description: "Use when reproducing or rapidly building HFSS/AEDT microstrip or planar RF networks from a paper/demo/project: synthesize microstrip widths and quarter-wave lengths from target impedances, create physically valid microstrip ports, run or validate solves, export raw S-parameters, compute amplitude/phase balance, return loss, insertion loss, and isolation metrics, especially for sum-difference networks, hybrid rings, Butler/beamforming feed networks, and multi-port microstrip circuits."
---

# HFSS Microstrip Reproduction

## Core Workflow

1. Inspect the paper/demo and existing AEDT/script before changing geometry.
2. Extract target impedances, center frequency, frequency band, substrate stack, copper thickness, and port definitions.
3. Synthesize every microstrip width from impedance; do not sweep blindly when a physical reverse calculation is available.
4. Compute guided quarter-wave length from the same effective permittivity used for the width calculation.
5. Build one reusable AEDT project/script and overwrite that project for iterations. Avoid creating many candidate projects unless explicitly requested.
6. Verify geometry visually against the paper figure before solving: topology, symmetry, port positions, line widths, board clearance, and reference planes.
7. Use physical microstrip port definitions and run a coarse solve first.
8. Export raw S-parameters or Touchstone. Compute balances and metrics outside AEDT unless native reports are needed for screenshots.
9. Write the synthesis table, solve status, key metrics, and deviations from the paper into the report.

Use `$hfss-control` and `$hfss-rf-modeling` together with this skill for AEDT hygiene, port validation, cleanup, and solve execution.

## Microstrip Synthesis

Use `scripts/microstrip_synthesis.py` for repeatable impedance-to-geometry calculation.

Default formula:

```text
W = 5.98 h / (0.8 exp(Z0 sqrt(er + 1.41) / 87))
```

Then compute effective permittivity with the standard quasi-static microstrip expression and guided quarter-wave length:

```text
Lq = c / (4 f0 sqrt(eps_eff))
```

For the xdld_20230913 workflow, the established calculator-compatible baseline is:

```text
er=2.2, h=2.2 mm, t=0.035 mm, f0=10 GHz
Z0=50 ohm   -> W~=5.518 mm, Lq~=5.511 mm
Z1=70.7 ohm -> W~=3.511 mm, Lq~=5.578 mm
Z2=90 ohm   -> W~=2.304 mm, Lq~=5.633 mm
Z3=100 ohm  -> W~=1.852 mm, Lq~=5.659 mm
```

If the model uses a different substrate height, recompute widths. A width set produced for `h=0.508 mm` is not interchangeable with a `h=2.2 mm` model.

## HFSS Geometry Rules

- Use a single parameterized build script when possible. Keep dimensions in JSON or command-line arguments.
- Board size must include actual trace bounding boxes plus clearance. Include port feed lines in the bounding box.
- Make the substrate/ground larger than all traces and port sheets; avoid ports at or beyond board edge unless intentionally using an edge wave port.
- Unite top copper only after all trace segments are created; keep port sheets separate.
- Match the paper figure before solving. If the geometry "looks obviously different," fix topology/proportions first.
- Track assumptions explicitly: paper may show stripline but the reproduction may use a single-layer microstrip equivalent.

For detailed setup and checks, read `references/hfss_microstrip_workflow.md`.

## Port Rules

Use microstrip lumped ports or wave ports; do not replace microstrip feeds with coax unless the task explicitly asks for coax.

For a lumped microstrip port:

- Port sheet spans from signal trace top/reference point down to bottom ground.
- Integration line starts on the signal conductor/reference plane and ends on ground.
- Both integration-line endpoints must lie on the port sheet.
- For an AEDT rectangle with `WhichAxis="Y"`, the sheet is in the X-Z plane. Use Z height as `Width` and trace span along X as `Height`.
- For `WhichAxis="X"`, the sheet is in the Y-Z plane. Use trace span along Y as `Width` and Z height as `Height`.

Hard stop before solving if HFSS reports: `Both endpoints of port lines must lie on the port.`

## AEDT Report Expression Rules

Prefer exporting raw `Sij` values and computing metrics with Python.

If creating native HFSS phase-difference reports, include angle units on constants:

```text
ang_deg(S(Port4,Port1))-ang_deg(S(Port4,Port2))-180deg
```

Do not write `-180` in an `ang_deg(...)` expression. AEDT 2018 can treat it as unitless and produce nonsense such as very large wrapped angles.

For multi-port sum-difference networks, do not trust a native phase-balance report until the raw phase grouping has been verified. First export raw complex or amplitude/phase S-parameters and compute the actual sign pattern at the output port:

- For each candidate output, compute wrapped relative phases `wrap(ang(S(out,Pi))-ang(S(out,P1)))`.
- Test every plausible two-plus/two-minus grouping before declaring a phase curve wrong.
- If one report curve sits near `180deg` while the raw phases show good two-group behavior, the likely fault is the report expression or logical port mapping, not necessarily the geometry.
- Use complex-ratio expressions for native HFSS reports, e.g. `ang_deg(S(Port7,Port3)/S(Port7,Port1))` for same-phase paths and `ang_deg(-S(Port7,Port4)/S(Port7,Port1))` for anti-phase paths.
- Record the selected logical mapping explicitly in the manifest/report, especially when physical HFSS labels differ from paper labels.

For the xdld_20230913 seven-port network, verify whether `Port7` is producing the paper azimuth-difference grouping or the unused diagonal/difference-difference grouping before tuning dimensions. A pattern like `P1/P3` same-phase and `P2/P4` anti-phase means the output is `(1+3)-(2+4)`, not `(1+4)-(2+3)`.

## Post-Processing

Use `scripts/evaluate_sparams.py` for raw CSV or Touchstone `.sNp` files.

For a four-port sum-difference network with branch ports 1/2, sum port 3, and difference port 4, compute over all swept frequencies:

- Sum amplitude balance: `abs(dB(S31)-dB(S32))`
- Sum phase balance: `abs(wrap(ang(S31)-ang(S32)))`
- Difference amplitude balance: `abs(dB(S41)-dB(S42))`
- Difference phase error: `abs(wrap(ang(S41)-ang(S42)-180deg))`
- Sum-difference isolation: worst of `S34` and `S43`
- Return loss: all required port self terms, e.g. `S11..S44`
- Insertion loss limit: check all required transfer paths, e.g. `S31,S32,S41,S42`

When judging user constraints, report pass/fail from the worst value across `Freq=All`, then include 10 GHz center-point values if useful.

## Optimization Triage

Before tuning lengths or widths:

1. Verify visual topology against the paper: no extra bypasses, no missing thin/thick transitions, ports on the correct side, and branch labels matching the paper.
2. Verify every generated width is parameterized in AEDT Local Variables or in an exported manifest: `w_z0`, `w_z1`, `w_z2`, `w_z3`, connection widths, substrate height, and copper thickness.
3. Verify raw output sign patterns from S-parameters. Fix report expressions or port mappings before interpreting a large phase error as a geometry defect.
4. Check convergence. Treat non-converged results as directional only; do not overfit fine dimensions to a non-converged solve.
5. Optimize in small physics-based groups: output assignment/mapping first, then obvious path length imbalance, then impedance transitions, then board/port clearance. Avoid arbitrary meanders or extra branches unless the paper shows them.

## Report Update Checklist

- Include paper figure/topology and generated model screenshot or recreated layout.
- Include the microstrip synthesis table: target impedance, width, effective permittivity, quarter-wave length.
- Include port setup notes: lumped/wave, reference conductor, integration-line direction.
- Include solve setup: Driven Modal, setup frequency, sweep type, sweep points.
- Include metric table with requirement, worst value, pass/fail, and worst frequency when available.
- Record known limitations: microstrip equivalent vs stripline, coarse sweep, non-converged adaptive pass, or AEDT report workaround.
