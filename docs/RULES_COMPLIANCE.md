<!--
SPDX-FileCopyrightText: 2026 Christoph Maier
SPDX-License-Identifier: Apache-2.0
-->
# Rules compliance matrix (Chipalooza Challenge #4)

Rules page: https://opencircuitdesign.com/chipalooza/rules-4.html, read on 2026-11-23 (the live text equals the copy of the
same day apart from line breaks). One row per rule or requirement, in the order of the page. State at the proposal stage:
most design-stage rules are **gap** today by nature (no sky130 schematic or layout yet); the action column says how and when
each is closed.

Status values: **met** / **partly** / **gap** / **n/a** / **needs user decision**.

| # | rule (short) | status | evidence | action / when |
|---|---|---|---|---|
| 1 | design conforms to all Sky130 requirements (DRC, voltage limits) | gap | [PORT_PLAN.md](PORT_PLAN.md) (device choice: 5 V-class devices used at 3.3 V) | DRC (magic, KLayout) and device-voltage checks from the schematic review on |
| 2 | proposal due 2026-11-23 | met (if submitted today) | [PROPOSAL.md](PROPOSAL.md) | submit by e-mail to chipalooza@opencircuitdesign.com (address from the Challenge #4 page) |
| 3 | proposal item: type of IP block | met | PROPOSAL.md §1 | – |
| 4 | proposal item: list of I/O incl. test ports | met (harness register names TBD) | PROPOSAL.md §2 | map to the harness pin names when the harness repository is published |
| 5 | proposal item: functional description | met | PROPOSAL.md §3 | – |
| 6 | proposal item: target specification with average, min, max, absolute limits | partly | PROPOSAL.md §4 (35 rows; absolute limits TBC from PDK; sky130 simulation column TBD) | fill absolute limits from the sky130 PDK / pad-library ratings; replace TBD with sky130 pre-layout results ([../verification/](../verification/)) |
| 7 | proposal item: test-plan outline | met | PROPOSAL.md §5, [TEST_PLAN.md](TEST_PLAN.md) | detailed register sequences when the harness exists |
| 8 | list of equipment available (sent separately) | needs user decision | [EQUIPMENT_NEEDED.md](EQUIPMENT_NEEDED.md) lists what is *needed*; availability is not in the repository | the user sends the availability list separately |
| 9 | CVs (sent separately) | needs user decision | – (no personal data in the repository) | the user sends CVs separately |
| 10 | personal and institutional details left out of the main proposal | met | PROPOSAL.md (no names, institutions, e-mail, personal URLs; checked by `grep` at every push) | keep at every edit |
| 11 | block useful in an SoC; fill gaps of the Challenge #1 list | met | PROPOSAL.md §1 (the Challenge #1 list has no analog pad buffers or single-ended / differential converters) | – |
| 12 | uses only the resource list; exceptions approved | needs approval | PROPOSAL.md §2 (custom pads; everything else within the list) | approval request for the custom pads with the proposal |
| 13 | meets the target specification in post-layout verification; spec changes approved | gap | – | post-layout simulation over PVT for the review of 2027-02-01 |
| 14 | analog design for 3.3 V; 1.8 V designs need overvoltage protection at the pads | met (by design choice) | PROPOSAL.md §2, §6 (3.3 V analog; 1.8 V only for controls and read-back) | – |
| 15 | public git repository with everything to reproduce, verify and use the block | partly | this repository (public); sky130 design sources do not exist yet | add schematics, layouts, netlists, decks per the template layout as they are made |
| 16 | verifiable with open-source tools; AI not required to use, verify, modify | met for the IHP basis | IHP characterization with ngspice / CACE / KLayout / magic / netgen ([SOURCES.md](SOURCES.md)); [AI_ASSISTANCE.md](AI_ASSISTANCE.md) | keep all sky130 flows script-driven (Makefile) |
| 17 | all sources to generate all views; modifiable with open-source tools | gap | – | xschem schematics, layout scripts / GDS, CACE files committed with each block |
| 18 | full behavioural description documented in the repository | partly | PROPOSAL.md §3; IHP predecessor documentation | per-block READMEs and data sheets at the schematic review |
| 19 | no unnecessary data dumps; sign-off data (final DRC and LVS) required | gap (no layout yet) | `.gitignore` keeps raw simulation output out | DRC / LVS reports in `verification/drc`, `verification/lvs` as in the template |
| 20 | simulation results as plots, raw data reproducible on demand | gap (sky130); IHP basis summarized as plots / tables in the predecessor documentation | [SOURCES.md](SOURCES.md) | – |
| 21 | standard open-source license, preferably Apache-2.0 | needs organizers' decision | `LICENSE` (Apache-2.0), `LICENSES/SHL-2.1.txt`, [LICENSE_NOTE.md](LICENSE_NOTE.md) | organizers approve Apache-2.0 or SHL-2.1 |
| 22 | no sources violating their license or Apache-2.0 | met | LICENSE_NOTE.md (sky130 PDK Apache-2.0; no third-party design sources) | – |
| 23 | follow the repository template; sign-off scripts runnable by anyone | gap | template compared below | adopt the layout below at the schematic review; Makefile targets for DRC / LVS / PEX / CACE |
| 24 | design environment free; IIC-OSIC-TOOLS encouraged | met | tool versions pinned to IIC-OSIC-TOOLS 2026.10 (IHP basis) | – |
| 25 | post-layout verification over PVT, commercial spec (≥ 110 °C) | gap (planned wider) | PROPOSAL.md §4 (−40 … 125 °C, 3.0 … 3.6 V, 5 corners) | post-layout CACE over PVT |
| 26 | layout restricted to slot size; IP wired inside the wrapper | gap | – | slot size and I/O configuration TBD by the harness repository |
| 27 | two forms: standalone layout and slot-wrapper layout; do not fill the slot | gap | PROPOSAL.md §6 | standalone: the two pad cells (foundry-pad size) + one core macro (references, replica, glue) with its own pins; wrapper: that macro placed and wired in the slot wrapper. IHP slot 7 exists only in the wrapper form |
| 28 | artwork only within density rules | n/a (none planned) | – | – |
| 29 | shared slots: independent repositories, slot layout in one of them | n/a (own slot) | – | – |
| 30 | dedicated pins: up to 3, any pad type, noted in the harness configuration | met (proposed) | PROPOSAL.md §2 (2 custom + 1 optional foundry analog pad) | – |
| 31 | custom pads: approval; same size and configuration as foundry pads; abut cleanly; layout in the repository; verified independently (DRC, LVS, simulation) | needs approval; then gap | PROPOSAL.md §1, §2, §7 | approval; pad cells built on the sky130 foundry-pad frame; per-pad DRC, LVS, CACE in their own macro directories |
| 32 | shared analog lines: < 5 Ω switches, not for high-frequency signals | met (by plan) | PROPOSAL.md §5 (DC on the shared lines; all dynamic measurements on the dedicated pins) | – |
| 33 | stages gated by four reviews | met (schedule) | PROPOSAL.md §8 | – |
| 34 | not ready at the final review → may miss tapeout | n/a | PROPOSAL.md §7 (pads first; references can be dropped for harness references) | – |
| 35 | awards: half at tapeout, half for measurement and published results | n/a | TEST_PLAN.md (measurement plan) | – |

## Template conformance

Template: `simi1505/sg13cmos5l_chipalooza_analog_project` at `c72f665b` (2026-08-28), read on 2026-11-23. Its layout:
`final/{gds,lef,lib,vh}`, `layout/`, `schematic/xschem/`, `testbenches/xschem/` (with `plot_simulations/`),
`macros/<macro>/{verification/{cace,drc,lvs},testbenches,netlist/{schematic,layout,pex},final,scripts,README.md,Makefile}`,
`verification/{drc,lvs}`, `netlist/`, `floorplan/`, `render/`, `scripts/`, `Makefile`, `submission.yaml`, `.designinit`.

| template item | this repository today | plan |
|---|---|---|
| `final/`, `layout/`, `schematic/`, `netlist/` of the top cell | missing | at the schematic review (schematic, netlist) and layout review (layout, final) |
| `macros/<macro>/` with CACE, DRC, LVS, PEX | missing | one macro per block: `sky130_cm_IOPadSingle2Diff`, `sky130_cm_IOPadDiff2Single`, `oa_core`, `bg_core`, `bias_dist`, `pad_ref_rb`, `ctrl` (names provisional) |
| `testbenches/xschem/` and plots | missing | with the sky130 schematics (schematic review) |
| `Makefile`, `.designinit`, `submission.yaml` | missing | copy from the template, adapt to sky130A (the template's precheck fields are IHP-specific) |
| `docs/` | present (proposal and plans) | the template has no `docs/`; kept as an addition |
