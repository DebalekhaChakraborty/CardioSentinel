"""Manuscript diagrams F1, F2, F5. Drawing only — no scientific quantity computed.

F1: handbook §52 (four layers), §52.1 (train/runtime equivalence audit).
F2: handbook v1.5 §3-§4, DATA_SPLIT_POLICY.md, E13a consumption record.
F5: EXPLANATION_EVALUATION_REPORT_V1.md §2, §4, §4.1, §4.2.

Text is never hand-positioned. `panel()` stacks wrapped lines from the top of a
box using the real font metrics, so a string that grows cannot silently escape
its own frame — which is exactly how the first two passes of these diagrams
failed.
"""
from __future__ import annotations
import pathlib, textwrap
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

OUT = pathlib.Path(__file__).resolve().parent
BLUE, ORANGE = "#2a78d6", "#eb6834"
GOOD, CRIT = "#0ca30c", "#d03b3b"
INK, MUTED, SURFACE = "#1a1a1a", "#5a5a5a", "#fcfcfb"
FAINT, WARM, ALERT, MINT = "#eef2f7", "#fff6f0", "#fdeaea", "#eefaee"
plt.rcParams.update({"font.size": 8, "text.color": INK, "pdf.fonttype": 42,
                     "figure.facecolor": SURFACE, "savefig.facecolor": SURFACE})

FIG_W = 7.2
UNIT_PT = (FIG_W * 72) / 100.0          # points per x-unit
CHAR_W = 0.72                            # DejaVu Sans, measured conservative
LINE_H = 1.95                            # line spacing multiplier

def chars(units, pt):   return max(6, int(units * UNIT_PT / (pt * CHAR_W)))
def line_u(pt):         return pt * LINE_H / UNIT_PT      # one line, in y-units

def blank(w, h):
    fig, ax = plt.subplots(figsize=(w, h))
    ax.set_xlim(0, 100); ax.set_ylim(0, 100); ax.axis("off")
    ax.set_facecolor(SURFACE)
    return fig, ax

def rect(ax, x, y, w, h, fc=FAINT, ec=BLUE, lw=1.0, ls="-", z=2):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=1.6",
                                fc=fc, ec=ec, lw=lw, zorder=z, linestyle=ls))

def panel(ax, x, y, w, h, lines, fc=FAINT, ec=BLUE, lw=1.0, ls="-",
          pad=2.2, centre=False, gap=1.1):
    """Draw a box and stack `lines` from its top. lines: (text, pt, colour, bold, italic)."""
    rect(ax, x, y, w, h, fc, ec, lw, ls)
    inner = w - 2 * pad
    cur = y + h - pad
    for text, pt, col, bold, it in lines:
        wrapped = textwrap.wrap(text, chars(inner, pt)) or [""]
        for ln in wrapped:
            cur -= line_u(pt) / 2
            ax.text(x + (w / 2 if centre else pad), cur, ln, fontsize=pt, color=col,
                    ha="center" if centre else "left", va="center", zorder=5,
                    fontweight="bold" if bold else "normal",
                    style="italic" if it else "normal")
            cur -= line_u(pt) / 2
        cur -= gap
    return cur                                   # bottom of the laid-out text

def T(t, pt=7.0, c=INK, b=False, i=False): return (t, pt, c, b, i)

def arrow(ax, x1, y1, x2, y2, c=MUTED, lw=1.1, style="-|>"):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle=style, mutation_scale=9,
                                 color=c, lw=lw, zorder=3, shrinkA=0, shrinkB=0))

def head(ax, title, sub):
    ax.text(4, 97, title, fontsize=9.5, fontweight="bold", va="center", color=INK)
    for k, ln in enumerate(textwrap.wrap(sub, chars(92, 7.4))):
        ax.text(4, 92.5 - k * line_u(7.4), ln, fontsize=7.4, color=MUTED, va="center")

# ============================================================ F1
fig, ax = blank(FIG_W, 5.0)
head(ax, "F1   CardioSentinel as an intelligent physical system",
     "Four layers. Each band names what runs; the line beneath it names the evidence "
     "that constrains it.")
