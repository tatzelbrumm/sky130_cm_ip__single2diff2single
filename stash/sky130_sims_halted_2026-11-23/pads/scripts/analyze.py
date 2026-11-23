#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Christoph Maier
# SPDX-License-Identifier: Apache-2.0
"""Reduce the ngspice data of verification/pads/build/ to tables (results/*.md, *.csv) and plots (results/*.png).

sky130 pre-layout schematic simulation (feasibility, not sign-off).
Usage: python3 scripts/analyze.py [s2d] [d2s]      (default: whatever data exists)

Definitions
  S2D (pad swept 0 .. 1 V, u = pad - vref, vd = outp - outn, vc = (outp + outn)/2 - vcm):
    gain, offset: least-squares line vd = G u + b over the whole sweep; offset = b / G (input-referred).
    INL: max |vd - (G u + b)| / G over the sweep, input-referred (output-referred = 2 x).
    CM error: vc at u = 0 (pad = vref); also max |vc| over the sweep.
    supply current: -i(vdd) at u = 0, includes the ideal 5 uA iref (sourced from vdd).
    window: vcm values with |G - 2| <= 1 % and INL <= 2 mV (IHP's proposed dc limits).
  D2S (vd = vinp - vinn, input CM = vref, e = pad - vref):
    gain, offset, INL: least-squares line e = G vd + b over |vd| <= 1 V; offset = b (output, at vd = 0
    by the fit); INL = max |e - (G vd + b)| over |vd| <= 1 V (output-referred, as IHP).
    swing: the e range around 0 over which |e - (G vd + b)| <= 10 mV, from the vd = +-2 V sweep (it
    includes the input-window limit of the units, which see vref +- vd/2).
    window: vref values with |G - 0.5| <= 1 % and INL <= 10 mV (IHP's dc limits) at 1 kOhm.
  AC (both): -3 dB frequency relative to the 100 Hz value; peaking = max |H| / |H(100 Hz)| in dB.
"""
import csv
import glob
import math
import os
import re
import sys
from collections import defaultdict

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
PADS = os.path.dirname(HERE)
BUILD = os.path.join(PADS, "build")
RES = os.path.join(PADS, "results")
LABEL = "sky130 pre-layout schematic simulation (feasibility, not sign-off)"
S2D_VREF = 0.49
EXTREMES = [("tt", 27), ("ss", -40), ("ff", 125)]


def load(fn):
    with open(fn) as f:
        names = f.readline().split()
    d = np.atleast_2d(np.loadtxt(fn, skiprows=1))
    return {n: d[:, i] for i, n in enumerate(names)}


def versions():
    v = {}
    try:
        import subprocess
        out = subprocess.run(["ngspice", "-v"], capture_output=True, text=True).stdout
        m = re.search(r"ngspice-(\S+)", out)
        v["ngspice"] = "ngspice-" + m.group(1) if m else out.strip().splitlines()[0]
    except Exception:
        v["ngspice"] = "unknown"
    pdk = os.environ.get("PDK_ROOT", "/foss/pdks")
    src = os.path.join(pdk, "sky130A", "SOURCES")
    v["pdk"] = "sky130A"
    if os.path.exists(src):
        txt = open(src).read()
        m = re.search(r"open_pdks\s+(\S+)", txt)
        v["open_pdks"] = m.group(1) if m else txt.strip().splitlines()[0]
    return v


def md_header(title):
    v = versions()
    return [f"<!--\nSPDX-FileCopyrightText: 2026 Christoph Maier\nSPDX-License-Identifier: Apache-2.0\n-->",
            f"# {title}", "",
            f"**{LABEL}.**", "",
            f"Tools: {v.get('ngspice')}; PDK {v.get('pdk')} (open_pdks {v.get('open_pdks', '?')}), "
            f"sky130_fd_pr g5v0d10v5 devices, xhigh_po resistors, MIM capacitors. "
            f"Decks: `verification/pads/decks/`, reduced by `scripts/analyze.py`.", ""]


def mmm(vals):
    a = np.asarray(vals, float)
    return a.min(), a.max()


