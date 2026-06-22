# Current Sinuous Antenna / Balun Project Notes

Use these notes only for the current workspace `E:\codex_ceshi\sinous`.

## Physical Target

- Product envelope: about `90 mm x 90 mm x 35 mm`.
- Current antenna body: about `74 mm` diameter and `32-34 mm` height.
- Required feed: two bottom SMA-K/coax inputs for H and V linear polarization.
- Target band: `2-18 GHz`.
- Antenna type: cavity-backed four-arm sinuous.
- Desired final flow: standalone balun -> one balun plus one polarization -> two orthogonal baluns -> final antenna far-field validation.

## Source Documents

- `2GHz-18GHz Dual-Polarized Sinuous Antenna Datasheet.pdf`
- `Klopfenstein_tapered_218_GHz_microstrip_balun.pdf`
- `A_planer_sinuous_antenna_and_the_relevant_balun.pdf`
- `Optimization_of_microstrip_tapered_balun_for_sinuous_antenna_feeding_circuits.pdf`
- `A_Wideband_Dual_Polarized_Sinuous_Antenna_with_Tapered_Microstrip_Balun_Feeds.pdf`
- `Four-Arm_Sinuous_Antenna_With_Low_Input_Impedance_for_Wide_Gain_Bandwidth.pdf`

## Verified Project State

- Original CST model: `1.cst`.
- The original Antenna Magus feed ports are high-impedance differential ports, about `267 ohm`, not ordinary 50 ohm loads.
- If exported/renormalized to 50 ohm, the original antenna appears badly matched. Use explicit no-renormalized/native-reference exports when comparing to the inherited model.
- Native/no-renormalized original antenna baseline is weak at low band: about `S11=-7.3 dB` at `2 GHz`, about `-10 dB` at `3 GHz`, then mostly better above `4 GHz`.
- This means a 50 ohm coax-to-130 ohm differential balun is not automatically correct for the current antenna center. The current model points closer to `50 ohm coax -> about 267 ohm differential` unless the antenna center feed is redesigned.

## Current Balun Findings

- Best standalone U-folded Klopfenstein-like balun with small optimized launch: `u_balun_optimized_current.cst`.
- It has roughly `S11/S22 <= -10 dB` over 2-18 GHz and average insertion loss about `0.5 dB`, but its launch uses small optimized dimensions rather than official SMA geometry.
- Official-style SMA dimensions tested: inner radius about `0.46 mm`, dielectric radius about `1.46 mm`, outer radius about `2.05 mm`, PTFE/Teflon `er≈2.1`.
- Official-style SMA launch with the same U balun is not acceptable yet: several high-band points are only about `-6` to `-9 dB`, and the best tested official launch remains far from `-10 dB` full-band.
- Do not claim the official-SMA version is solved until the coax-to-microstrip launch is physically redesigned and verified.

## Integration Pitfalls Already Observed

- Long bottom-to-top balanced probes cause severe broadband mismatch.
- Placing balun metal inside the bottom cavity/absorber layer is physically wrong unless a real feed PCB layer is defined there.
- Previous two-balun attempts had crossed or overlapping coax/probe geometry. Do not reuse those geometries.
- Large four-sector center pads can short or heavily load the sinuous arms. The original feed tabs are extremely small; practical pads must be introduced gradually and checked by current/continuity inspection.
- A good standalone balun does not guarantee integrated match. The antenna center loading dominates the current single-H failures.

## Recommended Next Engineering Steps

1. Freeze the original antenna native-reference baseline and document its port impedance/reference.
2. Build a physically correct official-SMA standalone balun baseline and diagnose the launch, not the whole taper.
3. Sweep only launch variables first: coax pin landing pad, ground antipad, coax protrusion length, short taper into microstrip, and shield/ground geometry.
4. Once standalone official launch is credible, connect one balun to one polarization with explicit non-overlapping geometry.
5. Only after one polarization is physically and electrically credible, mirror/rotate for dual H/V integration.

## Reporting Requirements For This Project

- Always report S-parameters at `2, 3, 4, 6, 8, 10, 12, 14, 16, 18 GHz`.
- For standalone balun, report S11, S21/S31 or differential S21, S22, amplitude balance, phase balance, and current sanity checks.
- For integrated antenna, report S11/S22/S21 isolation, realized gain, co/cross-pol, front-to-back ratio, 3 dB beamwidth, beam squint, and feed-current distribution when available.
- Keep root clutter low. Store temporary scripts/results under `codex_artifacts/tmp` or stage-specific result folders.
