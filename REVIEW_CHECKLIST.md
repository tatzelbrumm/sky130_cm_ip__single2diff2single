# Review checklist for the user (in reading order)

1. `docs/PROPOSAL.md` §1: is the framing right (pads = the proposal, references = test fallback, tentative specs)?
2. §2 pin table: the new `dig_in[6..13]` map, the default reference (Banba = 00), the optional third pin `pad_aux`.
3. §2 exceptions: custom-pad approval request; is "own references are inside the slot, no exception" acceptable to you?
4. §3.4: harness bias voltage as `vcm` or `vref` source only works if its value falls in the window (TBD: harness spec).
5. §4 target table: every value is a **target** chosen from IHP observed intervals with a margin (column "basis"); check margins, in particular rows 4, 5, 7 (mismatch), 16 (D2S INL at 3.0 V left TBD), 20 (THD), 29–30 (reference currents, tighter than IHP, tentative).
6. §4 column "sky130 sim": all TBD until the simulation results arrive.
7. §5 test plan: 110 °C added as a temperature point (commercial limit); OK?
8. §6 port plan, §7 risks: fallback "buffers in the core behind foundry analog pads" if the custom pads are not approved: acceptable?
9. §9 license, §10 AI paragraph: wording.
10. Anonymity: PROPOSAL.md has no names, institutions, personal URLs (checked by grep at each push).

Items needing an organizer's approval: custom pads; license (Apache-2.0 or SHL-2.1).

[S7] branch `chipalooza2-documentation`:
11. `signoff/README.md`: magic LVS property errors (`mm_ok`, antenna-diode W/L) in `bg_core_pd` and pad reports, not mentioned in their READMEs: accept or note?
12. `docs/chipalooza2_as_taped_out/TEST_PLAN.md`: SPI sequence and expected intervals for the chip measurement.