def bw_peak(f, mag):
    m0 = mag[0]
    pk = 20 * math.log10(mag.max() / m0)
    idx = np.where(mag < m0 / math.sqrt(2))[0]
    if len(idx) == 0:
        return float("nan"), pk
    i = idx[0]
    # log interpolation
    f1, f2, m1, m2 = f[i - 1], f[i], mag[i - 1], mag[i]
    t = (m0 / math.sqrt(2) - m1) / (m2 - m1)
    return 10 ** (math.log10(f1) + t * (math.log10(f2) - math.log10(f1))), pk


def parse_name(fn, prefix):
    b = os.path.basename(fn)[len(prefix):-4]
    parts = b.split("_")
    out = {"corner": parts[0]}
    for p in parts[1:]:
        m = re.match(r"([A-Za-z]+)(-?[0-9.]+)(p?)$", p)
        if m and m.group(1) in ("T", "V", "cm", "vr", "cl"):
            out[m.group(1)] = float(m.group(2))
        else:
            out["tag"] = p
    return out


# ------------------------------------------------------------------ S2D
def s2d_dc_rows():
    rows = []
    for fn in sorted(glob.glob(os.path.join(BUILD, "s2d_dc_*.txt"))):
        k = parse_name(fn, "s2d_dc_")
        d = load(fn)
        vin = d["v-sweep"]
        u = vin - S2D_VREF
        vd = d["v(op)"] - d["v(on)"]
        vc = (d["v(op)"] + d["v(on)"]) / 2 - k["cm"]
        G, b = np.polyfit(u, vd, 1)
        inl = np.max(np.abs(vd - (G * u + b))) / G
        i0 = np.argmin(np.abs(u))
        rows.append(dict(corner=k["corner"], T=k["T"], V=k["V"], vcm=k["cm"], gain=G, off_mV=b / G * 1e3,
                         inl_mV=inl * 1e3, cm0_mV=vc[i0] * 1e3, cmmax_mV=np.max(np.abs(vc)) * 1e3,
                         idd_uA=-d["i(vdd)"][i0] * 1e6))
    return rows


def s2d_ok(r):
    return abs(r["gain"] - 2) <= 0.02 and r["inl_mV"] <= 2.0


