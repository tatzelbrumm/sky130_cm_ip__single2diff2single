#!/usr/bin/env bash
# SPDX-FileCopyrightText: 2026 Christoph Maier
# SPDX-License-Identifier: Apache-2.0
#
# Reproduce all sky130 pre-layout schematic simulations (feasibility, not sign-off).
#   PDK_ROOT  directory that holds sky130A (default /foss/pdks)
#   SIM_DIR   scratch directory for expanded decks, logs and data (default /tmp/sky130_cm_sim;
#             never inside verification/)
#   JOBS      parallel ngspice runs (default: number of CPUs)
# Usage: ./run_all.sh [group ...]   groups: smoke bg_dc bg_tran oa_dc oa_tran meas
set -euo pipefail
cd "$(dirname "$0")"
export PDK_ROOT="${PDK_ROOT:-/foss/pdks}"
export PDK=sky130A
export SIM_DIR="${SIM_DIR:-/tmp/sky130_cm_sim}"
case "$SIM_DIR" in "$(pwd)"*) echo "SIM_DIR must be outside verification/"; exit 1;; esac
mkdir -p "$SIM_DIR"
ngspice -v | grep -m1 ngspice-
cat "$PDK_ROOT/$PDK/SOURCES"
python3 -c 'import matplotlib' 2>/dev/null || pip install --break-system-packages matplotlib
groups=("$@")
[ ${#groups[@]} -eq 0 ] && groups=(smoke bg_dc bg_tran oa_dc oa_tran meas)
python3 scripts/run_sims.py "${groups[@]}"
# summarize whatever is complete
sum=()
for g in "${groups[@]}"; do
  case $g in smoke) sum+=(smoke);; bg_*) sum+=(bg);; oa_*) sum+=(oa);; meas) sum+=(meas);; esac
done
mapfile -t sum < <(printf '%s\n' "${sum[@]}" | awk '!s[$0]++')
# bg/oa summaries need both their DC and transient runs
for r in bg oa; do
  if printf '%s\n' "${sum[@]}" | grep -qx $r && \
     ! { [ -d "$SIM_DIR/${r}_dc" ] && [ -d "$SIM_DIR/${r}_tran" ]; }; then
    echo "skip $r summary: run both ${r}_dc and ${r}_tran"; sum=("${sum[@]/$r}")
  fi
done
python3 scripts/summarize.py ${sum[@]}
du -sh results
