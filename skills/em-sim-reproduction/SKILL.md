---
name: em-sim-reproduction
description: Use when reproducing, building, validating, integrating, or optimizing HFSS/CST electromagnetic simulations from papers, screenshots, existing projects, or measured targets. Enforces source extraction, physical baseline modeling, port/material/boundary checks, single-parameter scans, sensitivity analysis, built-in optimizer use, and final verification. Especially relevant for wideband RF feeds, microstrip/coax baluns, antennas, metasurfaces, and the current 2-18 GHz sinuous antenna balun project.
---

# EM Simulation Reproduction

## Operating Rules

- Correct modeling comes before optimization. Do not launch an optimizer until the geometry, materials, ports, boundaries, solver setup, and reference impedances are physically credible.
- Do not improve plots by silently changing ports, reference planes, boundary conditions, materials, renormalization, de-embedding, or post-processing definitions.
- Do not fabricate simulation results. Report exact result file paths, frequency points, and whether a solve/export failed.
- Do not tune many variables at once. First establish baseline behavior, then run one-parameter scans, then choose 2-4 optimizer variables.
- Prefer CST/HFSS built-in parameter sweeps, DOE, response surface, Trust Region, Pattern Search, SNLP, Quasi-Newton, GA/PSO/CMA-ES, or equivalent mature optimizers. Do not use random script searches as the main optimization method.
- Treat sudden S-parameter improvement after a port/reference change as suspect until current/field distributions and reference definitions are checked.

## Workflow

1. **Extract sources first**: make a table of frequency band, targets, geometry, materials, ports, boundaries, solver settings, and post-processing. Mark missing data as "not given" and state engineering assumptions separately.
2. **Build a baseline**: reproduce the paper/original design without optimization. Parameterize critical dimensions but keep initial values faithful.
3. **Validate the model**: check metal continuity, ground continuity, coax inner/outer conductors, dielectric clearances, differential/common-mode definitions, port integration lines, wave-port size, boundary spacing, and mesh density around gaps, vias, tapers, and feeds.
4. **Run baseline simulation**: export raw S-parameters and required derived data. Compare against the paper/target in a table before changing dimensions.
5. **Diagnose differences** in this order: units, geometry, materials, ports, boundaries, mesh, sweep method, then post-processing.
6. **Run one-parameter scans**: one variable at a time, 5-9 points when practical. Record trend, best point, and whether the parameter is suitable for optimization.
7. **Run sensitivity analysis**: identify variables that affect resonance, matching, bandwidth, insertion loss, amplitude balance, phase balance, gain, efficiency, beam squint, or cross-pol.
8. **Define a broadband objective**: include the full target band and all relevant metrics, not only one frequency or S11.
9. **Use a built-in optimizer** only after baseline and scans. Start local when close to target; use DOE/response surface/global algorithms only after trend evidence.
10. **Verify the best candidate** with higher mesh fidelity, discrete/critical frequency checks, unchanged port references, current/field plots, geometry inspection, and manufacturing/space constraints.

## Required Output Tables

For paper/design intake:

| Topic | Extracted value | Source | Missing/assumption |
|---|---|---|---|

For parameterization:

| Parameter | Initial | Lower | Upper | Unit | Physical role | Main impact | Optimize |
|---|---:|---:|---:|---|---|---|---|

For baseline comparison:

| Metric | Paper/target | Baseline result | Difference | Likely cause |
|---|---:|---:|---:|---|

For scans:

| Scan parameter | Range | Main impact | Trend | Suitable for optimization | Recommended range |
|---|---|---|---|---|---|

For optimization history:

| Round | Algorithm | Variables | Ranges | Best parameters | Improved metrics | Worse metrics | Judgment | Next step |
|---|---|---|---|---|---|---|---|---|

For final verification:

| Metric | Baseline | Optimized | Target | Pass |
|---|---:|---:|---:|---|

## Wideband Balun Requirements

- Evaluate S11, S21, S31, output amplitude imbalance, output phase difference, insertion loss, common-mode leakage, and current direction. S11 alone is insufficient.
- Confirm that the output is a true balanced odd mode. For split single-ended output ports, expect similar magnitudes and about 180 deg phase difference without moving reference planes to fake phase.
- Keep coax launches physical: inner conductor, dielectric annulus, outer conductor tied to ground, valid wave/discrete port cross-section, and no overlap with radiator metal.
- For 2-18 GHz designs, judge the full band at key points such as 2, 3, 4, 6, 8, 10, 12, 14, 16, and 18 GHz.
- A standalone balun that meets return loss does not automatically integrate with the antenna. Re-check the antenna input impedance and loading at the actual connection pads.

## Antenna Integration Requirements

- Verify the antenna alone, the balun alone, then one balun plus one polarization, then two orthogonal baluns.
- Do not place bottom-feed microstrip inside absorber/cavity material unless that is the intended physical layer stack.
- Avoid crossed or overlapping coax probes, balanced pins, pads, or balun traces. If a route crosses, use an explicit multilayer/air-bridge/via transition and verify isolation.
- For dual-linear sinuous feeds, excite H and V independently with the other port terminated. Do not use +/-90 deg phase unless circular polarization is explicitly required.
- When integration degrades S-parameters, first check balun output impedance versus antenna differential input impedance, center-feed loading, probe length/common mode, ground interruptions, and feed-line radiation.

## Automation Discipline

- Keep one active CST/HFSS model family per stage. Avoid opening many solver instances in parallel unless the task is an explicit batch sweep.
- Record every run: project path, script/macro path, changed parameters, solver settings, result path, and key metrics.
- Use full available CPU/GPU acceleration when supported, but do not change solver type in a way that invalidates comparison with the baseline.
- Export both raw data and plots when possible. Preserve native S-parameter files, derived CSV summaries, and screenshots of geometry/current/field checks.
- Read [references/sinuous_balun_project.md](references/sinuous_balun_project.md) when working on the current 2-18 GHz sinuous antenna/balun project.
- Read [references/howtosim_notes.md](references/howtosim_notes.md) only when adapting examples from the local HowtoSim script archive.