def write_csv(rows, fn):
    if not rows:
        return
    with open(fn, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        for r in rows:
            w.writerow({k: (f"{v:.6g}" if isinstance(v, float) else v) for k, v in r.items()})


def window(rows, key, okf):
    """per (corner, T, V): sorted list of key values that pass, as contiguous range min..max."""
    by = defaultdict(list)
    for r in rows:
        by[(r["corner"], r["T"], r["V"])].append(r)
    out = {}
    for c, rs in by.items():
        good = sorted(r[key] for r in rs if okf(r))
        out[c] = (min(good), max(good)) if good else (float("nan"), float("nan"))
    return out


def s2d(port_vcm):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    rows = s2d_dc_rows()
    if not rows:
        print("no S2D DC data")
        return
    write_csv(rows, os.path.join(RES, "s2d_dc_all.csv"))
    win = window(rows, "vcm", s2d_ok)
    lo = max(v[0] for v in win.values())
    hi = min(v[1] for v in win.values())
    L = md_header("S2D core amplifier, sky130 port: results")
    L += ["Conditions: ideal 5 uA iref, vref = 0.49 V (ideal source), pad swept 0 .. 1 V (10 mV steps), "
          "0.5 pF external load per output plus the built-in 16 x 16 um MIM. No ESD, no pad, no layout, "
          "no mismatch (systematic offset only).", ""]
    L += ["## vcm window (where the port works)", "",
          "Pass = |gain - 2| <= 1 % and INL <= 2 mV (IHP's proposed DC limits). vcm swept 0.80 .. 1.40 V "
          "in 50 mV steps (and 1.26 V).", "",
          "| corner | T (C) | vdd (V) | vcm min (V) | vcm max (V) |", "|---|---:|---:|---:|---:|"]
    for (c, t, v), (a, b) in sorted(win.items(), key=lambda x: (x[0][0], x[0][1], x[0][2])):
        L.append(f"| {c} | {t:g} | {v:g} | {a:.2f} | {b:.2f} |")
    L += ["", f"**Common window over all 5 corners x (-40, 27, 125 C) x (3.0, 3.3, 3.6 V): vcm = {lo:.2f} .. {hi:.2f} V.** "
          f"The IHP value vcm = 1.26 V is "
          + ("inside" if lo <= 1.26 <= hi else "outside") + " it. Port value used below: "
          f"vcm = {port_vcm:g} V.", ""]
    for vv in (3.0, 3.3, 3.6):
        ws = [w for (c, t, v), w in win.items() if v == vv]
        L.append(f"- vdd = {vv:g} V only: vcm = {max(w[0] for w in ws):.2f} .. {min(w[1] for w in ws):.2f} V (all corners, -40 .. 125 C)")
    L.append("")
    L += ["Why: the units are PMOS pairs whose gates see up to vcm + 0.51 V (feedback and CMFB units on the "
          "outputs). The sky130 g5v0d10v5 pfet needs about 0.3 .. 0.4 V more Vsg than IHP's hv pmos "
          "(1.10 V at 5 uA, W/L 20/1, tt 27 C; 1.27 V at ss -40 C), so the upper end of the window drops; "
          "the lower end is set by the outputs (vcm - 0.51 V) against the NMOS fold sinks and cascodes.", ""]

    # --- table at the port vcm
    sel = [r for r in rows if abs(r["vcm"] - port_vcm) < 1e-6]
    L += [f"## DC at vcm = {port_vcm:g} V", "",
          "| corner | T (C) | vdd (V) | gain | offset (mV, in) | INL (mV, in) | CM err at pad = vref (mV) | max abs CM err (mV) | I(vdd) (uA) |",
          "|---|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for r in sorted(sel, key=lambda r: (r["corner"], r["T"], r["V"])):
        if (r["corner"], int(r["T"])) in EXTREMES:
            L.append(f"| {r['corner']} | {r['T']:g} | {r['V']:g} | {r['gain']:.5f} | {r['off_mV']:.3f} | {r['inl_mV']:.3f} | "
                     f"{r['cm0_mV']:.2f} | {r['cmmax_mV']:.2f} | {r['idd_uA']:.1f} |")
    L += ["", "Rows: the three requested PVT points (tt 27 C, ss -40 C, ff 125 C) x 3 supplies; "
          "all 45 points are in `s2d_dc_all.csv`.", ""]
    L += ["### min / typ / max", "", "| quantity | min | typ (tt 27 C 3.3 V) | max | over |", "|---|---:|---:|---:|---|"]
    typ = [r for r in sel if r["corner"] == "tt" and r["T"] == 27 and r["V"] == 3.3][0]
    ext = [r for r in sel if (r["corner"], int(r["T"])) in EXTREMES]
    for key, name, f in (("gain", "gain", "{:.5f}"), ("off_mV", "offset, input-referred (mV)", "{:.3f}"),
                         ("inl_mV", "INL, input-referred (mV)", "{:.3f}"), ("cm0_mV", "CM error at pad = vref (mV)", "{:.2f}"),
                         ("cmmax_mV", "max abs CM error over sweep (mV)", "{:.2f}"), ("idd_uA", "I(vdd) incl. 5 uA iref (uA)", "{:.1f}")):
        for lab, rs in (("3 PVT x 3 vdd", ext), ("5 corners x 3 T x 3 vdd", sel)):
            a, b = mmm([r[key] for r in rs])
            L.append(f"| {name} | {f.format(a)} | {f.format(typ[key])} | {f.format(b)} | {lab} |")
    # IHP vcm too
    sel126 = [r for r in rows if abs(r["vcm"] - 1.26) < 1e-6 and (r["corner"], int(r["T"])) in EXTREMES]
    if sel126:
        L += ["", "### Same at the IHP value vcm = 1.26 V (for comparison)", "",
              "| corner | T (C) | vdd (V) | gain | INL (mV, in) | CM err (mV) |", "|---|---:|---:|---:|---:|---:|"]
        for r in sorted(sel126, key=lambda r: (r["corner"], r["T"], r["V"])):
            L.append(f"| {r['corner']} | {r['T']:g} | {r['V']:g} | {r['gain']:.5f} | {r['inl_mV']:.3f} | {r['cm0_mV']:.2f} |")

    # --- AC
    ac = []
    for fn in sorted(glob.glob(os.path.join(BUILD, "s2d_acd_*.txt"))):
        k = parse_name(fn, "s2d_acd_")
        d = load(fn)
        f = d["frequency"]
        bw, pk = bw_peak(f, d["mag(vd)"])
        fc = fn.replace("s2d_acd_", "s2d_acc_")
        dc_ = load(fc)
        bwc, pkc = bw_peak(dc_["frequency"], dc_["mag(vc)"])
        op = load(fn.replace("s2d_acd_", "s2d_op_"))
        ac.append(dict(corner=k["corner"], T=k["T"], V=k["V"], g0=d["mag(vd)"][0], bw_MHz=bw / 1e6, peak_dB=pk,
                       bwcm_MHz=bwc / 1e6, peakcm_dB=pkc, idd_uA=-float(np.atleast_1d(op["i(vdd)"])[0]) * 1e6))
    if ac:
        write_csv(ac, os.path.join(RES, "s2d_ac_all.csv"))
        L += ["", f"## Closed-loop AC at vcm = {port_vcm:g} V, pad = vref", "",
              "Differential: pad -> outp - outn (ideal 2). Common mode: vcm -> (outp + outn)/2 (ideal 1; shows the CMFB loop).", "",
              "| corner | T (C) | vdd (V) | gain at 100 Hz | -3 dB BW (MHz) | peaking (dB) | CM BW (MHz) | CM peaking (dB) | I(vdd) op (uA) |",
              "|---|---:|---:|---:|---:|---:|---:|---:|---:|"]
        for r in sorted(ac, key=lambda r: (r["corner"], r["T"], r["V"])):
            if (r["corner"], int(r["T"])) in EXTREMES:
                L.append(f"| {r['corner']} | {r['T']:g} | {r['V']:g} | {r['g0']:.4f} | {r['bw_MHz']:.3f} | {r['peak_dB']:.3f} | "
                         f"{r['bwcm_MHz']:.3f} | {r['peakcm_dB']:.3f} | {r['idd_uA']:.1f} |")
        L += ["", "| quantity | min | max | over |", "|---|---:|---:|---|"]
        for key, name in (("bw_MHz", "-3 dB BW (MHz)"), ("peak_dB", "peaking (dB)"), ("bwcm_MHz", "CM BW (MHz)"),
                          ("peakcm_dB", "CM peaking (dB)")):
            e = [r for r in ac if (r["corner"], int(r["T"])) in EXTREMES]
            a, b = mmm([r[key] for r in e])
            a2, b2 = mmm([r[key] for r in ac])
            L.append(f"| {name} | {a:.3f} | {b:.3f} | 3 PVT x 3 vdd |")
            L.append(f"| {name} | {a2:.3f} | {b2:.3f} | 5 corners x 3 T x 3 vdd |")

    L += ["", "## IHP sg13cmos5l schematic results (for comparison only, not sky130)", "",
          "Gain 1.9985 .. 1.9993, INL <= 1.07 mV over 0 .. 1 V, CM error 5 .. 18 mV, BW 1.35 .. 1.81 MHz, ring current about 115 uA.", ""]
    open(os.path.join(RES, "s2d_summary.md"), "w").write("\n".join(L) + "\n")

    # --- plots
    fig, ax = plt.subplots(1, 2, figsize=(10, 3.8))
    for (c, t) in EXTREMES:
        for v, ls in ((3.0, ":"), (3.3, "-"), (3.6, "--")):
            fn = os.path.join(BUILD, f"s2d_dc_{c}_T{t}_V{v:g}_cm{port_vcm:g}.txt")
            if not os.path.exists(fn):
                continue
            d = load(fn)
            u = d["v-sweep"] - S2D_VREF
            vd = d["v(op)"] - d["v(on)"]
            G, b = np.polyfit(u, vd, 1)
            ax[0].plot(d["v-sweep"], (vd - G * u - b) / G * 1e3, ls, label=f"{c} {t} C {v:g} V")
            ax[1].plot(d["v-sweep"], ((d["v(op)"] + d["v(on)"]) / 2 - port_vcm) * 1e3, ls)
    ax[0].set_xlabel("pad (V)"); ax[0].set_ylabel("INL, input-referred (mV)")
    ax[1].set_xlabel("pad (V)"); ax[1].set_ylabel("(outp+outn)/2 - vcm (mV)")
    ax[0].legend(fontsize=6, ncol=1)
    fig.suptitle(f"S2D sky130 port, vcm = {port_vcm:g} V, vref = 0.49 V ({LABEL})", fontsize=8)
    fig.tight_layout()
    fig.savefig(os.path.join(RES, "s2d_dc_inl_cm.png"), dpi=110)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(6, 3.8))
    corners = sorted(set(r["corner"] for r in rows))
    for (c, t, v), (a, b) in sorted(win.items()):
        y = corners.index(c) * 10 + [-40, 27, 125].index(int(t)) * 3 + [3.0, 3.3, 3.6].index(v)
        ax.plot([a, b], [y, y], "-", lw=2, color={-40: "tab:blue", 27: "tab:green", 125: "tab:red"}[int(t)])
    ax.axvspan(lo, hi, color="0.85", zorder=0)
    ax.axvline(1.26, color="k", ls="--", lw=0.8)
    ax.set_yticks([i * 10 + 4 for i in range(len(corners))]); ax.set_yticklabels(corners)
    ax.set_xlabel("vcm (V)  [bars: passing range per corner / T (colour) / vdd; grey: common; dashed: IHP 1.26 V]")
    ax.set_title("S2D sky130 port: vcm window (|gain-2|<=1 %, INL<=2 mV)", fontsize=9)
    fig.tight_layout()
    fig.savefig(os.path.join(RES, "s2d_vcm_window.png"), dpi=110)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(6, 3.8))
    for (c, t) in EXTREMES:
        for v, ls in ((3.0, ":"), (3.3, "-"), (3.6, "--")):
            fn = os.path.join(BUILD, f"s2d_acd_{c}_T{t}_V{v:g}.txt")
            if os.path.exists(fn):
                d = load(fn)
                ax.semilogx(d["frequency"], 20 * np.log10(d["mag(vd)"]), ls, label=f"{c} {t} C {v:g} V")
    ax.set_xlabel("f (Hz)"); ax.set_ylabel("|(outp-outn)/pad| (dB)"); ax.set_ylim(-30, 12); ax.grid(True, which="both", lw=0.3)
    ax.legend(fontsize=6); ax.set_title(f"S2D sky130 port closed loop, 0.5 pF/output ({LABEL})", fontsize=8)
    fig.tight_layout(); fig.savefig(os.path.join(RES, "s2d_ac.png"), dpi=110); plt.close(fig)
    print(f"S2D: common vcm window {lo:.2f} .. {hi:.2f} V")


