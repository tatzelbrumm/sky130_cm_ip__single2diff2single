<!--
SPDX-FileCopyrightText: 2026 Christoph Maier
SPDX-License-Identifier: Apache-2.0
-->
# Measurement test plan (sky130 block)

Outline: [PROPOSAL.md section 5](PROPOSAL.md#5-outline-of-a-test-plan-for-validation-by-measurement). Expected values are
the target intervals of [PROPOSAL.md section 4](PROPOSAL.md#4-target-specification) until sky130 simulation results replace
them. Register addresses of the sky130 harness: TBD (harness repository not available yet). Instruments:
[EQUIPMENT_NEEDED.md](EQUIPMENT_NEEDED.md).

Detailed procedures per step (TBD, to be adapted from the IHP test-platform procedure, `docs/slot7_testplatform/PLAN.md` §5
of the IHP design repository at `efb80141`, and from the IHP slot 7 mode procedure):

1. Power-up and fail-safe: TBD
2. References: TBD
3. `vcm` / `vref`: TBD
4. S2D pad alone (mon): TBD
5. D2S pad alone (feed): TBD
6. Loop (default, swap, ext): TBD
7. Noise and PSRR: TBD
8. Temperature plan: −40, 27, 110, 125 °C
