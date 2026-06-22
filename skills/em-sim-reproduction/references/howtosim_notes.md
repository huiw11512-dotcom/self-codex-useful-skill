# HowtoSim Script Archive Notes

Local archive: `C:\Users\Administrator\Downloads\HowtoSim_Script-master.zip`.

The archive is primarily HFSS/AEDT automation examples. Use it as a scripting reference, not as evidence that a CST/HFSS electromagnetic model is correct.

Useful categories:

- Export/report helpers: `exportReport.py`, `ExportSweepImages.py`, `html_XY_Plot.py`, field-data export examples.
- Port/layout helpers: `CircuitPortEditor.py`, `DiffVia_Builder.py`, `Via_Array_Builder.py`, `Via_Fence_Generation.py`.
- Geometry helpers: `BuildArray.py`, `Flex_CPWG.py`, `BendingToolkit.zip`, `zigzag.py`.
- HFSS setting/property helpers: `get_HFSS_Setting_Info.py`, `exportDesignProperties.py`, `importDesignProperties.py`.
- Batch/automation examples: `BatchSim.py`, array/beam sweep examples, PyAEDT notebooks.

When adapting a script:

1. Extract only the needed file into a temporary working directory.
2. Read the script before running it; do not run unknown AEDT/CST automation blindly.
3. Preserve physical port/material/boundary definitions from the current model.
4. Use the script for repeatable export, reporting, or geometry generation only after the baseline model is verified.
