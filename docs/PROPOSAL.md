<!--
SPDX-License-Identifier: Apache-2.0
-->
# Proposal, Chipalooza Challenge #4 (Chip Foundry Sky130): custom single-to-differential and differential-to-single analog pads with selectable reference circuits

Status: proposal of 2026-11-23. Everything stated for sky130 is a **target** (a proposal) unless it is explicitly labelled
*sky130 pre-layout schematic simulation (feasibility, not sign-off)*. Observed values quoted from the predecessor design are
**IHP sg13cmos5l simulation results**, not sky130 results; their source files and commits are listed in
[SOURCES.md](SOURCES.md). "TBD" marks what is not known yet, with what determines it.

Contents: 1 Type of IP block · 2 I/O list including test ports · 3 Functional description · 4 Target specification ·
5 Test plan outline · 6 Port plan · 7 Risks · 8 Schedule · 9 License · 10 AI assistance

---

## 1. Type of IP block

**A proof of concept of custom analog pads**, ported from a design taped out on IHP sg13cmos5l (Chipalooza Challenge #2, slot 7,
November 2026), consisting of:

- **S2D pad**: a buffered single-ended-in, differential-out analog input pad. Pad voltage in, differential pair out:
  `outp − outn = 2 (pad − vref)`, `(outp + outn)/2 = vcm`.
- **D2S pad**: a buffered differential-in, single-ended-out class-AB analog output pad that drives the bond pad through
  output devices that are part of the pad's own clamp structure: `pad − vref = (vinp − vinn)/2`.

Together they carry a single-ended off-chip signal into the core as a differential signal and back out, with gain set by
device matching rather than by resistor ratios. For an SoC this is the analog front and back end that a fully differential
core (filter, ADC driver, DAC output) needs to talk to the single-ended outside world, packed into the pad frame instead of
the core area, with fail-safe enables and low leakage when unpowered. The list of Challenge #1 blocks has no analog pad
buffer and no single-ended / differential converter, so the block fills a gap.

**The pads are the part under review for this proposal.** The supporting circuits are a **fallback for testing** and are
also reusable on their own: an on-slot Oguey–Aebischer MOS-only current reference, an on-slot Banba current-mode bandgap
current reference, a switchable bias distribution, replica generators for `vcm` and `vref`, and 3.3 V mode / enable glue
with fail-safe level shifters. Their specifications are **tentative**, are meant to be better than those of the IHP
predecessor, and are to be reviewed at the final design review. Each supporting circuit can be bypassed by a harness
resource (section 3.4), so the pads can be measured even if an on-slot reference misbehaves.

The block is usable as a unit (pads + references + glue) and as separately reusable cells (each pad alone, each reference alone).

License: Apache-2.0 or Solderpad Hardware License v2.1, pending the organizers' approval (section 9).
AI assistance: the design was created with AI assistance; using, verifying or modifying it does not require AI (section 10).

## 2. List of I/O, including test ports

Harness resources (rules-4 resource list) and what the block uses:

| resource | available | used | for |
|---|---|---|---|
| 3.3 V analog supply / ground | yes | yes | everything analog, pad buffers, references, 3.3 V glue |
| 1.8 V digital supply / ground | yes | yes (small) | only for read-back outputs and pull-downs of `dig_out`; the block works with only 3.3 V on |
| bandgap-referenced bias voltage | 1 | optional (1) | selectable source for `vcm` or `vref` (section 3.4) |
| bandgap-referenced current sources | up to 2 | optional (2) | selectable reference current: harness current 0 / harness current 1 |
| digital controls (inputs) | up to 24 | 14 + project enable | modes, key, reference and voltage-source selection (table below) |
| digital test outputs | up to 12 | 8 | read-back of the decoded mode and enables (new) |
| shared analog lines | up to 4 | 4 | differential monitor / feed (0, 1), `vcm` / `vref` monitor or drive (2, 3) |
| dedicated pins | up to 3 | 2 custom + 1 optional foundry analog pad | S2D pad, D2S pad; optional third pin: reference-current monitor (new) |

**Exceptions that need approval:** (1) the two **custom pads** (rules: "With approval, custom pads may be designed by the
user"; same size and configuration as the foundry pads, abutting cleanly, verified independently with DRC, LVS and
simulation); (2) none for the references: own on-slot references are inside the slot, and the harness references stay
selectable.

