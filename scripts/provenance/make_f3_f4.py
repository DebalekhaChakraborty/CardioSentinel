"""Manuscript figures F3 and F4. Assembly and plotting only — no new metric.

F3 source: W1_WINDOW_COMPARATOR_REPORT_V1.md per-subject table (verbatim).
F4 source: E11 ATTEMPT 2 B0 held-out artifacts + the frozen fold consensus,
           the same estimand E11's outer geometry already reported in summary.
Palette: #2a78d6 / #eb6834 — validated colourblind-safe (dataviz validator,
light surface: CVD dE 24.7 protan, 32.7 tritan, normal 33.6
all checks PASS).
"""
from __future__ import annotations

import pathlib
import sys

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))
#: F3 is W1 evidence and F4 is B4 evidence; each is written beside its own
#: experiment rather than into a shared manuscript directory.
OUT_W1 = REPO / "docs" / "experiments" / "w1" / "figures"
OUT_B4 = REPO / "docs" / "experiments" / "b4" / "figures"

from cardiosentinel.neural.e11_data_binding import (  # noqa: E402
    E11Sources,
    bind_e11_data,
)
from cardiosentinel.neural.e11_instrumentation import (  # noqa: E402
    class_direction_consensus,
)

BLUE, ORANGE = "#2a78d6", "#eb6834"
INK, MUTED, GRID, SURFACE = "#1a1a1a", "#5a5a5a", "#d9d9d6", "#fcfcfb"
plt.rcParams.update({
    "font.size": 8, "axes.labelsize": 8, "axes.titlesize": 8.5,
    "xtick.labelsize": 7.5, "ytick.labelsize": 7.5, "legend.fontsize": 7.5,
    "axes.edgecolor": MUTED, "axes.linewidth": 0.6,
    "xtick.color": MUTED, "ytick.color": MUTED,
    "text.color": INK, "axes.labelcolor": INK,
    "figure.facecolor": SURFACE, "axes.facecolor": SURFACE,
    "savefig.facecolor": SURFACE, "pdf.fonttype": 42,
})

def recede(ax, xgrid=True):
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.grid(axis="x" if xgrid else "y", color=GRID, lw=0.5, zorder=0)
    ax.set_axisbelow(True)

# ---------------------------------------------------------------- F3
# verbatim from W1_WINDOW_COMPARATOR_REPORT_V1.md §3
SUBJ = ["s2004","s2005","s2019","s2020","s2023","s2031",
        "s2057","s2058","s2059","s3068","s3072","s3073"]
REF  = [38, 0, 6, 0, 0, 18, 5, 3, 47, 35, 1, 10]
T1   = [0.3750, 0.0000, 0.0000, 0.0000, 0.0000, 0.6207,
        0.8000, 0.0000, 0.0000, 0.4091, 0.0000, 0.8235]
W1   = [0.1890, 0.0000, 0.0000, 0.0000, 0.0000, 0.0580,
        0.0952, 0.0000, 0.0417, 0.1333, 0.0000, 0.2059]
DIFF, LO, HI = 0.1921, 0.0505, 0.3455
T1_MACRO, W1_MACRO = 0.2524, 0.0603

order = np.argsort(T1)                      # ascending, so best sits at the top
fig = plt.figure(figsize=(7.2, 4.3))
gs = fig.add_gridspec(2, 1, height_ratios=[3.4, 1.0], hspace=0.55)
ax, axr = fig.add_subplot(gs[0]), fig.add_subplot(gs[1])

y = np.arange(len(SUBJ))
for k, i in enumerate(order):
    ax.plot([W1[i], T1[i]], [k, k], color=GRID, lw=1.6, zorder=1,
            solid_capstyle="round")
    # orange drawn first and larger: where the two arms coincide (the seven
    # zeros) the square stays visible with the blue circle nested inside it
    ax.plot(W1[i], k, "s", ms=8.5, color=ORANGE, mec=SURFACE, mew=1.0, zorder=3)
    ax.plot(T1[i], k, "o", ms=5.0, color=BLUE,   mec=SURFACE, mew=0.8, zorder=4)

