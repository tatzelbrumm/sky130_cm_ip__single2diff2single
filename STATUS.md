# Status (22:00 UTC, 2026-11-23)

New repository pushable: yes (no fallback needed).

| item | state |
|---|---|
| P0 setup ([NEW] `main`, [SB] worktree, [S7] branch) | done |
| P1 [NEW] `docs/PROPOSAL.md` + `PROPOSAL.pdf`, `EQUIPMENT_NEEDED.md` | done; submittable. sky130 column TBD by decision; absolute limits TBC from the sky130 PDK |
| P2 [S7] `chipalooza2-documentation` | done: description set, chip TEST_PLAN, signoff/, AI_ASSISTANCE, rules-2 compliance, README section appended |
| P3 [NEW] compliance matrix, test plan, port plan | done (port plan without sky130 results, by decision) |
| P3b sky130 simulations | halted by the user; files stashed on `sudel_buecher` (`stash/`) |
| P3c IHP gap simulations ([S7] `verification/c2_gaps/`) | done: D2S PEX (complete), replica bias PEX + MC, bias distribution, ss / −40 °C verdict, bandgap alone |
| P4 consistency | PROPOSAL.md anonymity checked by grep at every push |

Open (IHP): mode × corner points that still abort in the simulator (tt / sf −40 °C, ss 125 °C swap); `dpantenna` parameters in the converted pad netlists; full-RC PEX; D2S mismatch; whole-slot PEX; no sign-off report for `slot_7.gds` with the art.

Needs the user's decision / action: custom-pad approval request (in the proposal); the control map within 24 inputs; equipment availability list and CVs (sent separately); submission by e-mail to chipalooza@opencircuitdesign.com (Challenge #4 page); license choice (organizers); target margins (REVIEW_CHECKLIST item 5).