# ------------------------------------------------------------------ D2S
def d2s_dc_rows():
    rows = []
    for fn in sorted(glob.glob(os.path.join(BUILD, "d2s_dc_*.txt"))):
        k = parse_name(fn, "d2s_dc_")
        d = load(fn)
        vd = d["v-sweep"]
        e = d["v(pad)"] - d["v(vref)"]
        m = np.abs(vd) <= 1.0 + 1e-9
        G, b = np.polyfit(vd[m], e[m], 1)
        dev = e - (G * vd + b)
        inl = np.max(np.abs(dev[m]))
        # swing: contiguous range around vd = 0 with |dev| <= 10 mV
        i0 = np.argmin(np.abs(vd))
        bad = np.abs(dev) > 0.010
        lo = i0
        while lo > 0 and not bad[lo - 1]:
            lo -= 1
        hi = i0
        while hi < len(vd) - 1 and not bad[hi + 1]:
            hi += 1
        iop = [n for n in d if "xop" in n][0]
        ion = [n for n in d if "xon" in n][0]
        rows.append(dict(corner=k["corner"], T=k["T"], V=k["V"], vref=k["vr"], load=k.get("tag", ""), gain=G,
                         off_mV=b * 1e3, inl_mV=inl * 1e3, e_lo=e[lo], e_hi=e[hi], pad_lo=d["v(pad)"][lo], pad_hi=d["v(pad)"][hi],
                         idd_uA=-d["i(vdd)"][i0] * 1e6, iop_uA=abs(d[iop][i0]) * 1e6, ion_uA=abs(d[ion][i0]) * 1e6))
    return rows