labels = [f"{SUBJ[i]}  ({REF[i]} ep.)" for i in order]
ax.set_yticks(y)
ax.set_yticklabels(labels)
for k, i in enumerate(order):                # episode-free subjects marked, not hidden
    if REF[i] == 0:
        ax.get_yticklabels()[k].set_color(MUTED)
ax.axvline(W1_MACRO, color=ORANGE, lw=0.9, ls=(0, (4, 3)), zorder=2)
ax.axvline(T1_MACRO, color=BLUE,   lw=0.9, ls=(0, (4, 3)), zorder=2)
ax.text(T1_MACRO, len(SUBJ) - 0.25, f" macro {T1_MACRO:.4f}",
        color=BLUE, fontsize=7, va="center")
ax.text(W1_MACRO, -0.78, f"macro {W1_MACRO:.4f} ", color=ORANGE, fontsize=7,
        va="center", ha="right")
ax.set_xlim(-0.05, 0.92)
ax.set_ylim(-1.1, len(SUBJ) - 0.05)
ax.set_xlabel("episode $F_1$")
recede(ax)
ax.set_title("(a)  Per-subject episode $F_1$, paired  ·  12 held-out subjects",
             loc="left")
ax.legend(handles=[
    Line2D([], [], marker="o", ls="", ms=5.0, color=BLUE,
           label="T1 episode state machine"),
    Line2D([], [], marker="s", ls="", ms=8.5, color=ORANGE,
           label="W1 memoryless window rule")],
    loc="lower right", frameon=False, handletextpad=0.6)
ax.text(0.30, 5.4, "seven subjects score zero —\n"
        "three have no reference episodes,\nfour are missed",
        fontsize=6.8, color=MUTED, va="center", linespacing=1.5)

axr.axvline(0, color=MUTED, lw=0.8, zorder=1)
axr.plot([LO, HI], [0, 0], color=BLUE, lw=2.2, solid_capstyle="round", zorder=2)
axr.plot([LO, HI], [0, 0], "|", color=BLUE, ms=9, mew=1.6, zorder=3)
axr.plot(DIFF, 0, "o", ms=8, color=BLUE, mec=SURFACE, mew=1.2, zorder=4)
axr.annotate(f"{DIFF:.4f}   [{LO:.4f}, {HI:.4f}]", (DIFF, 0),
             textcoords="offset points", xytext=(0, 13), ha="center",
             fontsize=8, color=INK, fontweight="bold")
axr.set_ylim(-0.55, 1.15)
axr.set_yticks([])
axr.set_xlim(-0.06, 0.42)
axr.set_xlabel("subject-macro episode $F_1$ difference, T1 − W1"
               "   (95% paired subject bootstrap)")
axr.spines["left"].set_visible(False)
recede(axr)
axr.set_title("(b)  Paired difference  ·  excludes zero  ·  one operating point",
              loc="left")

fig.tight_layout()
fig.savefig(OUT_W1 / "F3_episode_reasoning.pdf")
fig.savefig(OUT_W1 / "F3_episode_reasoning.png", dpi=200)
plt.close(fig)
print("F3 written")

# ---------------------------------------------------------------- F4

b = bind_e11_data(sources=E11Sources(
    waveform_cache=REPO/"cardiosentinel-features/b4-waveform-v1",
    protocol_dir=REPO / "cardiosentinel-runs/b4-e11-morphology-aware-v1"
                        "/E11_ATTEMPT_2/protocol"),
    expected_split_digest=(
        "ce037309cc2d67944acbee76e82700e5a54c9d2ff69bf54a121ab1b8940206c3"),
    experiment_id="FIGURE_F4")
E11D = REPO/"cardiosentinel-runs/b4-e11-morphology-aware-v1/E11_ATTEMPT_2/artifacts"

def stream_deltas(emb, lab, strm):
    out = {}
    for s in np.unique(strm):
        m = strm == s
        p, n = lab[m] == 1, lab[m] == 0
        if p.sum() == 0 or n.sum() == 0:
            continue
        out[str(s)] = emb[m][p].mean(0) - emb[m][n].mean(0)
    return out

