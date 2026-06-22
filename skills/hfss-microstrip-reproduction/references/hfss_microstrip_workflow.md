# HFSS Microstrip Reproduction Workflow

## 1. Extract Inputs

Capture these before modeling:

- Frequency band and center frequency.
- Substrate permittivity, loss tangent, thickness, copper thickness.
- Every target impedance and whether each segment is quarter-wave.
- Port numbering and physical meaning.
- Figure topology and physical orientation.
- Required metrics and whether they are band-wide or center-frequency only.

If substrate data is missing, choose the value used by the paper/demo/calculator only as an explicit assumption and record it in the report.

## 2. Synthesize Geometry

Use impedance formulas before optimization. For microstrip, calculate width for every target impedance and calculate guided quarter-wave length using the effective permittivity for that width.

Do not reuse a width table after changing substrate height or permittivity.

Generate a table like:

| Name | Z0 ohm | Width mm | eps_eff | quarter_wave_mm |
|---|---:|---:|---:|---:|

## 3. Build Geometry

Recommended construction order:

1. Compute trace segment bounding boxes.
2. Create substrate and ground with clearance around all traces and port feed lines.
3. Create top copper segments using synthesized widths and lengths.
4. Unite only the top copper segments.
5. Create port sheets.
6. Assign excitations with explicit integration lines.
7. Create air region and radiation/open boundary only if the model needs it.
8. Add setup and sweep.
9. Save the project.

Keep the script able to overwrite the same AEDT project. Delete only artifacts belonging to the target project when a clean rebuild is needed.

## 4. Microstrip Lumped Port Construction

For a top microstrip over bottom ground:

- Signal z = substrate top + copper top/reference.
- Ground z = bottom ground top or bottom reference, consistently documented.
- Port height = substrate height + copper thickness when the sheet starts at ground plane and ends at trace top.
- Integration line goes signal to ground unless a deliberate phase-reference reversal is required.

AEDT rectangle axis reminder:

- `WhichAxis="X"` means rectangle lies in the Y-Z plane.
- `WhichAxis="Y"` means rectangle lies in the X-Z plane.
- `WhichAxis="Z"` means rectangle lies in the X-Y plane.

For a Y-normal port at `y = y0`, use X span for the trace width and Z span for port height. If endpoints are rejected, the line is not on the sheet or the rectangle dimensions were swapped.

## 5. Solve and Export

Start with a coarse sweep such as 8-12 GHz with 0.5 or 1 GHz step to validate ports and topology. Increase mesh/sweep density only after the metrics are qualitatively correct.

Prefer exporting:

- Touchstone `.sNp`
- Raw CSV with `dB(S(...))` and `ang_deg(S(...))`

Avoid native AEDT arithmetic traces for final metrics on AEDT 2018 unless needed for screenshots.

## 6. Debug Order

If results are poor:

1. Check port count, names, and integration direction.
2. Check geometry against paper figure.
3. Check substrate and width synthesis.
4. Check quarter-wave length and whether bends/junctions add electrical length.
5. Check port reference-plane extensions.
6. Check phase expression units (`180deg`, not `180`).
7. Only then tune compact physical variables.