def d2s_ok(r):
    return abs(r["gain"] - 0.5) <= 0.005 and r["inl_mV"] <= 10.0


def d2s(port_vref):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    rows = d2s_dc_rows()
    if not rows:
        print("no D2S DC data")
        return
    write_csv(rows, os.path.join(RES, "d2s_dc_all.csv"))
    r1k = [r for r in rows if r["load"] == "r1k"]
    win = window(r1k, "vref", d2s_ok)
    lo = max(v[0] for v in win.values())
    hi = min(v[1] for v in win.values())
    L = md_header("D2S core amplifier, sky130 port: results")
    L += ["Conditions: ideal 5 uA iref; vinp = vref + vd/2, vinn = vref - vd/2 (input CM = vref, the shared vcm line); "
          "load 1 kOhm from pad to vref or open, 100 pF (DC: no effect). No ESD, no pad, no 2 kOhm secondary "
          "stages, no layout, no mismatch.", ""]
    L += ["## vref window (where the port works)", "",
          "Pass = |gain - 0.5| <= 1 % and INL (vd = +-1 V) <= 10 mV (IHP's DC limits), 1 kOhm load. "
          "vref swept 0.9 .. 1.5 V in 0.1 V steps (and 1.26 V).", "",
          "| corner | T (C) | vdd (V) | vref min (V) | vref max (V) |", "|---|---:|---:|---:|---:|"]
    for (c, t, v), (a, b) in sorted(win.items()):
        L.append(f"| {c} | {t:g} | {v:g} | {a:.2f} | {b:.2f} |")
    L += ["", f"**Common window over all corners / T / vdd: vref = {lo:.2f} .. {hi:.2f} V.** IHP value 1.26 V is "
          + ("inside" if lo <= 1.26 <= hi else "outside") + f" it. Port value used below: vref = {port_vref:g} V.", ""]
    for ld, title in (("r1k", "1 kOhm load"), ("open", "unloaded")):
        sel = [r for r in rows if r["load"] == ld and abs(r["vref"] - port_vref) < 1e-6]
        if not sel:
            continue
        L += [f"## DC at vref = {port_vref:g} V, {title}", "",
              "| corner | T (C) | vdd (V) | gain | offset (mV, out) | INL +-1 V (mV, out) | linear swing pad - vref (V) | I(vdd) (uA) | I(OP) (uA) | I(ON) (uA) |",
              "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|"]
        for r in sorted(sel, key=lambda r: (r["corner"], r["T"], r["V"])):
            if (r["corner"], int(r["T"])) in EXTREMES:
                L.append(f"| {r['corner']} | {r['T']:g} | {r['V']:g} | {r['gain']:.5f} | {r['off_mV']:.3f} | {r['inl_mV']:.3f} | "
                         f"{r['e_lo']:+.3f} .. {r['e_hi']:+.3f} | {r['idd_uA']:.1f} | {r['iop_uA']:.1f} | {r['ion_uA']:.1f} |")
        typ = [r for r in sel if r["corner"] == "tt" and r["T"] == 27 and r["V"] == 3.3][0]
        ext = [r for r in sel if (r["corner"], int(r["T"])) in EXTREMES]
        L += ["", "| quantity | min | typ (tt 27 C 3.3 V) | max | over |", "|---|---:|---:|---:|---|"]
        for key, name, f in (("gain", "gain", "{:.5f}"), ("off_mV", "offset, output (mV)", "{:.3f}"),
                             ("inl_mV", "INL +-1 V, output (mV)", "{:.3f}"), ("e_lo", "linear swing, low end, pad - vref (V)", "{:+.3f}"),
                             ("e_hi", "linear swing, high end, pad - vref (V)", "{:+.3f}"),
                             ("idd_uA", "I(vdd) quiescent incl. 5 uA iref (uA)", "{:.1f}"), ("iop_uA", "I(OP) quiescent (uA)", "{:.1f}")):
            for lab, rs in (("3 PVT x 3 vdd", ext), ("5 corners x 3 T x 3 vdd", sel)):
                a, b = mmm([r[key] for r in rs])
                L.append(f"| {name} | {f.format(a)} | {f.format(typ[key])} | {f.format(b)} | {lab} |")
        L.append("")
    sel126 = [r for r in r1k if abs(r["vref"] - 1.26) < 1e-6 and (r["corner"], int(r["T"])) in EXTREMES]
    if sel126 and abs(port_vref - 1.26) > 1e-6:
        L += ["### Same at the IHP value vref = 1.26 V, 1 kOhm (for comparison)", "",
              "| corner | T (C) | vdd (V) | gain | INL (mV) |", "|---|---:|---:|---:|---:|"]
        for r in sorted(sel126, key=lambda r: (r["corner"], r["T"], r["V"])):
            L.append(f"| {r['corner']} | {r['T']:g} | {r['V']:g} | {r['gain']:.5f} | {r['inl_mV']:.3f} |")
        L.append("")

    ac = []
    for fn in sorted(glob.glob(os.path.join(BUILD, "d2s_ac_*.txt"))):
        k = parse_name(fn, "d2s_ac_")
        d = load(fn)
        bw, pk = bw_peak(d["frequency"], d["mag(v(pad))"])
        ac.append(dict(corner=k["corner"], T=k["T"], V=k["V"], load=k.get("tag", ""), cl_pF=k["cl"], g0=d["mag(v(pad))"][0],
                       bw_MHz=bw / 1e6, peak_dB=pk))
    if ac:
        write_csv(ac, os.path.join(RES, "d2s_ac_all.csv"))
        L += [f"## Closed-loop AC at vref = {port_vref:g} V, vd = 0", "",
              "| load | Cl (pF) | BW min (MHz) | BW tt 27 C 3.3 V (MHz) | BW max (MHz) | peaking max (dB) | peaking tt (dB) | over |",
              "|---|---:|---:|---:|---:|---:|---:|---|"]
        for ld in ("r1k", "open"):
            for cl in (10, 100, 300):
                for lab, f in (("3 PVT x 3 vdd", lambda r: (r["corner"], int(r["T"])) in EXTREMES), ("5 corners x 3 T x 3 vdd", lambda r: True)):
                    rs = [r for r in ac if r["load"] == ld and r["cl_pF"] == cl and f(r)]
                    if not rs:
                        continue
                    t = [r for r in rs if r["corner"] == "tt" and r["T"] == 27 and r["V"] == 3.3][0]
                    a, b = mmm([r["bw_MHz"] for r in rs])
                    L.append(f"| {'1 kOhm' if ld == 'r1k' else 'open'} | {cl} | {a:.3f} | {t['bw_MHz']:.3f} | {b:.3f} | "
                             f"{max(r['peak_dB'] for r in rs):.3f} | {t['peak_dB']:.3f} | {lab} |")
        L.append("")
    L += ["## IHP sg13cmos5l schematic results (for comparison only, not sky130)", "",
          "Gain 0.498 .. 0.500, INL <= 7.4 mV at 3.3 .. 3.6 V (up to 87 mV at 3.0 V), BW 1.78 .. 2.25 MHz, quiescent about 300 uA.", ""]
    open(os.path.join(RES, "d2s_summary.md"), "w").write("\n".join(L) + "\n")

    fig, ax = plt.subplots(1, 2, figsize=(10, 3.8))
    for (c, t) in EXTREMES:
        for v, ls in ((3.0, ":"), (3.3, "-"), (3.6, "--")):
            fn = os.path.join(BUILD, f"d2s_dc_{c}_T{t}_V{v:g}_vr{port_vref:g}_r1k.txt")
            if not os.path.exists(fn):
                continue
            d = load(fn)
            vd = d["v-sweep"]; e = d["v(pad)"] - d["v(vref)"]
            m = np.abs(vd) <= 1
            G, b = np.polyfit(vd[m], e[m], 1)
            ax[0].plot(vd[m], (e[m] - G * vd[m] - b) * 1e3, ls, label=f"{c} {t} C {v:g} V")
            ax[1].plot(vd, e, ls)
    ax[0].set_xlabel("vinp - vinn (V)"); ax[0].set_ylabel("INL, output (mV)"); ax[0].legend(fontsize=6)
    ax[1].set_xlabel("vinp - vinn (V)"); ax[1].set_ylabel("pad - vref (V)"); ax[1].grid(True, lw=0.3)
    fig.suptitle(f"D2S sky130 port, vref = {port_vref:g} V, 1 kOhm to vref ({LABEL})", fontsize=8)
    fig.tight_layout(); fig.savefig(os.path.join(RES, "d2s_dc_inl.png"), dpi=110); plt.close(fig)

    fig, ax = plt.subplots(1, 2, figsize=(10, 3.8), sharey=True)
    for j, ld in enumerate(("r1k", "open")):
        for cl, col in ((10, "tab:blue"), (100, "tab:green"), (300, "tab:red")):
            for (c, t), ls in zip(EXTREMES, ("-", ":", "--")):
                fn = os.path.join(BUILD, f"d2s_ac_{c}_T{t}_V3.3_{ld}_cl{cl}p.txt")
                if os.path.exists(fn):
                    d = load(fn)
                    ax[j].semilogx(d["frequency"], 20 * np.log10(d["mag(v(pad))"]), ls, color=col, label=f"{cl} pF {c} {t} C")
        ax[j].set_title("1 kOhm to vref" if ld == "r1k" else "unloaded", fontsize=8)
        ax[j].set_xlabel("f (Hz)"); ax[j].set_ylim(-30, 0); ax[j].grid(True, which="both", lw=0.3)
    ax[0].set_ylabel("|pad / (vinp - vinn)| (dB)"); ax[0].legend(fontsize=6)
    fig.suptitle(f"D2S sky130 port closed loop, 3.3 V ({LABEL})", fontsize=8)
    fig.tight_layout(); fig.savefig(os.path.join(RES, "d2s_ac.png"), dpi=110); plt.close(fig)

    fig, ax = plt.subplots(figsize=(6, 3.8))
    corners = sorted(set(r["corner"] for r in rows))
    for (c, t, v), (a, b) in sorted(win.items()):
        y = corners.index(c) * 10 + [-40, 27, 125].index(int(t)) * 3 + [3.0, 3.3, 3.6].index(v)
        ax.plot([a, b], [y, y], "-", lw=2, color={-40: "tab:blue", 27: "tab:green", 125: "tab:red"}[int(t)])
    ax.axvspan(lo, hi, color="0.85", zorder=0); ax.axvline(1.26, color="k", ls="--", lw=0.8)
    ax.set_yticks([i * 10 + 4 for i in range(len(corners))]); ax.set_yticklabels(corners)
    ax.set_xlabel("vref (V)  [bars per corner / T (colour) / vdd; grey: common; dashed: IHP 1.26 V]")
    ax.set_title("D2S sky130 port: vref window (|gain-0.5|<=1 %, INL<=10 mV, 1 kOhm)", fontsize=9)
    fig.tight_layout(); fig.savefig(os.path.join(RES, "d2s_vref_window.png"), dpi=110); plt.close(fig)
    print(f"D2S: common vref window {lo:.2f} .. {hi:.2f} V")


if __name__ == "__main__":
    which = sys.argv[1:] or ["s2d", "d2s"]
    os.makedirs(RES, exist_ok=True)
    if "s2d" in which:
        s2d(float(os.environ.get("S2D_VCM_PORT", "1.05")))
    if "d2s" in which:
        d2s(float(os.environ.get("D2S_VREF_PORT", "1.26")))