train_cos, ho_cos, ho_norm, ho_name = [], [], [], []
for k in (0, 1, 2):
    z = np.load(E11D/f"e11_fold{k}_B0.npz")
    ot, ho = z["idx_ot"], z["idx_ho"]
    td = stream_deltas(z["emb_ot"].astype(np.float64), b.labels[ot], b.streams[ot])
    c = class_direction_consensus(list(td.values()))
    train_cos += [float(d @ c/np.linalg.norm(d)) for d in td.values()]
    for s, d in stream_deltas(z["emb_ho"].astype(np.float64),
                              b.labels[ho], b.streams[ho]).items():
        nrm = float(np.linalg.norm(d))
        ho_cos.append(float(d @ c/nrm))
        ho_norm.append(nrm)
        ho_name.append(s)
train_cos = np.array(train_cos)
ho_cos = np.array(ho_cos)
ho_norm = np.array(ho_norm)
neg = ho_cos < 0
print(f"  train streams {train_cos.size}, {int((train_cos<0).sum())} negative | "
      f"held-out {ho_cos.size}, {int(neg.sum())} negative")

fig, (ax, axr) = plt.subplots(1, 2, figsize=(7.2, 3.1),
                              gridspec_kw={"width_ratios": [1.0, 1.15]})
rng = np.random.default_rng(2026)
for row, vals, col, lab in ((1, train_cos, BLUE, f"outer-train  (n={train_cos.size})"),
                            (0, ho_cos, ORANGE, f"outer-held-out  (n={ho_cos.size})")):
    j = row + rng.uniform(-0.13, 0.13, vals.size)
    ax.plot(vals, j, "o", ms=4.0, color=col, alpha=0.55, mec="none",
            zorder=2, label=lab)
ax.axvline(0, color=MUTED, lw=0.8, ls=(0, (3, 3)), zorder=1)
ax.set_yticks([1, 0])
ax.set_yticklabels(["outer-train", "held-out"])
ax.set_xlim(-1.05, 1.05)
ax.set_ylim(-0.5, 1.5)
ax.set_xlabel("cosine to the fold's frozen class-direction consensus")
recede(ax)
ax.set_title("(a)  Class-direction coherence, B0", loc="left")
ax.text(-1.0, 1.38, f"{int((train_cos<0).sum())} / {train_cos.size} negative",
        fontsize=7, color=BLUE)
ax.text(-1.0, 0.38, f"{int(neg.sum())} / {ho_cos.size} negative",
        fontsize=7, color=ORANGE, fontweight="bold")

axr.plot(ho_cos[~neg], ho_norm[~neg], "o", ms=5.5, color=BLUE, alpha=0.6,
         mec="none", zorder=2, label=f"cosine $\\geq$ 0  (n={int((~neg).sum())})")
axr.plot(ho_cos[neg], ho_norm[neg], "D", ms=7.0, color=ORANGE, mec=SURFACE,
         mew=1.0, zorder=4, label=f"cosine < 0  (n={int(neg.sum())})")
axr.axvline(0, color=MUTED, lw=0.8, ls=(0, (3, 3)), zorder=1)
LBL = {"s20021:1": (-6, -16, "right"), "s20101:1": (9, 5, "left"),
       "s20171:0": (9, -2, "left")}
for nm, x, yv in zip(np.array(ho_name)[neg], ho_cos[neg], ho_norm[neg]):
    dx, dy, ha = LBL.get(str(nm), (9, 4, "left"))
    axr.annotate(str(nm), (x, yv), textcoords="offset points", xytext=(dx, dy),
                 fontsize=6.8, color=INK, ha=ha)
axr.set_xlabel("cosine to consensus")
axr.set_ylabel(r"$\|\delta\|$")
axr.set_xlim(-1.05, 1.05)
recede(axr, xgrid=False)
axr.grid(color=GRID, lw=0.5, zorder=0)
axr.set_title("(b)  Held-out streams: direction vs magnitude", loc="left")
axr.legend(loc="upper left", frameon=False)
fig.tight_layout()
fig.savefig(OUT_B4/"F4_representation_geometry.pdf")
fig.savefig(OUT_B4/"F4_representation_geometry.png", dpi=200)
plt.close(fig)
print("F4 written")
