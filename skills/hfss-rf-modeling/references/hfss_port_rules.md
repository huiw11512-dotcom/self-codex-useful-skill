# HFSS Port Rules

## Coax Feed

A coax feed needs three physical regions:

- Inner conductor: continuous pin from the coax reference plane to the radiator/probe.
- Dielectric annulus: air/PTFE/vacuum between inner and outer conductors.
- Outer conductor: shield tied electrically to the ground plane.

Preferred excitation:

- Use a wave port on the coax end cross-section.
- The port face must be at the coax end and expose both inner and outer conductors.
- The integration line starts on the inner conductor and ends on the outer conductor.
- Put the port on the exterior simulation boundary when HFSS requires it.

Acceptable temporary excitation:

- A lumped port across the coax annulus at the coax end, inner-to-outer.
- It should be below the ground/reference plane, not beside the radiator above the ground.

Avoid:

- Rectangular sheets beside the monopole base as the final feed.
- Port sheets placed on top of the ground clearance to imitate a coax mode.
- Outer conductor overlapping the ground volume; touch/unite it instead.

## Microstrip Feed

For a microstrip line, the port must reference the strip conductor and ground:

- Wave port: rectangle on the board edge including strip, substrate height, and ground reference.
- Lumped port: sheet/face from strip edge to ground at the reference plane.
- The terminal/integration line goes from signal trace to ground.

Avoid:

- Ports inserted deep into substrate or metal.
- Ports that only touch the strip and not the return conductor.
- Changing a requested microstrip input into coax without approval.

## Via/Probe To Antenna

For a probe-fed monopole/patch above a ground plane:

- Cut a clearance hole in the ground around the probe unless that probe is meant to short to ground.
- Keep the probe conductor continuous from the feed network output to the radiator.
- In integrated array mode, the feed network output is the source path; do not add a separate output S-port at the antenna unless the user requests a diagnostic port.

## Port Debug Checklist

Before simulation:

- Confirm the expected number and names of excitations in HFSS.
- Inspect all port faces visually after hiding air/substrate if needed.
- Check that each port has the intended reference conductor.
- Confirm no port face intersects a solid conductor.
- Confirm no duplicate or stale port from an earlier model remains.

If HFSS reports repeated port errors:

- Delete stale boundaries before recreating ports.
- Rebuild only the port objects and related booleans where possible.
- Export or list boundary assignments from the script/log.
- Run a single-frequency solve before sweeping.
