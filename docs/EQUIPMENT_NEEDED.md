<!--
SPDX-FileCopyrightText: 2026 Christoph Maier
SPDX-License-Identifier: Apache-2.0
-->
# Equipment the test plan needs

A list of instrument *types* for [TEST_PLAN.md](TEST_PLAN.md) (no availability, no persons; the list of equipment available
is sent separately from the proposal, as the rules ask).

| instrument | used for (test-plan step) | minimum capability |
|---|---|---|
| harness test board with its SPI / control host | all steps: project select, `dig_in` routing, `analog_ena`, read-back | as provided by the harness |
| source-measure unit, 2 channels | supply currents, disabled and unpowered leakage, reference currents into 0.7 V, D2S short-circuit and output impedance | pA resolution, ±100 mA range |
| precision DC voltage source | S2D DC sweep 0 … 1 V, D2S differential drive around `vcm` (2 channels or 1 + `vcm` tracking) | 0 … 3.3 V, µV resolution |
| digital multimeters, high input impedance, 2 units | `vcm`, `vref`, S2D `outp` / `outn` on the shared lines, INL | 6½ digits, ≥ 10 GΩ input option |
| function generator | sine and step into the S2D pad | ≥ 10 MHz, low distortion (THD < −70 dB at 100 kHz) |
| oscilloscope | step response, slew, settling, enable / disable timing | ≥ 100 MHz, 4 channels |
| audio / dynamic-signal analyzer or 24-bit ADC with FFT | THD, noise spectrum | 10 Hz … 1 MHz |
| low-noise preamplifier | output noise | < 5 nV/√Hz |
| programmable supply with ripple injection (or a bias-T) | PSRR of both supplies | 3.0 … 3.6 V |
| temperature chamber or thermal forcer | temperature plan | −40 … 125 °C |
| loads | D2S load conditions | 1 kΩ, 10 / 100 / 300 pF |
