<!--
SPDX-FileCopyrightText: 2026 Christoph Maier
SPDX-License-Identifier: Apache-2.0
-->
# Sources of the observed (IHP sg13cmos5l) values

Every "IHP observed" number in [PROPOSAL.md](PROPOSAL.md) comes from simulation results committed to the repositories below
(read only). None is a sky130 result and none is a silicon measurement (no silicon data exist at the time of writing).

| ref | what | repository, commit, path |
|---|---|---|
| S1 | S2D pad CACE results (schematic and magic PEX views): gain, offset, INL, CM error, range, bandwidth, settling, noise, PSRR, ring current, enable, power-down | [`tatzelbrumm/sg13cmos5l_cm_ip__single2diff2single`](https://github.com/tatzelbrumm/sg13cmos5l_cm_ip__single2diff2single) `91a7da8b67ac56a26c605501146667a1fde28c32`, `macros/sg13cmos5l_IOPadSingle2Diff/verification/cace/` |
| S2 | D2S pad CACE results (schematic view only; the committed results predate its layout) | same repository, `91a7da8b…`, `macros/sg13cmos5l_IOPadDiff2Single/verification/cace/` |
| S3 | replica bias `pad_ref_rb` CACE results (`vcm`, `vref`, supply current, power-down, mismatch) | same repository, `9052bd35928c6d40344e8e686c9abbe736bfadb9`, `macros/pad_ref_rb/verification/cace/` |
| S4 | slot tier-1 system simulation (round-trip error, slot and ring currents, disabled currents, modes) | same repository, `9052bd35…`, `docs/slot7_hookup/tier1/results.txt`, `modes.txt` |
| S5 | Oguey–Aebischer and Banba core output currents, switching times (test platform stage A, schematic and extracted) | same repository, `efb8014101ba0afad1235859016592bf511b2117`, `docs/slot7_testplatform/` |
| S6 | enable / starvation leakage of the pads (`en_ctrl_3v3` starvation test) | same repository, `9052bd35…`, `macros/en_ctrl_3v3/` (as quoted in the slot 7 documentation) |
| S7 | taped-out slot 7 (GDS, netlists, pads, modes) | [`tatzelbrumm/sg13cmos5l_cm_slot7`](https://github.com/tatzelbrumm/sg13cmos5l_cm_slot7) `158afc5afab0056bd6d216a4db3833e34a364949` |
| S8 | the summaries the intervals were read from: data sheets generated from S1–S4 with an ex post facto specification (observed min / median / max) | [`tatzelbrumm/sg13cmos5l_ocd_chipalooza`](https://github.com/tatzelbrumm/sg13cmos5l_ocd_chipalooza), branch `sudel_buecher`, `sudelbuecher/slots/slot_7/datasheets/` and `test_platforms.md`; the Chipalooza #2 description is also on branch `chipalooza2-documentation` of S7 |
| S9 | D2S pad post-layout (magic PEX) CACE results of the taped-out cell, compared with S2 | [`tatzelbrumm/sg13cmos5l_cm_slot7`](https://github.com/tatzelbrumm/sg13cmos5l_cm_slot7/tree/chipalooza2-documentation/verification/c2_gaps/d2s_pex) branch `chipalooza2-documentation`, `verification/c2_gaps/d2s_pex/` (`results.md`, `run.sh`); made 2026-11-23 |
| S10 | `pad_ref_rb` post-layout (magic C-coupled PEX of the cell cut from the taped-out `slot_7.gds`) vs schematic; 100-run mismatch Monte Carlo with per-run data; `bias_dist_pd` copy accuracy and mismatch | same branch, `verification/c2_gaps/replica_bias/` (`results.md`, `run.sh`); made 2026-11-23 |

Mapping of PROPOSAL.md section 4 rows to sources: rows 4–13 S1; 14–25 S2; 26, 32–34 S4; 27–28 S3, S4 and S10; 29–30 S5;
31 S1, S2, S3; 35 S6.