LAY = [
    (72, "Layer 4   AGENTIC", "Evidence Agent · Explanation Agent · Research Assistant",
     "claim boundary on every output — 18 of 25 Appendix A claims machine-checked"),
    (53, "Layer 3   EVIDENCE", "AlertEvent → EvidenceRecord → EvidenceGraph",
     "35 nodes / 39 edges per alert · closed node kinds and edge relations"),
    (34, "Layer 2   EDGE RUNTIME", "StreamingInferenceSession, five pieces of causal state",
     "~61× real time on a laptop CPU · encoder 4.161 ms/window median"),
    (15, "Layer 1   SIGNAL", "StreamingPreprocessor → CausalWindowGenerator",
     "→ 146-d representation → M1L / M2-G → U1 → T2 → T1"),
]
for y, name, body, note in LAY:
    panel(ax, 4, y, 88, 15, [T(name, 8.3, BLUE, True), T(body, 7.9), T(note, 6.8, MUTED)])
for y in (29, 48, 67):
    arrow(ax, 48, y, 48, y + 5, c=BLUE, lw=1.4)
ax.text(50.5, 31.5, "evidence flows up; nothing flows back down", fontsize=6.8,
        color=MUTED, style="italic", va="center")
panel(ax, 4, 0, 88, 13,
      [T("Train / runtime equivalence audit — the bridge, and the only real unknown",
         7.4, ORANGE, True),
       T("physiology half (18-d) bit-exact, 0.000e+00 on 64 of 64 audited rows · "
         "embedding half (128-d) max 7.15e-07 = 6 ULP of float32", 6.8, MUTED)],
      fc=WARM, ec=ORANGE)
fig.savefig(OUT/"F1_ips_architecture.pdf", bbox_inches="tight")
fig.savefig(OUT/"F1_ips_architecture.png", dpi=200, bbox_inches="tight")
plt.close(fig); print("F1 written")

# ============================================================ F2
fig, ax = blank(FIG_W, 5.0)
head(ax, "F2   Partition authority and the one-way spend of evidence",
     "Every access below was taken once. None can be taken again.")
panel(ax, 4, 54, 84, 33,
      [T("TRAIN — 56 subjects · 44 evaluable · 132 streams", 8.3, BLUE, True),
       T("the only partition a future experiment may use", 7.0, MUTED)])
panel(ax, 8, 57, 76, 21,
      [T("E11 prospective 3-fold subject-disjoint split · folds 19 / 19 / 18", 7.1),
       T("digest ce037309cc…206c3", 7.1),
       T("held-out geometry population — 44 subjects / 79 streams", 7.1)],
      fc=WARM, ec=ORANGE)
panel(ax, 11, 58.5, 60, 6,
      [T("CONSUMED 2026-08-28 (E13a) for confirmatory geometry", 7.0, CRIT, True)],
      fc=ALERT, ec=CRIT, pad=1.8)
panel(ax, 4, 35, 84, 16,
      [T("VALIDATION — 12 subjects · 9 with positives", 8.3, CRIT, True),
       T("SPENT for confirmatory purposes — used for hypothesis generation across "
         "E1–E10; may not serve as fresh confirmation.", 6.9, MUTED)],
      fc=ALERT, ec=CRIT, lw=1.2)
panel(ax, 4, 17, 84, 16,
      [T("TEST (sealed) — CONSUMED 2026-08-25, attempt 1 of 1", 8.3, CRIT, True),
       T("repeat_attempt_permitted: false · four sealed artifacts immutable · "
         "the fifteenth and last budget", 6.9, MUTED)],
      fc=ALERT, ec=CRIT, lw=1.6)
panel(ax, 4, 0, 84, 15,
      [T("All fifteen one-shot budgets are spent.", 8.0, INK, True),
       T("A spent AUTHORIZED flag is a receipt for an access already taken, not a live "
         "permission. Every future run needs a fresh human authorization.", 6.8, MUTED)],
      fc=FAINT, ec=MUTED, ls=(0, (4, 3)))