Pin table. Column "IHP slot 7" gives the corresponding pin of the taped-out IHP design; **new** means *new, not in the
taped-out IHP slot 7*. Register-level names of the sky130 harness are TBD until the harness repository exists; names below
are generic.

| pin | dir | domain | function | IHP slot 7 |
|---|---|---|---|---|
| `vdda` / `vssa` | supply | 3.3 V | analog supply and ground of block and pad core side | `vdd_3v3` / `vss_3v3` |
| `vccd` / `vssd` | supply | 1.8 V | read-back level shifters, `dig_out` pull-downs only | `vdd_1v2` / `vss_1v2` (1.2 V there) |
| pad ring `vddio` / `vssio` etc. | supply | pad ring | pad buffers' output stage and ESD (custom pads take the ring pins of the foundry frame) | `iovdd iovss vdd vss` |
| `pad_s2d` | in | analog, 0 … 1 V | **S2D pad** (custom), signal input | `s7_an[0]` (custom pad) |
| `pad_d2s` | out | analog | **D2S pad** (custom), signal output | `s7_an[1]` (custom pad) |
| `pad_aux` | out | analog | optional foundry analog pad: selected reference current to an off-chip SMU | new |
| `enable` | in | 1.8 V | project enable: 1 = on in the default mode, 0 = everything off, all switches open | `enable` (1.2 V) |
| `dig_in[0]` | in | 1.8 V | swap: loop crossed (polarity flip) | `dig_in[0]` |
| `dig_in[1]` | in | 1.8 V | mon: S2D `outp` / `outn` → `analog_bus0/1` | `dig_in[1]` |
| `dig_in[2]` | in | 1.8 V | feed: `analog_bus0/1` → D2S `vinp` / `vinn`, loop off (wins over swap and mon) | `dig_in[2]` |
| `dig_in[3]` | in | 1.8 V | key bit, must be 1 for any mode | `dig_in[3]` |
| `dig_in[4]` | in | 1.8 V | key bit, must be 0 for any mode | `dig_in[4]` |
| `dig_in[5]` | in | 1.8 V | ext: replica disconnected, `vcm` / `vref` driven from `analog_bus2/3` | `dig_in[5]` |
| `dig_in[6..7]` | in | 1.8 V | reference current select: 00 Banba (default), 01 Oguey–Aebischer, 10 harness current 0, 11 harness current 1 | new (model: IHP test platform stage B, `dig_in[4..6]` one-hot OA / BG / `ibias0`, not taped out) |
| `dig_in[8]` | in | 1.8 V | `vcm` from the harness bias voltage instead of the replica | new |
| `dig_in[9]` | in | 1.8 V | `vref` from the harness bias voltage instead of the replica | new |
| `dig_in[10]` | in | 1.8 V | selected reference current → `pad_aux` (or `analog_bus3` if no third pin) | new (model: test platform stage A / B bus gates, not taped out) |
| `dig_in[11..12]` | in | 1.8 V | pad bias select (the pads' `sel` input; tied statically in IHP slot 7) | new as a control |
| `dig_in[13]` | in | 1.8 V | read-back enable for `dig_out` | new |
| `dig_in[14..23]` | in | – | not used, tied off inside the block | – |
| `ibias0`, `ibias1` | in | 3.3 V | harness bandgap-referenced currents (selectable reference) | `ibias0/1` existed, unused by the taped-out slot |
| `vbias` | in | 3.3 V | harness bandgap-referenced voltage (selectable `vcm` or `vref`) | unused by the taped-out slot |
| `analog_bus0/1` | io | 3.3 V | S2D outputs monitor (mon) or D2S inputs feed (feed) | same |
| `analog_bus2` | io | 3.3 V | `vcm` monitor (default) or drive (ext) | same |
| `analog_bus3` | io | 3.3 V | `vref` monitor (default) or drive (ext); fallback reference-current monitor | same (current monitor: new) |
| `dig_out[0..5]` | out | 1.8 V | read-back: `en`, loop direct, loop crossed, S2D → bus, bus → D2S, replica connected | new (IHP: all held low) |
| `dig_out[6..7]` | out | 1.8 V | read-back: reference current select | new |
| `dig_out[8..11]` | out | 1.8 V | held low | as IHP (`s7_doutpd`) |

Default with only `enable` = 1 and all `dig_in` = 0: Banba reference (the reference of the taped-out IHP slot 7), replica
`vcm` / `vref`, loop direct, `vcm` / `vref` on `analog_bus2/3`. Whether the default becomes the Oguey–Aebischer core is
decided at the schematic review (TBD).

## 3. Functional description

### 3.1 Signal path

The S2D pad takes the single-ended pad voltage and produces `outp − outn = 2 (pad − vref)` around the common mode `vcm`
(matched-pair differential difference amplifier: four matched units, folded cascode, CMFB; gain from how the matched units
are connected). The D2S pad takes a differential pair and drives the bond pad with `pad − vref_d2s = (vinp − vinn)/2`
(MP-DDA front end, folded cascode, Miller-compensated class-AB output stage that is part of the pad's clamp frame).
In the default loop the S2D output drives the D2S input directly, so the D2S pad reproduces the S2D pad voltage shifted from
the S2D `vref` to the D2S reference (= `vcm`): `pad_d2s = vcm + (pad_s2d − vref)`, for a pad input of 0 … 1 V.

### 3.2 Modes (taped out in IHP slot 7, kept unchanged)

Modes act only with the key `dig_in[3]` = 1 and `dig_in[4]` = 0, so the harness's reset patterns (all inputs equal) give the
default. Default: loop direct, `vcm` on `analog_bus2`, `vref` on `analog_bus3`. swap: loop crossed (output inverted about
`vcm`). mon: S2D outputs also on `analog_bus0/1` (loop stays on; slower while the bus switches load it). feed: `analog_bus0/1`
drive the D2S inputs, loop open. ext: replica generators disconnected, `vcm` and `vref` driven from `analog_bus2/3`.
Logic: `ld = en·¬f·¬s`, `lx = en·¬f·s`, `sb = en·m·¬f`, `bd = en·f`, `rc = en·¬(ext·key)`.

### 3.3 Enable and fail-safe behaviour

`enable` = 0 opens every switch, turns the references and the bias distribution off (outputs high-impedance, tree nodes
pulled to the rails) and holds the pad outputs at their disabled state; the block draws leakage only. The 1.8 V controls
enter through fail-safe level shifters powered from the 3.3 V supply alone, so the block works with only 3.3 V on, and an
unpowered block does not load the pads beyond leakage. (In IHP these shifted 1.2 V harness levels to 3.3 V; in sky130 the
input level is 1.8 V.)

### 3.4 References and voltage sources (selectable)

| item | source options | status |
|---|---|---|
| reference current (≈ 5 µA, sourced) for the pads' bias trees and the replica | Oguey–Aebischer core / Banba bandgap core / harness current 0 / harness current 1 | Banba: taped out in IHP slot 7. Oguey–Aebischer: built and verified on IHP (DRC, LVS, PEX), used in the IHP test platforms, **not in the taped-out slot 7**; proposed here as part of the block. Harness currents and the 4-way selection: new (model: test platform stage B selection OA / BG / `ibias0`) |
| `vcm` (S2D output common mode = D2S reference, centre of the linear band) | replica generator / harness bias voltage / `analog_bus2` | replica and bus: taped out (ext mode). Harness voltage: new; usable only if the harness voltage lies in the `vcm` window (TBD: harness voltage reference specification) |
| `vref` (S2D reference, ≈ 0.5 V, lower end of the pad range) | replica generator / harness bias voltage / `analog_bus3` | as for `vcm`; harness voltage for `vref` only if it lies in the `vref` window (TBD) |

**Replica-bias principle.** `vcm` and `vref` are not resistive dividers: they come from replicas of the pads' input and
fold-node devices, biased from the same reference current and tree, so they follow the pads' operating windows over process,
temperature and supply at a few µA (IHP: about 19 µA for tree and both generators).

### 3.5 Test modes

mon and feed separate the two pads (S2D measured alone through `analog_bus0/1`; D2S driven alone from them); ext measures
the pads with external `vcm` / `vref`; the reference select plus `dig_in[10]` measures each reference current alone; the
`dig_out` read-back confirms the decoded state before any analog measurement.

## 4. Target specification

All values are **sky130 targets (proposed)**, to be confirmed in pre-layout simulation for the review in the week of
2026-12-28 and in post-layout simulation over PVT. Conditions unless stated: `vdda` = 3.0 … 3.6 V, T = −40 … 125 °C
(commercial 0 … 110 °C is the minimum the block must meet), process corners tt / ss / ff / sf / fs, pad input 0 … 1 V,
D2S load 1 kΩ ∥ ≤ 300 pF or unloaded. "Basis" gives the IHP sg13cmos5l observed interval (simulation; source in
[SOURCES.md](SOURCES.md)) and the margin applied; **no sky130 simulation result is included yet** (column "sky130 sim":
TBD = sky130 pre-layout simulation for the schematic review, ported from the IHP results; see [PORT_PLAN.md](PORT_PLAN.md)). Absolute limits: TBC from the sky130 PDK and pad-library
ratings (the 3.3 V devices are the 5 V-class `g5v0d10v5` devices; exact rated values to be copied from the PDK documentation).

| # | quantity | conditions | min | typ | max | absolute limit | basis (IHP observed, schematic unless noted) | sky130 sim |
|---|---|---|---|---|---|---|---|---|
| 1 | analog supply `vdda` | | 3.0 V | 3.3 V | 3.6 V | TBC (PDK) | rules: 3.3 V analog | – |
| 2 | digital control level | | | 1.8 V | | TBC (PDK) | rules: 1.8 V digital | – |
| 3 | temperature | | −40 °C | 27 °C | 125 °C | | rules: ≥ 0 … 110 °C | – |
| 4 | S2D gain `(outp−outn)/(pad−vref)` incl. mismatch | | 1.94 | 2.00 | 2.06 | | 1.9985 … 1.9993 (PVT); 1.959 … 2.038 (100 mismatch runs); margin ≈ 1 % | TBD |
| 5 | S2D input offset incl. mismatch | tt, 27 °C | −25 mV | 0 | 25 mV | | −17.3 … 18.2 mV (mismatch) | TBD |
| 6 | S2D INL | pad 0 … 1 V | | 0.2 mV | 2 mV | | 0.087 … 1.069 mV | TBD |
| 7 | S2D output common-mode error incl. mismatch | | −50 mV | 10 mV | 50 mV | | 5.0 … 18.1 mV (PVT); −19.0 … 39.9 mV (mismatch) | TBD |
| 8 | S2D input range (`vref` ≈ 0.5 V) | | 0 V | | 1.0 V | pad: TBC (ESD / pad library) | low end ≤ 0.087 V, high end ≥ 1.057 V | TBD |
| 9 | S2D −3 dB bandwidth | | 1 MHz | 1.4 MHz | | | 1.237 … 1.666 MHz (post-layout PEX); 1.353 … 1.812 (schematic) | TBD |
| 10 | S2D settling to 1 % | ≤ 0.5 pF | | 0.4 µs | 1 µs | | 0.222 … 0.596 µs | TBD |
| 11 | S2D input noise density | 100 kHz | | 0.15 µV/√Hz | 0.25 µV/√Hz | | 0.142 … 0.157 µV/√Hz | TBD |
| 12 | S2D PSRR (pad-ring supply), input-referred | 1 kHz | 60 dB | 90 dB | | | 79.1 … 113.4 dB (mismatch runs) | TBD |
| 13 | S2D pad-ring supply current, enabled | default bias | | 116 µA | 135 µA | | 114.6 … 116.9 µA | TBD |
| 14 | D2S gain `(pad−vref)/(vinp−vinn)` incl. mismatch | 3.3 … 3.6 V | 0.49 | 0.50 | 0.51 | | 0.4981 … 0.5000; post-layout 0.4983 … 0.5000; 0.4939 … 0.5085 (mismatch, schematic) | TBD |
| 15 | D2S output offset incl. mismatch | | −20 mV | 0 | 20 mV | | 0.035 … 1.95 mV (PVT); post-layout 0.044 … 1.75 mV; −11.4 … 10.1 mV (mismatch, schematic) | TBD |
| 16 | D2S INL | ±1 V differential, input common mode = vref = vcm (≈ 1.26 V), `vdda` 3.0 … 3.6 V | | 0.5 mV | 10 mV | | at the slot's operating point ≤ 1.38 mV at 3.0 V, ≤ 0.56 mV at 3.3 V, ≤ 0.50 mV at 3.6 V (schematic and post-layout agree within 0.001 mV); the 87 … 88 mV at 3.0 V of the CACE suite are an artefact of its 1.65 V input common mode | TBD |
| 17 | D2S −3 dB bandwidth | 10 … 300 pF | 1 MHz | 2 MHz | | | 1.58 … 3.01 MHz; post-layout 1.43 … 2.71 MHz | TBD |
| 18 | D2S gain peaking | ≤ 300 pF | | 0 dB | 4 dB | | ≤ 2.9 dB; post-layout ≤ 2.5 dB | TBD |
| 19 | D2S slew rate | 10 … 300 pF | 1 V/µs | 2.4 V/µs | | | 1.76 … 3.17 V/µs; post-layout 1.59 … 2.79 V/µs (settling 0.35 … 0.55 µs, overshoot ≤ 8 %) | TBD |
| 20 | D2S THD | 0.5 V output amplitude | | −58 dB | −50 dB | | −73.2 / −57.8 / −38.9 dB at 0.25 / 0.5 / 0.75 V output amplitude (`thd_params.csv`); post-layout −73.2 / −57.7 / −38.7 dB | TBD |
| 21 | D2S output swing | `vdda` 3.3 V | ≤ 0.9 V low | | ≥ 3.0 V high | | 0.64 … 0.74 V / 3.27 … 3.28 V; post-layout 0.64 … 0.74 V / 3.27 … 3.28 V | TBD |
| 22 | D2S short-circuit current | | 20 mA | | | TBC (pad metal / ESD) | 49.7 … 120.3 mA; post-layout 49.7 … 124.2 mA | TBD |
| 23 | D2S output impedance | 1 kHz | | 0.2 Ω | 10 Ω | | 0.195 … 3.85 Ω; post-layout 0.208 … 3.30 Ω | TBD |
| 24 | D2S PSRR (pad-ring supply) | 1 kHz | 60 dB | 71 dB | | | 70.7 … 72.5 dB; post-layout 70.0 … 71.9 dB | TBD |
| 25 | D2S pad-ring quiescent current | | | 300 µA | 400 µA | | 293 … 314 µA; post-layout ring current 302 … 325 µA | TBD |
| 26 | round trip S2D → D2S error | pad 0 … 1 V, systematic | | 1 mV | 10 mV | | 0.90 … 6.49 mV (slot, extracted pads, 5 corners) | TBD |
| 27 | `vcm` (replica) | | 1.10 V | 1.26 V | 1.45 V | | 1.115 … 1.395 V; post-layout (C-coupled PEX) 1.242 … 1.395 V, equal to schematic; mismatch σ 5.4 mV (100 runs) | TBD (the sky130 window follows the sky130 pads) |
| 28 | `vref` (replica) | | 0.40 V | 0.49 V | 0.65 V | | 0.436 … 0.596 V (bias tree reference); 0.376 … 0.668 V with an on-slot core as reference; post-layout 0.436 … 0.596 V, equal to schematic; mismatch σ 3.8 mV (100 runs) | TBD |
| 29 | reference current, Banba (tentative, better than IHP) | sourced into 0.7 V | 4.25 µA | 5.0 µA | 5.75 µA | | IHP 3.83 … 6.37 µA (test platform); `bg_core_pd` alone 3.829 … 6.369 µA (135 PVT points; resistor corners −21 % / +28 %, MOS ≤ 0.31 %, supply ≤ 0.73 %/V) | TBD |
| 30 | reference current, Oguey–Aebischer (tentative, better than IHP) | sourced into 0.7 V | 3.5 µA | 5.0 µA | 6.5 µA | | IHP 3.04 … 7.05 µA (PTAT) | TBD |
| 31 | enable time (block, to 1 %) | | | 2 µs | 5 µs | | S2D 1.36 … 1.52 µs; D2S 0.81 … 1.23 µs (post-layout 1.11 … 2.39 µs); `vcm` 0.79 … 1.81 µs, `vref` 1.03 … 2.02 µs | TBD |
| 32 | 3.3 V block current, enabled | default | | 50 µA | 80 µA | | 48.4 … 49.7 µA | TBD |
| 33 | pad-ring current, enabled (both pads) | | | 390 µA | 500 µA | | 364.6 … 395.6 µA | TBD |
| 34 | supply currents, disabled | `enable` = 0 | | | 1 µA | | block 25 … 56 nA, ring 9 … 58 nA | TBD |
| 35 | pad leakage, block unpowered | pad 0 … 3.3 V, 125 °C | −100 nA | | 100 nA | | S2D ≤ 25 nA, D2S ≤ 67 nA (125 °C); D2S pad leakage, pad off, post-layout −36.9 … +15.0 nA (48 runs) | TBD |

D2S rows: the schematic values come from CACE results committed on 2026-10-21, which predate the final D2S schematic
(changed until 2026-11-03); a re-run of the schematic is in progress. The "post-layout" values are IHP magic-PEX (C-coupled) simulations of the taped-out D2S pad cell made on 2026-11-23
(predecessor repository, branch `chipalooza2-documentation`, `verification/c2_gaps/d2s_pex/`; see [SOURCES.md](SOURCES.md) S9);
unloaded closed-loop bandwidth post-layout 1.57 … 2.02 MHz (schematic 1.78 … 2.25 MHz); D2S output noise post-layout 0.142 … 0.156 µV/√Hz at
100 kHz, 224 µV integrated (schematic 0.143 … 0.156 µV/√Hz, 234 µV). All D2S CACE groups except mismatch have post-layout results (all runs; the simulator option `rshunt` = 1 TΩ was
needed for convergence of the extracted netlist).

Replica and distribution (IHP, 2026-11-23, predecessor repository `verification/c2_gaps/replica_bias/`, SOURCES S10): `pad_ref_rb`
extracted from the taped-out slot GDS matches its schematic in DC to 0.1 mV; `bias_dist_pd` copies 5 µA with +0.49 … +1.56 %
systematic error over 5 corners × −40 / 27 / 125 °C and 0.5 … 2.5 V output, mismatch σ 1.0 … 1.2 % per output; off-state leakage
≤ 145 pA.

Rows 29–30 are tentative specifications of the fallback references, to be reviewed at the final design review. Mismatch and
noise targets assume the same device areas as on IHP; the sky130 mismatch models decide whether that holds (schematic review).

## 5. Outline of a test plan for validation by measurement

Details and expected values: [TEST_PLAN.md](TEST_PLAN.md); instruments: [EQUIPMENT_NEEDED.md](EQUIPMENT_NEEDED.md). Adapted
from the measurement procedures of the IHP test platforms and the IHP slot 7 modes; register-level details TBD until the
harness repository exists.

1. **Power-up and fail-safe.** Harness: select the project, route all `dig_in` to 0, 3.3 V on with `enable` = 0: supply
   currents (row 34), pad leakage (row 35, also with the block's supplies off). `enable` = 1: `dig_out` read-back shows the
   default; supply currents (rows 32, 33).
2. **References** (one at a time, `dig_in[6..7]`, `dig_in[10]`): each current into an SMU at 0.7 V on `pad_aux` (or on
   `analog_bus3`; the bus switches are below 5 Ω, so 5 µA drop below 25 µV): rows 29, 30; supply sensitivity 3.0 / 3.3 / 3.6 V;
   enable / disable time with an oscilloscope on a sense resistor. Harness currents 0 / 1 measured the same way for comparison.
3. **`vcm` / `vref`**: high-impedance voltmeter on `analog_bus2/3` in the default mode, for each reference current (rows 27, 28).
4. **S2D pad alone** (mon): DC sweep of `pad_s2d` 0 … 1 V with a precision source, `outp` / `outn` on `analog_bus0/1` with
   two voltmeters: gain, offset, INL, common-mode error (rows 4–8). AC with ext and small signals for bandwidth: on the buses
   only at low frequency (bus capacitance); bandwidth is measured through the D2S pad in the loop instead (step 6).
5. **D2S pad alone** (feed): drive `analog_bus0/1` from a differential source around `vcm`, measure `pad_d2s`: gain, offset,
   INL, swing, output impedance, short-circuit limit (rows 14–16, 21–25).
6. **Loop** (default and swap): sine and step into `pad_s2d`, observe `pad_d2s` on the dedicated pins (no bus in the path):
   round-trip error, bandwidth, slew rate, settling, THD (rows 9, 10, 17–20, 26); with ext, the same with external `vcm` /
   `vref`.
7. **Noise and PSRR** (default): output spectrum at `pad_d2s` with a low-noise preamplifier; supply ripple injected on `vdda`
   and on the pad ring (rows 11, 12, 24).
8. **Temperature plan:** steps 1–6 at −40, 27, 110 and 125 °C (110 °C is the commercial limit of the rules); step 7 at 27 °C.
9. **Pass guidance:** expected values are the min … max of section 4; first silicon results are compared with the
   post-layout intervals, not treated as guarantees.

What goes where: DC voltages of `vcm`, `vref` and the S2D outputs, and reference currents, on the shared analog lines
(DC only); all signal-bandwidth, slew and distortion measurements on the dedicated pins.

## 6. Port plan (IHP sg13cmos5l → sky130)

Details: [PORT_PLAN.md](PORT_PLAN.md).

| item | IHP sg13cmos5l (taped out) | sky130 (proposed) |
|---|---|---|
| analog devices | `sg13_hv` 3.3 V MOS | `sky130_fd_pr__nfet_g5v0d10v5` / `pfet_g5v0d10v5` (5 V-class, used at 3.3 V) |
| digital domain | 1.2 V harness controls, fail-safe shifters 1.2 → 3.3 V | 1.8 V harness controls; shifters re-sized for 1.8 V inputs; 3.3 V logic from hand-made hv gates or the 3.3 V `sky130_fd_sc_hvl` cells |
| resistors | `rhigh` poly | `sky130_fd_pr__res_xhigh_po` or `res_high_po` (choice by matching and TC, schematic review) |
| bipolar | `pnpMPA` vertical PNP | sky130 vertical PNP (`sky130_fd_pr__pnp_05v5_W3p40L3p40` or the smaller variant) |
| capacitors | hv MOS capacitors (bypass, Miller, load) | MIM capacitors (`cap_mim_m3_1`) or MOS capacitors, by area |
| pads | own cells in IHP pad frame (80 × 180 µm), IHP ESD devices | own cells matching the sky130 foundry pad frame (size, ring pins, abutment), ESD from the sky130 pad library's structures: **needs approval** |
| shared lines | harness transmission gates | sky130 harness switches (< 5 Ω) |
| layout | slot wrapper only (IHP slot 7, 537.15 × 273 µm) | standalone block layout + slot-wrapper layout (both required by the rules) |

## 7. Risks

| risk | effect | mitigation |
|---|---|---|
| custom pads not approved, or ESD of the custom pads not acceptable | no pad test | ask for approval with this proposal; fallback: the same buffers in the core behind foundry analog pads (loses the pad-frame aspect, keeps the circuits) |
| custom pad ESD / latch-up cannot be simulated with open tools | unverified protection | reuse the pad library's ESD structures unchanged; DRC with latch-up rules; document what is not simulated |
| bandgap start-up (on IHP: DC non-convergence at ss / −40 °C in four manual modes; shown on 2026-11-23 to be a simulator artefact: power-up transients settle in all modes, no second stable state of the bandgap found) | stuck reference | start-up check by supply-ramp transient over all corners at the schematic review; harness currents selectable as a bypass |
| model differences (sky130 thresholds, headroom of the 3.3 V devices at 3.0 V) | narrower input and output windows | windows set by replica bias; targets of rows 8, 16, 21 confirmed first |
| area of two pad cells and the references in a slot | does not fit | pads live in the pad frame; references and glue are small on IHP (well under the IHP slot) |
| schedule (pads + references + glue in 13 weeks) | incomplete layout | pads first; references are fallbacks and can be dropped in favour of the harness references |

## 8. Schedule against the reviews

| review / date | content |
|---|---|
| proposal, week of 2026-11-23 | this document; approval request for the custom pads |
| schematic and pre-layout, week of 2026-12-28 | sky130 schematics of both pads, references, replica, glue; pre-layout simulation over PVT against section 4; target table updated with sky130 results |
| layout and post-layout, week of 2027-02-01 | standalone layout; DRC, LVS, PEX; post-layout simulation over PVT; pads verified independently |
| final design, week of 2027-02-22 | slot-wrapper layout and integration; sign-off data in the repository; tentative reference specifications reviewed |
| tapeout 2027-05-19 | – |

## 9. License

Either **Apache-2.0** or the **Solderpad Hardware License v2.1** (an Apache-2.0-based, permissive hardware license),
**pending approval by the Chipalooza organizers**. See [LICENSE_NOTE.md](LICENSE_NOTE.md).

## 10. AI assistance

This IP block is also a proof of concept of AI-assisted analog design: much of the design and nearly all of the
documentation were created with AI assistance, reviewed by the designer. The finished design, its sources, its verification
flows and its documentation do not require AI to use, verify or modify; all verification uses open-source tools. See
[AI_ASSISTANCE.md](AI_ASSISTANCE.md).
