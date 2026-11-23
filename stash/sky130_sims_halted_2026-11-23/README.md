<!--
SPDX-FileCopyrightText: 2026 Christoph Maier
SPDX-License-Identifier: Apache-2.0
-->
# sky130 feasibility simulations of the reference-current cores

**sky130 pre-layout schematic simulation (feasibility, not sign-off).** These runs check
whether the two reference-current cores of the IHP sg13cmos5l design
(`tatzelbrumm/sg13cmos5l_cm_ip__single2diff2single`, commit 9052bd3, macros `bg_core_pd` and
`oa_core_pd`) can be ported to sky130A. Every number in `results/` comes from the decks in this
directory. IHP numbers quoted below are for orientation only; they are not sky130 results.

## Versions

- ngspice-47 (`/usr/local/bin/ngspice`, `ngspice -v`: build date Fri Oct 30 17:16:00 UTC 2026, KLU)
- sky130A installed with ciel, open_pdks 1689ac3f2dc763876eaf967227c7dfe831b031ae
  (`$PDK_ROOT/sky130A/SOURCES`), sky130_fd_pr 403964dc7f9cca5ec1a8cc7b4f2a6f532b781676
  (`.config/nodeinfo.json`); only library sky130_fd_pr is used
- model library `$PDK_ROOT/sky130A/libs.tech/ngspice/sky130.lib.spice`, ngspice init from
  `$PDK_ROOT/sky130A/libs.tech/ngspice/spinit` (copied to `.spiceinit` in the run directory)
- Python 3.13.18, matplotlib 3.11.2

## How to reproduce

```sh
cd verification
PDK_ROOT=/foss/pdks SIM_DIR=/tmp/sky130_cm_sim ./run_all.sh            # everything, ~10 min on 4 cores
PDK_ROOT=/foss/pdks SIM_DIR=/tmp/sky130_cm_sim ./run_all.sh smoke meas # selected groups
```

`run_all.sh` forces `PDK=sky130A`, expands the deck templates with `scripts/run_sims.py`
(tokens `@PDK_ROOT@ @PDK@ @CORNER@ @OUT@ @NETLIST@ @DUT@ @CHECKNODES@`; ngspice does not expand
environment variables in `.lib`), runs ngspice in parallel, and calls `scripts/summarize.py`, which
writes `results/*.md` and `results/*.png`. Expanded decks, logs and data stay in `$SIM_DIR`
(no raw output in `verification/`).

## Files

| file | content |
|---|---|
| `netlists/bg_core_sky130.spice` | Banba current-mode bandgap core with start-up and power-down (sizes and reasoning in comments) |
| `netlists/oa_core_sky130.spice` | Oguey-Aebischer MOS-only core with start-up and power-down |
| `decks/tb_smoke.spice` | Id-Vgs of nfet/pfet_g5v0d10v5 and nfet/pfet_01v8, tt, 27 C |
| `decks/tb_ref_dc.spice` | per library section: T sweeps (up and down) at 3.0/3.3/3.6 V, vdd sweeps at -40/27/125 C, disabled state |
| `decks/tb_ref_tran.spice` | per library section: supply-ramp start-up, 10 us and 1 ms ramps, -40/27/125 C, 3.0/3.6 V |
| `decks/tb_meas_path.spice` | test-plan dry run: 5 ohm series switch into an external 0.7 V ammeter |
| `scripts/run_sims.py`, `scripts/summarize.py`, `run_all.sh` | runner, plots/tables, top-level script |
| `results/smoke.md`, `results/bg_core.md`, `results/oa_core.md`, `results/meas_path.md` | tables (min/typ/max with conditions) |
| `results/*.png` | plots referenced from the tables |

## Device mapping and topology changes

- `sg13_hv_nmos` / `sg13_hv_pmos` -> `sky130_fd_pr__nfet_g5v0d10v5` / `sky130_fd_pr__pfet_g5v0d10v5`
  (5 V gate oxide, used at 3.0..3.6 V).
- `rhigh` -> `sky130_fd_pr__res_xhigh_po` (generic scalable model, 2 kohm/sq, w = 0.69 um). Its
  corner sections vary R by -/+ 15 %. Magic extracts a 0.69 um wide xhigh_po as
  `sky130_fd_pr__res_xhigh_po_0p69`, a different model whose corner spread is smaller and is
  keyed to `res_high_po__var_mult`; post-layout runs must check this.
- `pnpMPA` -> `sky130_fd_pr__pnp_05v5_W3p40L3p40` (fixed-size vertical PNP; 1 and 8 parallel devices).
- PMOS mirrors: the IHP cores stack two diode-connected PMOS (mirror + cascode). With sky130
  g5v0d10v5 PMOS (|Vt| ~ 1.0 V, VSG ~ 1.2 V at 2.5 uA and -40 C) the stack leaves V(vpc) =
  0.25..0.40 V at 3.0 V, -40 C (tt/ss), below the ~0.79 V the NMOS pair needs. All PMOS pairs
  are therefore **self-cascodes** (long mirror device + wide cascode, common gate vpg).
  Start-up (MS1 chain, MS2, MS3) and power-down switches (SKS, SVPG) are kept, acting on vpg.
- Bandgap: R1B = R1A x 10/11 is kept from IHP; it is essential. Without it (first sky130
  version, R1A = R1B) a supply-ramp transient at ss, -40 C, 3.0 V settled at 2.6 uA with both
  PNPs off (V(ea) = V(eb) = 0.48 V).
- OA core: MCS = MCL width reduced from 3.4 to 2.0 um (L = 30 um) for about 5 uA at tt, 27 C.

Corner sections: MOS tt/ss/ff/sf/fs (the vertical PNP Is/beta follow ss/ff; tt/sf/fs are the
same for the PNP). Resistor corners exist separately as `ll`/`hh` (tt MOS) and `<c>_ll`/`<c>_hh`;
the bandgap runs all 15 combinations, the OA core (no resistor) the 5 MOS corners.

## Numerical aids (and why)

- `.option rshunt=1e12` (1 Tohm from every node to ground, <= 3.6 pA per node) in all reference
  decks. The disabled-state currents are therefore only resolved down to this level.
- The PDK xhigh_po body resistance grows with |V| at large |V|. ngspice sometimes accepts a
  spurious DC point with internal nodes at 1e5..1e8 V. `tb_ref_dc` saves internal node voltages;
  `summarize.py` rejects any point with a node outside -0.2 V..vdd + 0.2 V, takes each
  temperature from the other sweep direction, and reports how many points it rejected.
- Transients use Gear integration. A run that aborts with "timestep too small" near vdd = 0 is
  repeated with gmin 1e-14, 1e-15, 1e-13; the tables list the runs that needed this.
- In `tb_meas_path`, trapezoidal integration showed a fake -26 uA tail (numerical ringing of the
  5 ohm x 0.5 pF node); Gear removes it.

## What the results mean and what they do NOT show

See the tables in `results/`. In short: the sky130 ports bias at ~5 uA, start up from supply
ramps at all simulated corners, temperatures and supplies, and show the spread, supply
sensitivity and TC listed there. Not covered: mismatch / Monte Carlo (the offset of the NMOS
pair and mirrors sets the real bandgap accuracy), layout parasitics, extracted-resistor models,
noise, PSRR vs frequency, enable/disable transients, ESD/pad leakage, aging, silicon. The
sizes are first cuts, not optimized. The OA core keeps the IHP device ratios; its temperature
behaviour in sky130 differs from IHP (see `results/oa_core.md`).