arrow(ax, 92, 86, 92, 3, c=CRIT, lw=1.3)
ax.text(96, 45, "one-way", fontsize=6.9, color=CRIT, style="italic",
        ha="center", va="center", rotation=90)
fig.savefig(OUT/"F2_partition_authority.pdf", bbox_inches="tight")
fig.savefig(OUT/"F2_partition_authority.png", dpi=200, bbox_inches="tight")
plt.close(fig); print("F2 written")

# ============================================================ F5
fig, ax = blank(FIG_W, 4.6)
head(ax, "F5   A fluent generation that three gates passed and the fourth refused",
     "One evaluated context. Qwen3-1.7B and Qwen3-4B-Instruct-2507, greedy, CPU. "
     "A demonstrated failure mode — not a failure rate.")
panel(ax, 3, 62, 19, 20,
      [T("generation", 8.0, BLUE, True), T("local Qwen", 6.9, MUTED),
       T("latency", 6.9, MUTED), T("63.4014 s", 6.9, MUTED)],
      centre=True, pad=1.6, gap=0.2)
for x, name, val in ((26, "evidence fidelity", "1.000"), (43.5, "claim violations", "0"),
                     (61, "completeness", "1.000")):
    panel(ax, x, 62, 15.5, 20,
          [T(name, 6.6), T(val, 9.0, INK, True), T("PASS", 7.0, GOOD, True)],
          fc=MINT, ec=GOOD, centre=True, pad=1.0)
for x1, x2 in ((22, 26), (41.5, 43.5), (59, 61), (76.5, 78)):
    arrow(ax, x1, 72, x2, 72, c=MUTED, lw=1.2)
panel(ax, 78, 62, 19, 20,
      [T("runtime gate", 6.9), T("REFUSED", 8.5, CRIT, True),
       T("mode →", 6.4, CRIT), T("DETERMINISTIC", 6.4, CRIT)],
      fc=ALERT, ec=CRIT, lw=1.8, centre=True, pad=1.4, gap=0.2)
panel(ax, 3, 31, 94, 25,
      [T("What the fourth gate caught", 8.1, CRIT, True)], fc=SURFACE, ec=CRIT, lw=1.1)
ax.text(6, 45, "the generation asserted", fontsize=6.9, color=MUTED, va="center")
ax.text(6, 40.5, "“the G1–G6 range passed”", fontsize=8.1, color=INK, style="italic", va="center")
ax.text(55, 45, "the evidence records", fontsize=6.9, color=MUTED, va="center")
ax.text(55, 40.5, "G4 and G5  BLOCKED", fontsize=8.1, color=CRIT, fontweight="bold", va="center")
arrow(ax, 46, 41, 53, 41, c=CRIT, lw=1.2, style="<|-|>")
for k, ln in enumerate(textwrap.wrap(
        "It rounded correctly, ended with the canonical disclaimer and invented no number "
        "— and inverted the fact the contamination control exists to communicate.",
        chars(82, 6.8))):
    ax.text(6, 36 - k * line_u(6.8), ln, fontsize=6.8, color=MUTED, va="center")
panel(ax, 3, 2, 94, 25,
      [T("Two properties that must be stated together", 8.0, INK, True),
       T("•  The harness calls provider.generate() directly, so no runtime gate runs during "
         "evaluation: the three PASS scores describe raw model output, not what a user "
         "receives.", 6.8, MUTED),
       T("•  The inversion reproduced on two independent runs, before and after the "
         "reasoning-mode fix, on the same context.", 6.8, MUTED)],
      fc=FAINT, ec=MUTED, ls=(0, (4, 3)))
fig.savefig(OUT/"F5_guarded_generation.pdf", bbox_inches="tight")
fig.savefig(OUT/"F5_guarded_generation.png", dpi=200, bbox_inches="tight")
plt.close(fig); print("F5 written")
