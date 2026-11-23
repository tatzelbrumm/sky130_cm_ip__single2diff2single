# Run log, 2026-11-23 (times UTC; CET = UTC+1)

- 19:52 P0. `add_repo` push for `tatzelbrumm/sg13cmos5l_cm_slot7` (clone at `158afc5`) and `tatzelbrumm/sky130_cm_ip__single2diff2single` (empty, pushable). Task file and rules copy read from `sg13cmos5l_ocd_chipalooza` `sudel_buecher`.
- 19:52 sky130A PDK: `claude-cloud-config` `parts/ciel.sh` + `parts/pdk-sky130A.sh` with `CIEL_LIB_OPTS="-l sky130_fd_pr"`; ciel's index and the GitHub API were refused, the third path (direct release downloads, local manifest) worked: `/foss/pdks/sky130A` (open_pdks `1689ac3f`), `sky130_fd_pr` only, 0 dangling links, `PDK_OK`. The IHP PDK stays at `/foss/pdks/ihp-sg13cmos5l`.
- 19:53 Background simulation job started (verification/ of the new repository).
- 19:56 Inputs read: slot 7 `README.md`, `glue_logic.md` (mode decode), `test_platforms.md` (OA / BG currents), data sheets (S2D, D2S, `pad_ref_rb`, `slot_7_system`).
- 19:58 [NEW] `main`: initial commit with README, LICENSE (Apache-2.0 from `/usr/share/common-licenses/Apache-2.0`), `LICENSES/SHL-2.1.txt` (from the slot 7 repository `LICENSE`), `docs/` (PROPOSAL complete in structure, SOURCES, LICENSE_NOTE, AI_ASSISTANCE, EQUIPMENT_NEEDED, PORT_PLAN / TEST_PLAN / RULES_COMPLIANCE as stubs). Pushed.
- 19:59 [SB] worktree `../sky130_cm_ip__single2diff2single_sudelbuecher` on orphan `sudel_buecher` (git 2.43, `worktree add --orphan`).

## Assumptions (no questions to the user during the run)

- The environment default branch `claude/wizardly-brahmagupta-5xnznk` is not used: the user's instructions name `main` and `sudel_buecher` for [NEW] and `chipalooza2-documentation` for [S7].
- PROPOSAL.md contains no personal URLs: the GitHub links (which carry the user name) are in `docs/SOURCES.md` and the README, not in PROPOSAL.md; PROPOSAL.md names commits and paths.
- Reference-select default: 00 = Banba (the reference that was taped out); whether the Oguey–Aebischer core becomes default is left to the schematic review.
- Digital-control map (14 of 24 inputs): taped-out bits `dig_in[0..5]` kept at their positions; new: `[6..7]` reference select, `[8]` / `[9]` harness voltage for `vcm` / `vref`, `[10]` reference-current monitor, `[11..12]` pad bias select, `[13]` read-back enable.
- Third dedicated pin proposed as an optional foundry analog pad for the reference-current monitor.
- Target-table margins chosen by me from the IHP observed intervals (stated per row as basis); the reference-current targets (rows 29, 30) are tighter than IHP, as the user's decision 3 asks, and are tentative.
