<!--
SPDX-FileCopyrightText: 2026 Christoph Maier
SPDX-License-Identifier: Apache-2.0
-->
# Measurement test plan (sky130 block)

Outline: [PROPOSAL.md §5](PROPOSAL.md#5-outline-of-a-test-plan-for-validation-by-measurement). **Expected values** are the
target intervals of [PROPOSAL.md §4](PROPOSAL.md#4-target-specification) ("row n" below) until sky130 pre-layout and
post-layout results replace them; they are intervals to compare against, not guarantees. Register addresses of the sky130
harness are TBD (harness repository not published yet); the sequence below names harness *functions*, modelled on the
Chipalooza #2 harness procedure used for the IHP predecessor (select the project; route all digital inputs to constant 0
first; then set individual bits; enable the analog-bus switches in use). Instruments: [EQUIPMENT_NEEDED.md](EQUIPMENT_NEEDED.md).
Pin and control names: [PROPOSAL.md §2](PROPOSAL.md#2-list-of-io-including-test-ports).

Origin: adapted from the IHP test-platform procedure (`docs/slot7_testplatform/PLAN.md` §5 of the IHP design repository at
`efb80141`; supply-current subtraction, enable / disable timing, fail-safe states, bus-current measurement into an SMU at
0.7 V) and from the IHP slot 7 modes (key `dig_in[3]` = 1, `dig_in[4]` = 0; swap, mon, feed, ext). See
[SOURCES.md](SOURCES.md).

## 0. Set-up and conventions

- Every step starts from the **safe state**: project selected, all `dig_in` routed to constant 0, `enable` = 0, analog-bus
  switches open, SMUs on the buses at 0 V or open.
- Leakage baseline `I_leak` (3.3 V supply current with `enable` = 0) is taken at every temperature and subtracted from
  enabled currents (leakage grows with temperature).
- Before switching `vdda` off: bus switches open and bus sources at 0 V (on IHP a voltage on a bus drove the switch PMOS into a
  floating 3.3 V rail).
- Read-back: after every control change, `dig_out[0..7]` must show the decoded state (`en`, loop direct, loop crossed,
  S2D → bus, bus → D2S, replica connected, reference select); a mismatch stops the step.

## 1. Power-up, enable, fail-safe

| # | action | measure | expected |
|---|---|---|---|
| 1.1 | `vdda` on, `enable` = 0 | `vdda` current, pad-ring current | row 34 (≤ 1 µA) |
| 1.2 | block unpowered (`vdda` off, pad ring on), `pad_s2d` and `pad_d2s` swept 0 … 3.3 V with the SMU | pad current | row 35 (±100 nA at 125 °C) |
| 1.3 | `enable` = 1, all `dig_in` = 0 | read-back = default; `vdda` and pad-ring currents | rows 32, 33 |
| 1.4 | `enable` 0 → 1 → 0, oscilloscope on `vcm` (`analog_bus2`, high-impedance probe) and on `pad_d2s` | enable time to 1 %, disable | row 31 |
| 1.5 | `enable` = 1 with `vccd` (1.8 V) off | block works (3.3 V only); read-back invalid by design | as 1.3 |

## 2. References (one at a time)

`dig_in[3]` = 1 (key), `dig_in[6..7]` = 00 / 01 / 10 / 11, `dig_in[10]` = 1 (reference current to `pad_aux`, or to
`analog_bus3` if no third pin is granted). SMU at 0.7 V sinks the current.

| # | measure | conditions | expected |
|---|---|---|---|
| 2.1 | Banba output current | `vdda` 3.0 / 3.3 / 3.6 V | row 29 |
| 2.2 | Oguey–Aebischer output current | same | row 30 |
| 2.3 | harness current 0 and 1, through the same path | same | harness specification |
| 2.4 | compliance: SMU voltage 0.2 … 2.0 V | 3.3 V | change < 1 % (target; IHP test platform: < 0.02 % over 0 … 2.0 V) |
| 2.5 | enable / disable time of each core (sense resistor + oscilloscope) | 27 °C | ≤ 5 µs (row 31) |

Bus path: the shared-line switches are below 5 Ω (rules), so 5 µA drops less than 25 µV across them; the bus measurement
is valid for DC. (A sky130 pre-layout dry run of this path is in [../verification/](../verification/) when available.)

## 3. `vcm` and `vref`

Default mode (no key): `vcm` on `analog_bus2`, `vref` on `analog_bus3`; high-impedance voltmeter (≥ 10 GΩ).
For each reference select (key on, `dig_in[6..7]`): rows 27, 28. With `dig_in[8]` / `dig_in[9]` = 1: the harness voltage
appears in place of `vcm` / `vref` (expected: the harness voltage, within the voltmeter accuracy).

## 4. S2D pad alone (mon: key, `dig_in[1]` = 1)

DC sweep of `pad_s2d` 0 … 1.0 V in 10 mV steps; voltmeters on `analog_bus0` (`outp`) and `analog_bus1` (`outn`); `vref` read
on `analog_bus3` (default) or forced (ext, `dig_in[5]` = 1, `vref` from `analog_bus3`, `vcm` from `analog_bus2`).
Fit `outp − outn` against `pad − vref`: gain (row 4), offset (row 5), INL as the largest deviation from the fit (row 6);
`(outp + outn)/2 − vcm` (row 7); input range where INL stays within row 6 (row 8). The loop stays on in mon mode; the bus
switches load the S2D outputs (on IHP the loop was 10–30× slower with them closed), so this step is DC only.

## 5. D2S pad alone (feed: key, `dig_in[2]` = 1)

Drive `analog_bus0/1` with a differential voltage around `vcm` (± 1 V differential in 20 mV steps); measure `pad_d2s` with
a voltmeter, unloaded and with 1 kΩ: gain (row 14), offset (row 15), INL (row 16), swing (row 21); output impedance from the
loaded / unloaded difference (row 23); short-circuit current into the SMU at 0 V and 3.3 V, briefly (row 22); quiescent
pad-ring current (row 25).

## 6. Loop (default; swap: key, `dig_in[0]` = 1; ext: key, `dig_in[5]` = 1)

Signal into `pad_s2d`, observed at `pad_d2s` on dedicated pins only (no bus in the signal path).

| # | stimulus | measure | expected |
|---|---|---|---|
| 6.1 | DC 0 … 1 V | `pad_d2s − (vcm + pad_s2d − vref)`; swap: `pad_d2s − (vcm − (pad_s2d − vref))` | row 26 |
| 6.2 | small sine, swept 1 kHz … 10 MHz | −3 dB bandwidth of the loop (lower of rows 9 and 17) | ≥ 1 MHz |
| 6.3 | 0.5 V step, 10 / 100 / 300 pF on `pad_d2s` | slew rate, settling to 1 %, overshoot / peaking | rows 10, 18, 19 |
| 6.4 | 1 kHz sine, 0.5 V amplitude at the D2S output | THD | row 20 |
| 6.5 | ext: `vcm` / `vref` forced from `analog_bus2/3` | 6.1 again | row 26 |

## 7. Noise and PSRR

Default mode, `pad_s2d` at `vref` + 0.5 V from a low-noise source: output noise spectrum at `pad_d2s` through a low-noise
preamplifier, 10 Hz … 1 MHz (row 11; the D2S output noise has no target row yet: IHP observed 0.143 … 0.156 µV/√Hz at 100 kHz, D2S data sheet, see SOURCES.md S2); 100 mV ripple at 1 kHz on `vdda` and on the pad-ring supply,
output ripple at `pad_d2s` (rows 12, 24).

## 8. Temperature plan

Steps 1–6 at −40, 27, 110 and 125 °C (110 °C is the commercial limit named in the rules); step 7 at 27 °C. At each
temperature repeat the leakage baseline (step 0).

## 9. Evaluation

Each result is reported against the interval of its row: *inside* or *outside the simulated / target interval*, with the
measured value; the first silicon results are compared with the post-layout intervals and published with plots.
