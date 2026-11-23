<!--
SPDX-FileCopyrightText: 2026 Christoph Maier
SPDX-License-Identifier: Apache-2.0
-->
# S2D core amplifier, sky130 port: results

**sky130 pre-layout schematic simulation (feasibility, not sign-off).**

Tools: ngspice-47; PDK sky130A (open_pdks 1689ac3f2dc763876eaf967227c7dfe831b031ae), sky130_fd_pr g5v0d10v5 devices, xhigh_po resistors, MIM capacitors. Decks: `verification/pads/decks/`, reduced by `scripts/analyze.py`.

Conditions: ideal 5 uA iref, vref = 0.49 V (ideal source), pad swept 0 .. 1 V (10 mV steps), 0.5 pF external load per output plus the built-in 16 x 16 um MIM. No ESD, no pad, no layout, no mismatch (systematic offset only).

## vcm window (where the port works)

Pass = |gain - 2| <= 1 % and INL <= 2 mV (IHP's proposed DC limits). vcm swept 0.80 .. 1.40 V in 50 mV steps (and 1.26 V).

| corner | T (C) | vdd (V) | vcm min (V) | vcm max (V) |
|---|---:|---:|---:|---:|
| ff | -40 | 3 | 0.85 | 1.25 |
| ff | -40 | 3.3 | 0.85 | 1.40 |
| ff | -40 | 3.6 | 0.85 | 1.40 |
| ff | 27 | 3 | 0.90 | 1.35 |
| ff | 27 | 3.3 | 0.90 | 1.40 |
| ff | 27 | 3.6 | 0.90 | 1.40 |
| ff | 125 | 3 | 1.00 | 1.40 |
| ff | 125 | 3.3 | 1.00 | 1.40 |
| ff | 125 | 3.6 | 1.00 | 1.40 |
| fs | -40 | 3 | 0.90 | 1.26 |
| fs | -40 | 3.3 | 0.90 | 1.40 |
| fs | -40 | 3.6 | 0.90 | 1.40 |
| fs | 27 | 3 | 0.95 | 1.40 |
| fs | 27 | 3.3 | 0.95 | 1.40 |
| fs | 27 | 3.6 | 0.95 | 1.40 |
| fs | 125 | 3 | 1.00 | 1.40 |
| fs | 125 | 3.3 | 1.00 | 1.40 |
| fs | 125 | 3.6 | 1.00 | 1.40 |
| sf | -40 | 3 | 0.85 | 1.10 |
| sf | -40 | 3.3 | 0.85 | 1.40 |
| sf | -40 | 3.6 | 0.85 | 1.40 |
| sf | 27 | 3 | 0.90 | 1.20 |
| sf | 27 | 3.3 | 0.90 | 1.40 |
| sf | 27 | 3.6 | 0.90 | 1.40 |
| sf | 125 | 3 | 1.00 | 1.40 |
| sf | 125 | 3.3 | 1.00 | 1.40 |
| sf | 125 | 3.6 | 1.00 | 1.40 |
| ss | -40 | 3 | 0.90 | 1.10 |
| ss | -40 | 3.3 | 0.90 | 1.40 |
| ss | -40 | 3.6 | 0.90 | 1.40 |
| ss | 27 | 3 | 0.95 | 1.25 |
| ss | 27 | 3.3 | 0.95 | 1.40 |
| ss | 27 | 3.6 | 0.95 | 1.40 |
| ss | 125 | 3 | 1.00 | 1.40 |
| ss | 125 | 3.3 | 1.00 | 1.40 |
| ss | 125 | 3.6 | 1.00 | 1.40 |
| tt | -40 | 3 | 0.90 | 1.15 |
| tt | -40 | 3.3 | 0.90 | 1.40 |
| tt | -40 | 3.6 | 0.90 | 1.40 |
| tt | 27 | 3 | 0.95 | 1.30 |
| tt | 27 | 3.3 | 0.95 | 1.40 |
| tt | 27 | 3.6 | 0.95 | 1.40 |
| tt | 125 | 3 | 1.00 | 1.40 |
| tt | 125 | 3.3 | 1.00 | 1.40 |
| tt | 125 | 3.6 | 1.00 | 1.40 |

**Common window over all 5 corners x (-40, 27, 125 C) x (3.0, 3.3, 3.6 V): vcm = 1.00 .. 1.10 V.** The IHP value vcm = 1.26 V is outside it. Port value used below: vcm = 1.05 V.

- vdd = 3 V only: vcm = 1.00 .. 1.10 V (all corners, -40 .. 125 C)
- vdd = 3.3 V only: vcm = 1.00 .. 1.40 V (all corners, -40 .. 125 C)
- vdd = 3.6 V only: vcm = 1.00 .. 1.40 V (all corners, -40 .. 125 C)

Why: the units are PMOS pairs whose gates see up to vcm + 0.51 V (feedback and CMFB units on the outputs). The sky130 g5v0d10v5 pfet needs about 0.3 .. 0.4 V more Vsg than IHP's hv pmos (1.10 V at 5 uA, W/L 20/1, tt 27 C; 1.27 V at ss -40 C), so the upper end of the window drops; the lower end is set by the outputs (vcm - 0.51 V) against the NMOS fold sinks and cascodes.

## DC at vcm = 1.05 V

| corner | T (C) | vdd (V) | gain | offset (mV, in) | INL (mV, in) | CM err at pad = vref (mV) | max abs CM err (mV) | I(vdd) (uA) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| ff | 125 | 3 | 1.99830 | -0.016 | 0.296 | 5.04 | 15.51 | 124.5 |
| ff | 125 | 3.3 | 1.99868 | -0.014 | 0.325 | 5.87 | 16.08 | 126.1 |
| ff | 125 | 3.6 | 1.99868 | -0.008 | 0.347 | 6.56 | 16.52 | 127.7 |
| ss | -40 | 3 | 1.99235 | 0.034 | 0.476 | 0.98 | 13.68 | 120.1 |
| ss | -40 | 3.3 | 1.99708 | -0.027 | 0.214 | 2.54 | 14.42 | 122.1 |
| ss | -40 | 3.6 | 1.99847 | -0.050 | 0.265 | 3.79 | 15.62 | 124.0 |
| tt | 27 | 3 | 1.99721 | -0.039 | 0.308 | 3.85 | 14.78 | 122.0 |
| tt | 27 | 3.3 | 1.99887 | -0.059 | 0.360 | 5.01 | 15.93 | 123.8 |
| tt | 27 | 3.6 | 1.99942 | -0.065 | 0.337 | 5.96 | 16.68 | 125.6 |

Rows: the three requested PVT points (tt 27 C, ss -40 C, ff 125 C) x 3 supplies; all 45 points are in `s2d_dc_all.csv`.

### min / typ / max

| quantity | min | typ (tt 27 C 3.3 V) | max | over |
|---|---:|---:|---:|---|
| gain | 1.99235 | 1.99887 | 1.99942 | 3 PVT x 3 vdd |
| gain | 1.99087 | 1.99887 | 1.99958 | 5 corners x 3 T x 3 vdd |
| offset, input-referred (mV) | -0.065 | -0.059 | 0.034 | 3 PVT x 3 vdd |
| offset, input-referred (mV) | -0.072 | -0.059 | 0.039 | 5 corners x 3 T x 3 vdd |
| INL, input-referred (mV) | 0.214 | 0.360 | 0.476 | 3 PVT x 3 vdd |
| INL, input-referred (mV) | 0.137 | 0.360 | 0.736 | 5 corners x 3 T x 3 vdd |
| CM error at pad = vref (mV) | 0.98 | 5.01 | 6.56 | 3 PVT x 3 vdd |
| CM error at pad = vref (mV) | 0.44 | 5.01 | 11.95 | 5 corners x 3 T x 3 vdd |
| max abs CM error over sweep (mV) | 13.68 | 15.93 | 16.68 | 3 PVT x 3 vdd |
| max abs CM error over sweep (mV) | 10.26 | 15.93 | 24.60 | 5 corners x 3 T x 3 vdd |
| I(vdd) incl. 5 uA iref (uA) | 120.1 | 123.8 | 127.7 | 3 PVT x 3 vdd |
| I(vdd) incl. 5 uA iref (uA) | 119.8 | 123.8 | 127.7 | 5 corners x 3 T x 3 vdd |

### Same at the IHP value vcm = 1.26 V (for comparison)

| corner | T (C) | vdd (V) | gain | INL (mV, in) | CM err (mV) |
|---|---:|---:|---:|---:|---:|
| ff | 125 | 3 | 2.00015 | 0.587 | 4.93 |
| ff | 125 | 3.3 | 2.00130 | 0.528 | 5.76 |
| ff | 125 | 3.6 | 2.00152 | 0.447 | 6.45 |
| ss | -40 | 3 | 1.95000 | 13.711 | 0.90 |
| ss | -40 | 3.3 | 1.99556 | 0.153 | 2.46 |
| ss | -40 | 3.6 | 1.99887 | 0.358 | 3.70 |
| tt | 27 | 3 | 1.99413 | 0.604 | 3.76 |
| tt | 27 | 3.3 | 1.99971 | 0.515 | 4.92 |
| tt | 27 | 3.6 | 2.00099 | 0.509 | 5.86 |

## Closed-loop AC at vcm = 1.05 V, pad = vref

Differential: pad -> outp - outn (ideal 2). Common mode: vcm -> (outp + outn)/2 (ideal 1; shows the CMFB loop).

| corner | T (C) | vdd (V) | gain at 100 Hz | -3 dB BW (MHz) | peaking (dB) | CM BW (MHz) | CM peaking (dB) | I(vdd) op (uA) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| ff | 125 | 3 | 1.9977 | 1.869 | 0.000 | 2.182 | 0.000 | 124.5 |
| ff | 125 | 3.3 | 1.9982 | 1.872 | 0.000 | 2.188 | 0.000 | 126.1 |
| ff | 125 | 3.6 | 1.9984 | 1.876 | 0.000 | 2.193 | 0.000 | 127.7 |
| ss | -40 | 3 | 1.9936 | 1.609 | 0.000 | 1.788 | 0.000 | 120.1 |
| ss | -40 | 3.3 | 1.9967 | 1.608 | 0.000 | 1.788 | 0.000 | 122.1 |
| ss | -40 | 3.6 | 1.9980 | 1.609 | 0.000 | 1.789 | 0.000 | 124.0 |
| tt | 27 | 3 | 1.9967 | 1.730 | 0.000 | 1.964 | 0.000 | 122.0 |
| tt | 27 | 3.3 | 1.9982 | 1.731 | 0.000 | 1.967 | 0.000 | 123.8 |
| tt | 27 | 3.6 | 1.9988 | 1.734 | 0.000 | 1.971 | 0.000 | 125.6 |

| quantity | min | max | over |
|---|---:|---:|---|
| -3 dB BW (MHz) | 1.608 | 1.876 | 3 PVT x 3 vdd |
| -3 dB BW (MHz) | 1.589 | 1.890 | 5 corners x 3 T x 3 vdd |
| peaking (dB) | 0.000 | 0.000 | 3 PVT x 3 vdd |
| peaking (dB) | 0.000 | 0.000 | 5 corners x 3 T x 3 vdd |
| CM BW (MHz) | 1.788 | 2.193 | 3 PVT x 3 vdd |
| CM BW (MHz) | 1.770 | 2.208 | 5 corners x 3 T x 3 vdd |
| CM peaking (dB) | 0.000 | 0.000 | 3 PVT x 3 vdd |
| CM peaking (dB) | 0.000 | 0.000 | 5 corners x 3 T x 3 vdd |

## IHP sg13cmos5l schematic results (for comparison only, not sky130)

Gain 1.9985 .. 1.9993, INL <= 1.07 mV over 0 .. 1 V, CM error 5 .. 18 mV, BW 1.35 .. 1.81 MHz, ring current about 115 uA.

