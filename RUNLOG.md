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

- 19:58 Live rules pages read (`rules-4`, `challenge-4`, `challenge-1`, `rules-2`, all HTTP 200). rules-4 live text = the copy of 2026-11-23 apart from line breaks around links. `challenge-4.html` names the submission channel: "send your proposal to chipalooza@opencircuitdesign.com". `challenge-1.html`: no analog pad buffer or S2D / D2S block in the Challenge #1 list (gap note added to PROPOSAL §1).
- 19:58 Template `simi1505/sg13cmos5l_chipalooza_analog_project` read at `c72f665b` (directory layout, Makefile targets) for the compliance matrix.
- 19:59 [S7] branch `chipalooza2-documentation` created from `158afc5` (local); P2 content being written by a background job, committed by me after review.
- 20:00 [NEW] `docs/RULES_COMPLIANCE.md` (35 rows + template comparison), `docs/TEST_PLAN.md` (detailed), `.gitignore`; pushed. `docs/PROPOSAL.pdf` rendered by `scripts/render_proposal_pdf.sh` (pandoc 3.1.3 → HTML → Playwright Chromium PDF; no LaTeX engine installed), 9 pages A4.
- 20:10 [S7] `chipalooza2-documentation` pushed (`9d3e441`, from `158afc5`): `docs/chipalooza2_as_taped_out/` (slot 7 set from `sg13cmos5l_ocd_chipalooza` `sudel_buecher` `sudelbuecher/slots/slot_7/`, links adapted, "this session" → "on 2026-11-22", `oa_core_pd` statement at the top), `TEST_PLAN.md` (fabricated chip), `signoff/` (14 reports copied byte-identical from the design repository at `9052bd35` / `91a7da8b`, sha256 in `signoff/README.md`; largest 1.2 MB KLayout lvsdb), `docs/AI_ASSISTANCE.md`, `docs/RULES_COMPLIANCE_chipalooza2.md`; `README.md` only appended. `final/ pads/ netlist/ art/ macros/` unchanged (empty diff).
- Source conflicts found while writing [S7] (recorded, not "fixed"):
  1. delivery README says both cores are in `slot_7.gds`; the taped-out GDS has no `oa_core_pd` / `oa_*` cell.
  2. `tapeout_nov_2026` tip gitlink `c072679` (stage B) vs `config.txt` and tapeout commit `7eeb3cb`: `158afc5`.
  3. `en_ctrl_3v3` README says CACE suite v2; its file list says "v1 suite … to be rewritten for v2".
  4. magic / netgen LVS reports of `bg_core_pd` and both pads contain property errors (`mm_ok`; W/L swapped on antenna diodes) that the READMEs do not mention.
  5. floating `vdd_3v3`: PLAN.md 0.6–0.67 V vs SUMMARY data 0.5–0.665 V.
  6. FOR_TIM: `0x0D` / `0x0E` are route codes written into `0x20…0x37`, not register addresses (checked against the harness RTL).
  7. delivery README: harness flow "not yet run"; design-repository RUNLOG row 129: passed for v2 on the fork with four patches.
- No sign-off report exists for the taped-out `final/gds/slot_7.gds` with the art; `slot_7_checks.txt` covers v3 without the art. No DRC / LVS reports committed for `pad_ref_rb` or `bias_dist_pd` at the cited commits.
- 20:40 User instruction: halt all sky130 simulations, stash the files, simulate what is missing on IHP instead. Both sky130 jobs stopped; their files removed from [NEW] `main` and kept on `sudel_buecher` under `stash/sky130_sims_halted_2026-11-23/` (sources and partial plots only, 1.1 MB). [NEW] docs updated: no sky130 simulation in the proposal; sky130 numbers TBD until the schematic review.
