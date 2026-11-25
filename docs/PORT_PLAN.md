<!--
SPDX-FileCopyrightText: 2026 Christoph Maier
SPDX-License-Identifier: Apache-2.0
-->
# Port plan: IHP sg13cmos5l slot 7 → sky130

Summary table: [PROPOSAL.md section 6](PROPOSAL.md#6-port-plan-ihp-sg13cmos5l--sky130). This page adds the per-block plan and
the sky130 feasibility results.

## 1. Per block

| block (IHP name) | in taped-out IHP slot 7 | port to sky130 | first check |
|---|---|---|---|
| S2D pad `sg13cmos5l_IOPadSingle2Diff` (DDA `s2d_mpdda`, own bias tree, ESD) | yes | core amplifier with `g5v0d10v5` devices, re-sized for the sky130 thresholds; ESD from the sky130 pad library inside a cell of foundry-pad size | gain, input window 0 … 1 V at `vdda` 3.0 V, CM error |
| D2S pad `sg13cmos5l_IOPadDiff2Single` (class-AB, output devices in the clamp frame) | yes | class-AB driver with `g5v0d10v5`; output devices integrated with the pad library's clamp structure (approval) | swing and INL at 3.0 V at the operating input common mode (IHP: INL ≤ 1.4 mV at vicm 1.26 V, but 88 mV at 1.65 V) |
| `bg_core_pd` (Banba, `pnpMPA`, `rhigh`) | yes | sky130 vertical PNP, `res_xhigh_po` / `res_high_po`, start-up | current over PVT, start-up transient |
| `oa_core_pd` (Oguey–Aebischer) | no (IHP test platforms only) | MOS-only, `g5v0d10v5` | current over PVT |
| `bias_dist_pd`, bias trees | yes | same topology; 4-way reference select (new) | switch truth table |
| `pad_ref_rb` (replica `vcm`, `vref`) | yes | replicas of the sky130 pad devices; must be ported together with the pads | `vcm` / `vref` windows vs. the sky130 pad windows |
| `s7_ctrl`, fail-safe shifters `ls_up_fs` | yes | 1.8 V inputs; 3.3 V logic from hv gates or `sky130_fd_sc_hvl`; added selects and read-back (new) | truth table, fail-safe with 3.3 V only |
| `s7_doutpd` | yes | 1.8 V pull-downs / read-back level-down shifters (new) | – |

## 2. sky130 simulations

None in this proposal (decision of 2026-11-23): the basis of the proposal is the IHP sg13cmos5l characterization of the
taped-out design, completed where it had gaps (see [SOURCES.md](SOURCES.md)). The sky130 schematics and their pre-layout
simulation over PVT are the work of the schematic review (week of 2026-12-28); they port the IHP circuits and test benches
and replace the TBD column of [PROPOSAL.md §4](PROPOSAL.md#4-target-specification).
