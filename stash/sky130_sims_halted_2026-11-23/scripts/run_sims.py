#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Christoph Maier
# SPDX-License-Identifier: Apache-2.0
"""Expand the testbench templates in ../decks and run them with ngspice.

Tokens replaced in the templates: @PDK_ROOT@ @PDK@ @CORNER@ @OUT@ @NETLIST@ @DUT@.
Expanded decks, logs and text data go to $SIM_DIR (never into verification/).

Usage: run_sims.py [job-group ...]   groups: smoke bg_dc bg_tran oa_dc oa_tran meas (default: all)
"""
import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
VER = HERE.parent
DECKS = VER / "decks"
NETS = VER / "netlists"

PDK_ROOT = os.environ.get("PDK_ROOT", "/foss/pdks")
PDK = os.environ.get("PDK", "sky130A")
if not PDK.startswith("sky130"):
    raise SystemExit(f"PDK={PDK}: these decks need sky130A (export PDK=sky130A)")
SIM_DIR = Path(os.environ.get("SIM_DIR", "/tmp/sky130_cm_sim")).resolve()
NGSPICE = os.environ.get("NGSPICE", "ngspice")
JOBS = int(os.environ.get("JOBS", str(os.cpu_count() or 2)))

MOS_CORNERS = ["tt", "ss", "ff", "sf", "fs"]
# bandgap: MOS/BJT corner x xhigh_po corner (typical, low = ll, high = hh) -> library sections
BG_SECTIONS = []
for c in MOS_CORNERS:
    BG_SECTIONS += [c, ("ll" if c == "tt" else c + "_ll"), ("hh" if c == "tt" else c + "_hh")]
# the OA core has no resistor: MOS corners only
OA_SECTIONS = MOS_CORNERS

DUTS = {
    "bg": ("bg_core_sky130.spice", "bg_core_sky130"),
    "oa": ("oa_core_sky130.spice", "oa_core_sky130"),
}
# internal nodes saved by tb_ref_dc for the physical-range check in summarize.py
CHECKNODES = {
    "bg_core_sky130": "v(xdut.vpg) v(xdut.g) v(xdut.ea) v(xdut.eb) v(xdut.e2) v(xdut.ks)",
    "oa_core_sky130": "v(xdut.vpg) v(xdut.vbr) v(xdut.vnc) v(xdut.vres) v(xdut.d10) v(xdut.ks)",
}


def expand(template, corner, out, netlist="", dut=""):
    s = (DECKS / template).read_text()
    for k, v in {"@PDK_ROOT@": PDK_ROOT, "@PDK@": PDK, "@CORNER@": corner,
                 "@OUT@": str(out), "@NETLIST@": netlist, "@DUT@": dut,
                 "@CHECKNODES@": CHECKNODES.get(dut, "")}.items():
        s = s.replace(k, v)
    return s


def jobs_for(group):
    jobs = []
    if group == "smoke":
        jobs.append(("tb_smoke.spice", "tt", SIM_DIR / "smoke" / "smoke", "", ""))
    elif group in ("bg_dc", "bg_tran", "oa_dc", "oa_tran"):
        ref, kind = group.split("_")
        net, dut = DUTS[ref]
        secs = BG_SECTIONS if ref == "bg" else OA_SECTIONS
        for sec in secs:
            jobs.append((f"tb_ref_{kind}.spice", sec, SIM_DIR / group / f"{ref}_{sec}",
                         str(NETS / net), dut))
    elif group == "meas":
        for ref in ("bg", "oa"):
            net, dut = DUTS[ref]
            jobs.append(("tb_meas_path.spice", "tt", SIM_DIR / "meas" / f"meas_{ref}",
                         str(NETS / net), dut))
    else:
        raise SystemExit(f"unknown group {group}")
    return jobs


def run(job):
    template, corner, out, netlist, dut = job
    out.parent.mkdir(parents=True, exist_ok=True)
    deck = out.parent / (out.name + ".spice")
    deck.write_text(expand(template, corner, out, netlist, dut))
    # PDK-recommended ngspice init (compatibility mode hsa, KLU)
    init = out.parent / ".spiceinit"
    if not init.exists():
        init.write_text(Path(PDK_ROOT, PDK, "libs.tech/ngspice/spinit").read_text())
    log = out.parent / (out.name + ".log")
    with open(log, "w") as fh:
        r = subprocess.run([NGSPICE, "-b", deck.name], cwd=out.parent, stdout=fh,
                           stderr=subprocess.STDOUT)
    return deck, r.returncode


def main():
    groups = sys.argv[1:] or ["smoke", "bg_dc", "bg_tran", "oa_dc", "oa_tran", "meas"]
    jobs = [j for g in groups for j in jobs_for(g)]
    print(f"PDK_ROOT={PDK_ROOT} PDK={PDK} SIM_DIR={SIM_DIR} jobs={len(jobs)} parallel={JOBS}")
    bad = 0
    with ThreadPoolExecutor(JOBS) as ex:
        for deck, rc in ex.map(run, jobs):
            print(f"  rc={rc} {deck}")
            bad += rc != 0
    if bad:
        print(f"{bad} ngspice runs returned non-zero")
        sys.exit(1)


if __name__ == "__main__":
    main()
