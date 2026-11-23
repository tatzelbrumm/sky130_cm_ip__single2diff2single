#!/usr/bin/env bash
# SPDX-FileCopyrightText: 2026 Christoph Maier
# SPDX-License-Identifier: Apache-2.0
#
# run_pads.sh: reproduce every number in verification/pads/results/ from a clean checkout.
# sky130 pre-layout schematic simulation (feasibility, not sign-off).
#
# Usage:  PDK_ROOT=/foss/pdks ./run_pads.sh [s2d] [d2s]     (default: both)
#         JOBS=4 sets how many ngspice runs go in parallel (default: number of CPUs).
# Needs:  ngspice (tested ngspice-47), python3 with numpy and matplotlib, sky130A under $PDK_ROOT.
# Writes: decks/*.spice (regenerated from scripts/gen_decks.py with this PDK_ROOT), build/ (data, logs;
#         git-ignored), results/*.md / *.csv / *.png.
# Port values (where the sky130 window is, see results/*_summary.md): S2D vcm and D2S vref, both 1.05 V.
set -euo pipefail
cd "$(dirname "$0")"
export PDK_ROOT="${PDK_ROOT:-/foss/pdks}"
export S2D_VCM_PORT="${S2D_VCM_PORT:-1.05}"
export D2S_VREF_PORT="${D2S_VREF_PORT:-1.05}"
JOBS="${JOBS:-$(nproc)}"
WHICH=("$@"); [ ${#WHICH[@]} -eq 0 ] && WHICH=(s2d d2s)

SPINIT="$PDK_ROOT/sky130A/libs.tech/ngspice/spinit"
[ -f "$SPINIT" ] || { echo "no sky130A ngspice spinit at $SPINIT (set PDK_ROOT)"; exit 1; }
# the PDK's ngspice init (ngbehavior=hsa, KLU); one thread per run, the runs go in parallel instead
sed 's/num_threads=[0-9]*/num_threads=1/' "$SPINIT" > decks/.spiceinit
mkdir -p build results
ngspice -v 2>&1 | grep -m1 ngspice- | tee build/versions.txt
grep -m1 open_pdks "$PDK_ROOT/sky130A/SOURCES" 2>/dev/null | tee -a build/versions.txt || true

python3 scripts/gen_decks.py "${WHICH[@]}"

decks=()
for w in "${WHICH[@]}"; do
  for c in tt ss ff sf fs; do decks+=("${w}_dc_$c" "${w}_ac_$c"); done
  if [ "$w" = s2d ]; then decks+=(s2d_vref_tt s2d_vref_ss s2d_vref_ff); fi
done
echo "running ${#decks[@]} decks, $JOBS in parallel (the DC decks take 10 .. 30 min each: the PDK's"
echo "xhigh_po model has abs(v) in its voltage coefficient, so ngspice falls back to gmin stepping per point)"
cd decks
printf '%s\n' "${decks[@]}" | xargs -P "$JOBS" -I{} sh -c 'ngspice -b {}.spice > ../build/{}.log 2>&1 || echo "FAILED: {}"'
cd ..
if grep -l -iE "^error|fatal" build/*.log; then echo "errors in the logs above"; fi
python3 scripts/analyze.py "${WHICH[@]}"
echo "done: results/"
