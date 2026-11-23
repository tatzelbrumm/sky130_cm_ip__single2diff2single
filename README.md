<!--
SPDX-FileCopyrightText: 2026 Christoph Maier
SPDX-License-Identifier: Apache-2.0
-->
# sky130_cm_ip__single2diff2single

Custom single-to-differential (S2D) and differential-to-single (D2S) analog pads with selectable reference circuits, for the
**Chipalooza Challenge #4 (Chip Foundry Sky130)**. A port of slot 7 of the IHP sg13cmos5l Chipalooza #2 chip (taped out
November 2026), proposed as a proof of concept of custom analog pads and of AI-assisted analog design.

Designer: Christoph Maier.

| document | |
|---|---|
| [docs/PROPOSAL.md](docs/PROPOSAL.md) | the proposal (the five required items, port plan, risks, schedule); anonymous |
| [docs/PORT_PLAN.md](docs/PORT_PLAN.md) | port plan and sky130 feasibility results |
| [docs/TEST_PLAN.md](docs/TEST_PLAN.md) | measurement test plan |
| [docs/EQUIPMENT_NEEDED.md](docs/EQUIPMENT_NEEDED.md) | instrument types the test plan needs |
| [docs/RULES_COMPLIANCE.md](docs/RULES_COMPLIANCE.md) | rules-4 compliance matrix |
| [docs/SOURCES.md](docs/SOURCES.md) | sources of every IHP value quoted |
| [docs/LICENSE_NOTE.md](docs/LICENSE_NOTE.md) | license: Apache-2.0 or SHL-2.1, pending the organizers' approval |
| [docs/AI_ASSISTANCE.md](docs/AI_ASSISTANCE.md) | what was AI-assisted, and why the IP does not require AI |
| [verification/](verification/) | sky130 pre-layout feasibility simulations (reproducible decks and scripts; results as plots and tables) |

Predecessor (IHP sg13cmos5l, as taped out): [`tatzelbrumm/sg13cmos5l_cm_slot7`](https://github.com/tatzelbrumm/sg13cmos5l_cm_slot7)
(commit `158afc5`; Chipalooza #2 documentation on branch `chipalooza2-documentation`); design repository
[`tatzelbrumm/sg13cmos5l_cm_ip__single2diff2single`](https://github.com/tatzelbrumm/sg13cmos5l_cm_ip__single2diff2single).

## License

Apache-2.0 (`LICENSE`) or Solderpad Hardware License v2.1 (`LICENSES/SHL-2.1.txt`), **pending approval by the Chipalooza
organizers**; see [docs/LICENSE_NOTE.md](docs/LICENSE_NOTE.md).
