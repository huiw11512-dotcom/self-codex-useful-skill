# HFSS Control Workflow

## Environment

- Use the local Ansys Electronics Desktop install available on this machine.
- Confirm the `ANSYSEM_ROOT242` environment variable or the AEDT executable path before launching.
- Prefer PyAEDT for repeatable project creation, validation, setup creation, and solve automation.

## Standard Sequence

1. Inspect the current `.aedt`, generator script, result folder, and logs.
2. Decide whether to edit the existing project or rebuild from a clean state.
3. If rebuilding, close AEDT first and remove only generated project artifacts.
4. Launch HFSS through PyAEDT.
5. Build parameterized geometry and assign materials.
6. Assign ports, boundaries, setups, and sweeps.
7. Save the project, run one coarse solve, and inspect the log.
8. If the first solve converges, tune dimensions and sweep limits.

## Common Failure Modes

- Internal or buried wave-port face: move the port to an exterior solve boundary, or create a valid internal-port cap.
- Repeated geometry names: rebuild the project from a clean directory.
- Immediate solve failure: inspect `batch.log` and the PyAEDT log for port or geometry errors.
- Sweep completes but results look wrong: check feed mapping, excitation phases, and active source definitions.

## Report Back

- Exact project path.
- Whether the project was rebuilt or edited in place.
- Whether validation passed.
- Whether the setup and sweep converged.
- Exact frequency points used for S-parameter checks.
