<!--
SPDX-FileCopyrightText: 2026 Christoph Maier
SPDX-License-Identifier: Apache-2.0
-->
# AI assistance

This IP block is a **proof of concept of AI-assisted analog design**. Designer: Christoph Maier.

What was AI-assisted, in the predecessor IHP sg13cmos5l design (Chipalooza #2 slot 7) and in this repository, as the
repositories' commit histories and session records show:

- **circuits:** schematic netlists and sizing of blocks, in sessions directed by the designer (the designer specified the
  pads' function, the modes and the replica-bias concept);
- **layout scripts:** scripted layout generation (Python / KLayout) for macros and the slot assembly;
- **netlists and test benches:** SPICE netlists, CACE characterization files, test-platform benches;
- **data sheets:** generated from the committed CACE results by a script;
- **documentation:** nearly all of it, including this proposal.

What is not AI-dependent:

- Verification uses open-source tools only (ngspice, CACE, KLayout, magic, netgen; versions recorded with each result).
- Every source needed to use, verify or modify the block is a plain file in the repository (netlists, decks, scripts,
  layouts); no AI tool, model or service is needed to run any flow or to change the design.
- The designer reviewed the results and made the design decisions; the decisions are recorded in the documents.

This statement claims no more than the repositories show: where a document or result was produced in an AI-assisted session,
it was checked by the open-source tools named in it, not by the AI.
