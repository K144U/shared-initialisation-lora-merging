#!/usr/bin/env python3
"""Three figures added on 2026-11-12, kept apart from make_figures.py so that
rebuilding them does not regenerate the six data figures.

  fig0_concept.pdf  the mechanism in one picture (Introduction)
  fig_wudi.pdf      the lead result: WUDI-Merging as published (Section 6.2)
  fig_decision.pdf  what to do before a merge (Section 7); states the rule,
                    so it draws no measured number

Same style, palette and column width as make_figures.py, whose module-level
setup this imports. Every number drawn or printed is read from a result file.
The exceptions are the two panels marked as illustrations in the caption:
panel (a), small random matrices drawn with a fixed seed to show what "one
draw" means, and panel (b), a two-dimensional sketch of the subspaces.

    python paper/nc/make_concept_figures.py
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import numpy as np  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.gridspec import GridSpec  # noqa: E402

from make_figures import (  # noqa: E402
    BASES, BL, BLUE, CAMP, DATA, FAINT, INK, INK2, ORANGE, RES, WIDE,
    lab, load, save, title,
)

CAMP10 = RES / "campaign_2026-10"


def fmt_pow(x: float) -> str:
    ex = int(np.floor(np.log10(x)))
    return f"{x / 10 ** ex:.1f}\\times10^{{{ex}}}"


# --------------------------------------------------------------------------
# The mechanism in one picture.
# --------------------------------------------------------------------------
def fig_concept():
    G = load(DATA / "geometry_stats.json")["data"]
    geo = load(RES / "geometry_T4_vs_T3.json")
    drift = load(RES / "drift_summary.json")["arms"]
    wudi = load(CAMP10 / "wudi_summary.json")["acc"]
    heur = load(CAMP / "heur_tost_summary.json")["equivalence"]

    base = "llama31_8b"
    cos = {"sh": geo["shared | T=4"][base]["median_principal_cosine"],
           "in": geo["independent | T=4"][base]["median_principal_cosine"]}
    moved = 100 * np.mean([drift["drift_shared"]["drift_final"],
                           drift["drift_indep"]["drift_final"]])
    # The layer with the median condition number of the eight sampled, as in
    # the theory figure, so the two figures show the same layer.
    sh, ind = G[f"{base}/seed1"], G[f"{base}/indep1"]
    kap = [l[0] / l[-1] for l in sh["eig"]]
    li = int(np.argsort(kap)[len(kap) // 2])
    eig = {"sh": np.array(sh["eig"][li]), "in": np.array(ind["eig"][li])}
    acc = {
        "sh": (np.mean(heur["task_arithmetic/gsm8k"]["per_base"][base]["shared"]),
               np.mean(wudi[f"{base}/wudi_pub/gsm8k"]["shared"])),
        "in": (np.mean(heur["task_arithmetic/gsm8k"]["per_base"][base]["indep"]),
               np.mean(wudi[f"{base}/wudi_pub/gsm8k"]["indep"])),
    }

    fig = plt.figure(figsize=(WIDE, 3.35))
    gs = GridSpec(2, 4, figure=fig, width_ratios=[1.0, 0.8, 1.0, 1.0],
                  wspace=0.5, hspace=0.62, left=0.135, right=0.985,
                  top=0.83, bottom=0.11)
    rows = [("sh", ORANGE, "^", "one seed for\nall four tasks"),
            ("in", BLUE, "o", "a different\nseed per task")]
    titles = ["At creation:\n$B = 0$, $A$ drawn at random",
              f"After training:\n$A$ has moved {moved:.0f}%",
              "What a solver built\nfrom the adapters inverts",
              "Merged model,\nLlama-3.1-8B"]

    for i, (arm, col, mk, rowlab) in enumerate(rows):
        top = i == 0
        y_mid = 0.83 - (i + 0.5) * (0.83 - 0.11) / 2
        fig.text(0.004, y_mid, rowlab, color=col, fontweight="bold",
                 fontsize=7.8, va="center", ha="left")

        # (a) At creation: four A factors from one draw, or from four. An
        # illustration: small matrices drawn with a fixed seed.
        a = fig.add_subplot(gs[i, 0])
        r, d, gap = 6, 5, 1.6
        cmap = plt.get_cmap("Greys")
        for t in range(4):
            rng = np.random.default_rng(7 if arm == "sh" else 101 + t)
            x0 = t * (d + gap)
            a.imshow(rng.uniform(-1, 1, (r, d)), cmap=cmap, vmin=-1.4, vmax=1.4,
                     extent=(x0, x0 + d, 0, r), interpolation="nearest")
            a.text(x0 + d / 2, -0.5, f"$A_{t + 1}$", ha="center", va="top",
                   fontsize=7, color=INK)
        a.set_xlim(-0.3, 4 * d + 3 * gap + 0.3), a.set_ylim(-2.6, r + 0.3)
        a.set_aspect("auto"), a.axis("off")
        a.text(0.5, 0.0, "identical" if arm == "sh" else "all different",
               transform=a.transAxes, ha="center", va="top", fontsize=6.8,
               color=col, fontweight="bold")

        # (b) After training: the four input subspaces, sketched in 2-D as
        # lines through the origin (a subspace is a line, not an arrow).
        b = fig.add_subplot(gs[i, 1])
        angs = [55, 59, 63, 67] if arm == "sh" else [10, 55, 100, 145]
        for ang in angs:
            x, y = np.cos(np.radians(ang)), np.sin(np.radians(ang))
            b.plot([-x, x], [-y, y], color=col, lw=1.2, solid_capstyle="round")
        b.plot(0, 0, "o", color=INK, ms=2)
        b.set_xlim(-1.05, 1.05), b.set_ylim(-1.05, 1.05)
        b.set_aspect("equal"), b.axis("off")
        b.text(0.5, -0.08, f"median cosine\n{cos[arm]:.3f}",
               transform=b.transAxes, ha="center", va="top", fontsize=6.8,
               color=col, fontweight="bold", linespacing=1.0)

        # (c) What a solver built from the adapters has to invert.
        c = fig.add_subplot(gs[i, 2])
        k = np.arange(1, 65)
        c.semilogy(k, eig[arm], color=col, marker=mk, ls="none", ms=2.2)
        c.set_ylim(min(eig["sh"].min(), eig["in"].min()) / 4, 4)
        c.set_xlim(-2, 67)
        c.set_xticks([1, 16, 32, 48, 64])
        c.tick_params(labelsize=6.3)
        c.set_ylabel(r"eigenvalue of $\bar H$", fontsize=6.8, labelpad=1)
        if not top:
            c.set_xlabel("eigenvalue index", fontsize=6.8)
        kv = eig[arm][0] / eig[arm][-1]
        ktxt = f"$\\kappa = {fmt_pow(kv)}$" if kv >= 100 else f"$\\kappa = {kv:.1f}$"
        c.text(0.97, 0.93 if arm == "sh" else 0.08, ktxt, transform=c.transAxes,
               ha="right", va="top" if arm == "sh" else "bottom",
               fontsize=6.8, color=col, fontweight="bold")

        # (d) The merged model: names written above the bars, not as tick
        # labels, so they never run into panel (c).
        e = fig.add_subplot(gs[i, 3])
        names = ["averaging (task arithmetic)", "solver from the adapters (WUDI)"]
        vals = acc[arm]
        ys = [1, 0]
        e.barh(ys, vals, height=0.42, color=col, alpha=0.9)
        for yv, v, n in zip(ys, vals, names):
            e.text(0.0, yv + 0.27, n, va="bottom", ha="left", fontsize=6.3, color=INK)
            e.text(v + 0.03, yv, f"{v:.2f}", va="center", ha="left",
                   fontsize=6.8, color=INK, fontweight="bold")
        e.set_yticks([])
        e.set_xlim(0, 1.0)
        e.set_ylim(-0.45, 1.75)
        e.tick_params(axis="x", labelsize=6.3)
        e.grid(axis="y", visible=False)
        e.spines["left"].set_visible(False)
        if not top:
            e.set_xlabel("GSM8K accuracy", fontsize=6.8)

        if top:
            heads = []
            for ax, t in zip((a, b, c, e), titles):
                heads.append(ax.text(0.0, 1.05, t, transform=ax.transAxes,
                                     ha="left", va="bottom", fontsize=7.8,
                                     color=INK, linespacing=1.15))

    # Panel letters level with the FIRST line of each two-line title (the
    # usual lab() sits at the axes top, which is the second line here).
    fig.canvas.draw()
    rend = fig.canvas.get_renderer()
    for ax, head, letter in zip(fig.axes[:4], heads, "abcd"):
        bb = head.get_window_extent(rend)
        _, y1 = ax.transAxes.inverted().transform((bb.x0, bb.y1))
        ax.text(-0.04, y1, letter, transform=ax.transAxes, fontweight="bold",
                fontsize=8.5, color=INK, va="top", ha="right")

    save(fig, "fig0_concept")
    print(f"  concept: cos {cos['sh']:.4f}/{cos['in']:.4f}, moved {moved:.2f}%, "
          f"kappa {eig['sh'][0] / eig['sh'][-1]:.3g}/{eig['in'][0] / eig['in'][-1]:.3g}, "
          f"TA {acc['sh'][0]:.3f}/{acc['in'][0]:.3f}, WUDI {acc['sh'][1]:.3f}/{acc['in'][1]:.3f}")


# --------------------------------------------------------------------------
# The lead result: WUDI-Merging as published, per base and benchmark.
# --------------------------------------------------------------------------
def fig_wudi():
    wudi = load(CAMP10 / "wudi_summary.json")["acc"]
    heur = load(CAMP / "heur_tost_summary.json")["equivalence"]
    fig, axes = plt.subplots(1, 2, figsize=(WIDE, 1.95), sharey=True)
    ys = np.arange(len(BASES))[::-1]
    for ax, bench, name in zip(axes, ("gsm8k", "humaneval"), ("GSM8K", "HumanEval")):
        for y, b in zip(ys, BASES):
            w = wudi[f"{b}/wudi_pub/{bench}"]
            ta = heur[f"task_arithmetic/{bench}"]["per_base"][b]
            ms, mi = np.mean(w["shared"]), np.mean(w["indep"])
            ax.plot([ms, mi], [y, y], color=FAINT, lw=2.4, zorder=1,
                    solid_capstyle="round")
            ax.scatter(w["indep"], [y + 0.13] * 3, s=6, color=BLUE, alpha=0.45,
                       lw=0, zorder=2)
            ax.scatter(w["shared"], [y - 0.13] * 3, s=6, color=ORANGE, alpha=0.45,
                       lw=0, zorder=2)
            ax.scatter([mi], [y], s=30, color=BLUE, marker="o", zorder=3,
                       label="WUDI, a different seed per task" if y == ys[0] else None)
            ax.scatter([ms], [y], s=34, color=ORANGE, marker="^", zorder=3,
                       label="WUDI, one seed for all tasks" if y == ys[0] else None)
            tam = np.mean(ta["shared"] + ta["indep"])
            ax.scatter([tam], [y], s=26, facecolor="none", edgecolor=INK2,
                       marker="D", lw=0.8, zorder=3,
                       label="task arithmetic, same adapters" if y == ys[0] else None)
            if not w.get("harm", True):
                ax.text((ms + mi) / 2, y - 0.3, "difference within noise",
                        fontsize=5.8, color=INK2, va="top", ha="center")
        ax.set_xlim(-0.02, 0.86)
        ax.set_ylim(-0.6, len(BASES) - 0.4)
        ax.set_yticks(ys)
        ax.set_yticklabels([BL[b] for b in BASES])
        ax.grid(axis="y", visible=False)
        ax.set_xlabel(f"{name} accuracy")
        title(ax, name)
    lab(axes[0], "a", x=-0.27)
    lab(axes[1], "b")
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper center", ncol=3, bbox_to_anchor=(0.55, 1.1),
               fontsize=6.8, handletextpad=0.3, columnspacing=1.4)
    fig.subplots_adjust(wspace=0.08)
    save(fig, "fig_wudi")


def fig_decision():
    """What to do before a merge: the three cases of Section 7 as a flowchart.

    Every statement in it is one the text makes; the threshold is
    Algorithm 1's c_hi. No number is read from a result file, because the
    figure states the rule, not a measurement.
    """
    from matplotlib.patches import FancyBboxPatch

    GREEN = "#1baf7a"
    fig = plt.figure(figsize=(WIDE, 2.75))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    def box(cx, cy, w, h, head, body, edge=INK2, fill="#f4f3ef", hs=7.1, bs=6.5):
        ax.add_patch(FancyBboxPatch((cx - w / 2, cy - h / 2), w, h,
                                    boxstyle="round,pad=0.004,rounding_size=0.012",
                                    lw=1.0, edgecolor=edge, facecolor=fill, zorder=1))
        if head:
            ax.text(cx, cy + h / 2 - 0.035, head, ha="center", va="top", fontsize=hs,
                    fontweight="bold", color=INK, zorder=2)
        if body:
            y = cy - 0.035 if head else cy
            ax.text(cx, y, body, ha="center", va="center", fontsize=bs, color=INK,
                    linespacing=1.3, zorder=2)

    def arrow(x0, y0, x1, y1, text=None, tx=None, ty=None, ha="center"):
        ax.annotate("", xy=(x1, y1), xytext=(x0, y0),
                    arrowprops=dict(arrowstyle="-|>", color=INK2, lw=0.9,
                                    shrinkA=0, shrinkB=0, mutation_scale=8))
        if text:
            ax.text(tx, ty, text, ha=ha, va="center", fontsize=6.6, color=INK,
                    fontweight="bold")

    # main row
    box(0.078, 0.70, 0.142, 0.24, None, "$T$ LoRA\nadapters on\none base model")
    box(0.300, 0.70, 0.235, 0.40, "Which merge?",
        "Does it solve a least-squares\nproblem whose matrix is built\nfrom the adapters alone?\n"
        "(adapter-only RegMean,\nWUDI-Merging, our encoder)")
    box(0.560, 0.70, 0.205, 0.40, "Run the audit (Alg. 1)",
        "reads only the $A$ factors,\nabout one CPU minute,\nno data, no forward pass\n\n"
        "$c^\\star$ = largest pairwise\nmedian principal cosine")
    box(0.840, 0.835, 0.30, 0.29, "Collapsed: $c^\\star > 0.9$",
        "closed-form solver: add a ridge, start\nnear $\\lambda = 0.01$, sweep it on held-out data\n"
        "WUDI as published: use an\nunaffected merge instead",
        edge=ORANGE, fill="#fdebe3")
    box(0.840, 0.47, 0.30, 0.27, "Otherwise",
        "the solver works on our separated\ncohorts; on public adapters it also\n"
        "fails for other reasons, so check\nthe merged model",
        edge=BLUE, fill="#e4eefa")
    # lower row
    box(0.300, 0.20, 0.36, 0.27, "No: the initialisation does not matter",
        "task arithmetic, TIES, DARE, TVQ, KnOTS;\nRegMean with activation Grams, MaTS;\n"
        "diagonal Fisher; TSV-M",
        edge=GREEN, fill="#e2f5ee")
    box(0.745, 0.165, 0.49, 0.27, "Where collapsed cohorts come from",
        "one global seed for every task  $\\cdot$  Unsloth or LLaMA-Factory defaults\n"
        "PiSSA, OLoRA or MiLoRA initialisation  $\\cdot$  every task trained on\n"
        "from one adapter  $\\cdot$  designs that share $A$ on purpose",
        edge=FAINT, fill="#f7f6f2", bs=6.3)

    arrow(0.149, 0.70, 0.1825, 0.70)
    arrow(0.4175, 0.70, 0.4575, 0.70, "yes", 0.4375, 0.735)
    arrow(0.300, 0.50, 0.300, 0.335, "no", 0.315, 0.42, ha="left")
    arrow(0.6625, 0.76, 0.690, 0.835)
    arrow(0.6625, 0.64, 0.690, 0.47)
    save(fig, "fig_decision")


if __name__ == "__main__":
    fig_concept()
    fig_wudi()
    fig_decision()
    print("wrote fig0_concept.pdf, fig_wudi.pdf")
