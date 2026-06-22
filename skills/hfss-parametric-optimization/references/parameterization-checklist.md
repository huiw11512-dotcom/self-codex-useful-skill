# HFSS Parametric Optimization Checklist

Use this checklist before claiming a project is parameterized, optimized, or ready for delivery.

## Source Extraction

- Target frequency points and bands are listed.
- Required metrics are listed: S11, VSWR, input impedance, gain, direction pattern, beam direction, efficiency if needed.
- Geometry dimensions are mapped to coordinate axes.
- Materials and conductors are identified.
- Port family and reference definition are identified.
- Boundary and far-field setup are identified.
- Known CST/HFSS baseline files and import/export paths are recorded.

## Geometry and Parameters

- Variables are declared before geometry creation.
- Each variable has a physical role and unit.
- Derived dimensions are expressed from parent variables.
- Optimized variables appear in geometry or solver expressions.
- Imported STEP bodies are repaired only where necessary; unrelated topology is preserved.
- Redrawn objects are named consistently and do not duplicate old solids.
- Dependent features update together:
  - coax inner diameter updates inner pin and dielectric void;
  - coax outer diameter updates dielectric and shield void;
  - ridge spacing updates bridge length and feed clearance;
  - dielectric thickness updates sheet thickening and clearance checks;
  - grid count/diameter/positions update all sidewall ribs.

## Boolean Integrity

- Unions connect conductors that should be equipotential.
- Subtractions remove real material from the correct blank object.
- Tool solids do not remain in the final EM model unless intentionally kept.
- Imported PEC sheets/solids are not accidentally assigned dielectric material.
- Dielectrics do not overlap PEC unless explicitly subtracted or allowed by solver intent.
- Parameter extremes have been checked for self-intersection, zero-length objects, and invalid face references.

## Ports

- Coax/circuit/wave/lumped port choice is stated and stable across comparisons.
- The reference conductor is physically connected to ground/outer shield where required.
- The signal conductor is physically connected to the intended feed/ridge.
- The port cross-section is not buried in an invalid overlap.
- Port integration/reference direction is documented.
- Renormalization and impedance are stated and not changed to fake matching.

## Setup and Solves

- `validate_simple()` or equivalent validation passes before solve.
- Setup frequency and sweep points match target frequencies.
- Fields are saved where far-field screenshots are required.
- Solve return values are checked.
- Missing solution data is treated as a failure, not as a zero/blank result.
- Stale `.lock`, `.auto`, `.autotemp`, and polluted result folders are cleaned only for the target project.

## Scans and Optimization

- Baseline metrics are exported before scanning.
- One-parameter scans identify which variables matter.
- Optimetrics variables are limited to meaningful, validated variables.
- Bounds are physically plausible and do not create invalid booleans.
- Goals include all required frequencies.
- Broadband VSWR goals use the correct conversion:
  - VSWR <= 2.5 -> `mag(S11) <= 0.428571`.
- Post-optimization variables and metrics are exported.
- The selected final design is solved again as a normal design, not only reported from optimizer history.

## Screenshots and Reports

- Model screenshots are from HFSS/CST native model views when required, not illustrative redraws.
- Direction plots state frequency, Phi cut, Theta range, and gain quantity.
- Theta range matches the user request, such as -180 deg to 180 deg.
- Gain-vs-frequency summary is included when comparing stages.
- Reports use a consistent language and font style requested by the user.
- Final package contains exactly the files requested, without extra debug scripts unless requested.

## Stop Conditions

Stop and report honestly when:

- The trusted baseline cannot be reproduced in HFSS.
- A variable does not affect geometry or results.
- Optimization improves one target by breaking other required targets.
- Low-frequency matching requires a topology change beyond the allowed geometry.
- Far-field export or screenshot generation hangs after reasonable retry; provide existing solved data and state the limitation.
