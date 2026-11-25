# Review checklist for the user (in reading order)

1. `docs/PROPOSAL.md` §1: is the framing right (pads = the proposal, references = test fallback, tentative specs)?
2. §2 pin table: the new `dig_in[6..13]` map, the default reference (Banba = 00), the optional third pin `pad_aux`.
3. §2 exceptions: custom-pad approval request; is "own references are inside the slot, no exception" acceptable to you?
4. §3.4: harness bias voltage as `vcm` or `vref` source only works if its value falls in the window (TBD: harness spec).
5. §4 target table: every value is a **target** chosen from IHP observed intervals with a margin (column "basis"); check margins, in particular rows 4, 5, 7 (mismatch), 16 (D2S INL: now at the slot operating point, ≤ 1.38 mV at 3.0 V; condition changed from 3.3 … 3.6 V to 3.0 … 3.6 V), 20 (THD), 29–30 (reference currents, tighter than IHP, tentative).
6. §4 column "sky130 sim": all TBD by decision. The "basis" column now includes the IHP gap simulations of today (D2S post-layout rows 14–25, 31, 35; `vcm` / `vref` rows 27–28 with PEX and mismatch; bandgap row 29; notes under the table). Check that every target still has margin: closest are row 20 (D2S THD at 0.5 V: post-layout −57.7 dB vs target max −50 dB) and row 16 (D2S INL ≤ 1.38 mV vs 10 mV at the operating point).
7. §5 test plan: 110 °C added as a temperature point (commercial limit); OK?
8. §7 risks: bandgap start-up row rewritten (ss / −40 °C stall shown to be a simulator artefact). §6 port plan, fallback "buffers in the core behind foundry analog pads" if the custom pads are not approved: acceptable?
9. §9 license, §10 AI paragraph: wording.
10. Anonymity: PROPOSAL.md has no names, institutions, personal URLs (checked by grep at each push).

Items needing an organizer's approval: custom pads; license (Apache-2.0 or SHL-2.1).

[S7] branch `chipalooza2-documentation`:
11. `signoff/README.md`: magic LVS property errors (`mm_ok`, antenna-diode W/L) in `bg_core_pd` and pad reports, not mentioned in their READMEs: accept or note?
12. `docs/chipalooza2_as_taped_out/TEST_PLAN.md`: SPI sequence and expected intervals for the chip measurement.
13. **Proposal row 14 (D2S gain incl. mismatch, target 0.49 … 0.51):** the re-run on the taped-out schematic gives mismatch samples 0.4888 … 0.5051 (σ 0.0037, 30 runs); one sample is below 0.49. Decide: widen the target (e.g. 0.485 … 0.515 ≈ ±3σ plus systematic) or keep it and note the IHP basis violates it.
