---
name: hfss-parametric-optimization
description: Build, repair, simulate, and optimize HFSS/PyAEDT electromagnetic models with physically meaningful parameterized geometry, boolean operations, ports, sweeps, far-field outputs, and Optimetrics goals. Use when reproducing CST/HFSS antenna or RF structures, converting STEP/CST geometry into HFSS, creating variable-driven models, setting wave/circuit/coax ports, validating solves, exporting S-parameters/VSWR/gain/pattern screenshots, or diagnosing why an optimization variable is ineffective.
---

# HFSS Parametric Optimization

## Purpose

Use this skill for HFSS projects where parameters must drive real geometry and solver behavior. A valid parametric model is not a collection of boxes with variable names; each optimization variable must alter the actual solids, sheets, booleans, ports, boundaries, mesh, or material definitions that determine the EM response.

## Operating Rules

- Start from source evidence: CST files, STEP exports, screenshots, dimensions, paper figures, port type, solver settings, and target metrics.
- Preserve the physical topology first. Do not redraw a loose visual approximation when a verified CST/STEP baseline exists.
- Parameterize by design intent: a variable must map to a named physical feature and update all dependent operations.
- Keep boolean history meaningful: holes, coax passages, dielectric cutouts, ridge clearances, unions, subtractions, and sheet thickenings must reference the same variables as the geometry they constrain.
- Validate before optimizing. Never run Optimetrics on a model with invalid booleans, floating conductors, bad ports, missing fields, or stale solution data.
- Do not silently improve results by changing port family, reference impedance, de-embedding, boundary, solver type, renormalization, or post-processing definition.
- Record every run: project path, design name, variables, setup/sweep names, S-parameters, VSWR, gain, pattern plots, and known failures.

## Workflow

1. **Extract the baseline**
   - List dimensions, coordinate system, materials, conductors, dielectrics, sidewalls, grids, ridges, feed, port, boundaries, and target frequencies.
   - If CST is the trusted geometry, export STEP/SAT and import into HFSS for geometric fidelity. Only redraw from scratch after proving the import cannot support the required edits.

2. **Build the physical model**
   - Define variables before geometry creation.
   - Build features from variables, not from fixed numbers copied into variable tables.
   - For derived features, express dependencies explicitly: ridge gap controls feed bridge length, coax hole radius controls wall cutout, dielectric clearance controls both dielectric profile and ridge subtraction.
   - Use structured geometry APIs: cylinders for coax, polylines/sheets for ridge-matched dielectric, thicken_sheet for finite-thickness sheets, and boolean subtract/unite for actual topology.

3. **Tie parameters to boolean logic**
   - Every optimized dimension must affect at least one downstream object or operation.
   - When a variable changes, re-check dependent booleans: feed passage, coax dielectric void, outer shield void, ridge overlap clearance, dielectric-ridge subtraction, grid-to-wall intersections.
   - Use stable naming for objects that Optimetrics or post-processing will reference.
   - Prefer robust parameter ranges that do not create self-intersections, zero-length ports, or tool solids larger than blanks.

4. **Set physically valid ports**
   - Coax feeds require inner conductor, dielectric/air annulus, outer shield/reference conductor, and a port on a credible cross-section or circuit reference pair.
   - Wave ports should sit on an exterior solve boundary unless the internal construction is explicitly valid.
   - Circuit/lumped ports must have a real reference conductor and should not float inside dielectric or intersect unrelated PEC.
   - Integration/reference direction must match intended excitation. Keep port family fixed across comparisons.

5. **Validate and solve**
   - Run HFSS validation (`validate_simple()` or closest AEDT validation) before solving.
   - Solve a coarse baseline first with critical discrete points; do not start with a broad optimization.
   - Export exact point results for S11 magnitude/dB, VSWR, input impedance, gain, and far-field cuts. Use raw CSVs plus plots/screenshots.
   - If a solve fails or produces no data, inspect geometry validity, port assignments, field setup names, and stale lock/results files.

6. **Scan before optimizing**
   - Perform one-parameter scans over 5-9 values for likely-sensitive dimensions.
   - Rank parameters by actual metric movement, not by intuition.
   - Discard variables that only change documentation values or have negligible effect on the failing metric.

7. **Set Optimetrics goals**
   - Include all target frequencies and all required metrics. For broadband matching, convert VSWR target to `mag(S11)` target, e.g. VSWR <= 2.5 means `|S11| <= 1.5/3.5`.
   - Weight goals according to delivery priority, but verify that improving one point does not break other required points.
   - Use compact ranges based on scan evidence. Wider ranges are not better if they create invalid topology.
   - After optimization, re-run the final selected design as a normal HFSS solve and export fresh results.

8. **Export deliverables**
   - Save the `.aedt` project and any required `.aedtresults` if the user needs solved data.
   - Export screenshots/plots for model view, S11, VSWR, gain-vs-frequency, and far-field patterns over the specified angular range.
   - For reports, label exact project paths and result CSVs internally, but omit noisy file inventories if the user asks for only models and results.

## Parameterization Standard

A parameter is valid only when it satisfies all checks:

- It appears in the HFSS variable manager.
- It is used by at least one geometry, material, port, boundary, mesh, or setup expression.
- Changing it and updating the model changes the relevant object dimensions or operation positions.
- Dependent booleans still execute across its optimization range.
- The resulting port and conductor topology remains physically valid.
- It has measurable impact on at least one target metric in a scan or optimizer history.

If any check fails, treat the parameter as cosmetic and do not claim the model is truly parameterized.

## Boolean Modeling Patterns

- **Coax feed:** create inner conductor cylinder, dielectric/air cylinder, subtract inner void, create outer shield cylinder, subtract dielectric void, unite shield to reference metal, unite pin to feed/ridge where intended.
- **Wall feed passage:** subtract a coax-clearance cylinder from imported wall/transition metal using the same coax radius variables.
- **Ridge-matched dielectric:** sample or express the ridge inner contour, create a closed sheet in the center ridge plane, thicken it with the thickness variable, subtract from ridge metals with clearance variable.
- **Grid sidewalls:** grid post count, diameter, and positions must derive from aperture/flare variables; avoid first/last posts intersecting solid walls unless intended and validated.
- **Capacitive/inductive feed tuning:** ensure added plates/posts are connected to the intended conductor and do not short the opposite ridge unless that is the design.

## Diagnostics

- If 0.6 GHz or another low frequency remains badly matched while higher frequencies pass, export input impedance and S11 phase before adding variables. Strong inductive/capacitive behavior often requires a topology change, not more dielectric thickness scanning.
- If Optimetrics changes only one variable, compare baseline and post variables; the other variables may be ineffective or constrained by invalid ranges.
- If a redraw model differs badly from CST/STEP, stop optimizing it and return to the verified geometry baseline.
- If far-field export hangs, use already-solved field setups or saved CSVs; do not block indefinitely on screenshots.

## Reference

For a stricter audit checklist, read `references/parameterization-checklist.md`.
