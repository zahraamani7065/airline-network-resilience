"""Figures for the revised paper, drawn only from verified audit outputs."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import pandas as pd
from matplotlib.patches import Patch
from matplotlib.lines import Line2D

from audit_common import AIRLINES, FIG, OUT, nulls, observed, rank_desc, removal_count

BLUE, ORANGE, AQUA, VIOLET, YELLOW, RED = "#2a78d6", "#eb6834", "#1baf7a", "#6250d6", "#eda100", "#e34948"
INK, INK2, MUTED, GRID = "#0b0b0b", "#52514e", "#8a8984", "#e6e5e1"
plt.rcParams.update({"font.family": "Arial", "font.size": 8.5, "axes.edgecolor": INK2, "axes.labelcolor": INK, "xtick.color": INK2,
                     "ytick.color": INK2, "axes.linewidth": 0.6, "xtick.major.width": 0.6, "ytick.major.width": 0.6,
                     "axes.spines.top": False, "axes.spines.right": False, "legend.frameon": False, "savefig.dpi": 300,
                     "axes.titlesize": 9.5, "axes.titleweight": "bold"})
W = 6.3  # text width in inches (A4, 2.5 cm margins)
curves = dict(np.load(OUT / "a06_observed_curves.npz"))


def grid(ax, axis="y"):
    ax.grid(axis=axis, color=GRID, linewidth=0.6)
    ax.set_axisbelow(True)


# ---------- Figure 1: full-resolution efficiency retention curves ----------
fig, axes = plt.subplots(1, 3, figsize=(W, 2.45), sharey=True)
for ax, a in zip(axes, AIRLINES):
    n = len(observed(a)[0])
    x = np.arange(n + 1) / n * 100
    rc = curves[f"{a}|Random"]
    ret = rc[:, :, 0] / rc[:, :1, 0]
    ax.fill_between(x, np.percentile(ret, 2.5, 0), np.percentile(ret, 97.5, 0), color=AQUA, alpha=0.22, linewidth=0)
    ax.plot(x, np.median(ret, 0), color=AQUA, lw=1.6)
    for key, col, ls in [("Betweenness (static)", ORANGE, (0, (4, 2))), ("Degree (static)", BLUE, "-")]:
        c = curves[f"{a}|{key}"]
        ax.plot(x, c[:, 0] / c[0, 0], color=col, lw=1.6, ls=ls, drawstyle="steps-post")
    ax.axhline(0.5, color=MUTED, lw=0.6, ls=":")
    ax.set_xlim(0, 25); ax.set_ylim(0, 1.02)
    ax.set_xticks([0, 5, 10, 15, 20, 25])
    ax.set_title(f"{a}  (N = {n})", loc="left")
    ax.set_xlabel("Airports removed (%)")
    grid(ax)
axes[0].set_ylabel("Efficiency retention")
fig.legend(handles=[Line2D([], [], color=BLUE, lw=1.6, label="Degree targeting"),
                    Line2D([], [], color=ORANGE, lw=1.6, ls=(0, (4, 2)), label="Betweenness targeting"),
                    Line2D([], [], color=AQUA, lw=1.6, label="Random removal (median)"),
                    Patch(color=AQUA, alpha=0.22, label="Random 2.5–97.5%")],
           loc="lower center", ncol=4, bbox_to_anchor=(0.5, -0.02), fontsize=8)
fig.tight_layout(rect=(0, 0.1, 1, 1))
fig.savefig(FIG / "fig1_retention_curves.png"); plt.close(fig)

# ---------- Figure 2: airports cut off as the top hubs are removed ----------
fig, ax = plt.subplots(figsize=(3.4, 2.5))
marks = {"AA": ("o", INK), "DL": ("s", INK2), "WN": ("^", MUTED)}
for a in AIRLINES:
    ids, s, t, _, _ = observed(a)
    n = len(ids)
    U = nx.Graph(); U.add_nodes_from(range(n)); U.add_edges_from(zip(s.tolist(), t.tolist()))
    order = rank_desc(np.bincount(s, minlength=n) + np.bincount(t, minlength=n), ids)
    ks = np.arange(0, 13)
    iso = []
    for k in ks:
        H = U.subgraph([i for i in range(n) if i not in set(order[:k].tolist())])
        iso.append(sum(1 for i in H.nodes if H.degree(i) == 0) / n * 100)
    m, col = marks[a]
    ax.plot(ks, iso, marker=m, color=col, ms=4, lw=1.2)
    ax.annotate(a, (ks[-1], iso[-1]), xytext=(4, 0), textcoords="offset points", va="center", fontsize=8.5, color=INK, fontweight="bold")
ax.set_xlabel("Highest-degree airports removed")
ax.set_ylabel("Airports left with no route (%)")
ax.set_xlim(0, 13.5); ax.set_ylim(0, 100)
ax.set_xticks(range(0, 13, 2))
grid(ax)
fig.tight_layout()
fig.savefig(FIG / "fig2_isolated_airports.png"); plt.close(fig)

# ---------- Figure 3: H2 decision cells ----------
cells = pd.read_csv(OUT / "a05_h2_cells.csv")
dec = cells[cells["Measure"].isin(["Efficiency retention", "Reachability", "Largest SCC"])]
rows = [(a, s) for a in AIRLINES for s in ["Degree", "Betweenness", "Random"]]
cols = [(m, l) for m in ["Efficiency retention", "Reachability", "Largest SCC"] for l in [5, 10, 15, 20]]
fill = {"within": "#f0efec", "above": "#86b6ef", "below": "#f1a09f"}
fig, ax = plt.subplots(figsize=(W, 3.1))
for i, (a, s) in enumerate(rows):
    for j, (m, l) in enumerate(cols):
        r = dec[(dec["Airline"] == a) & (dec["Strategy"] == s) & (dec["Measure"] == m) & (dec["Level"] == l)].iloc[0]
        ax.add_patch(plt.Rectangle((j + 0.04, i + 0.04), 0.92, 0.92, facecolor=fill[r["Position"]], edgecolor="none"))
        if r["Width"] <= 0.001:
            ax.add_patch(plt.Rectangle((j + 0.04, i + 0.04), 0.92, 0.92, facecolor="none", edgecolor=MUTED, hatch="////", linewidth=0))
        sym = {"above": "+", "below": "−", "within": ""}[r["Position"]]
        if sym:
            ax.text(j + 0.5, i + 0.5, sym, ha="center", va="center", fontsize=10, color=INK, fontweight="bold")
ax.set_xlim(0, 12); ax.set_ylim(9, 0)
ax.set_xticks(np.arange(12) + 0.5, [f"{l}%" for _, l in cols], fontsize=7.5)
ax.set_yticks(np.arange(9) + 0.5, [f"{a} · {s}" for a, s in rows], fontsize=7.5)
for j, m in enumerate(["Efficiency retention", "Reachability", "Largest SCC"]):
    ax.text(4 * j + 2, -0.35, m, ha="center", va="bottom", fontsize=8.5, fontweight="bold", color=INK)
for k in [4, 8]:
    ax.axvline(k, color="white", lw=3)
for k in [3, 6]:
    ax.axhline(k, color="white", lw=3)
ax.tick_params(length=0)
for sp in ax.spines.values():
    sp.set_visible(False)
fig.legend(handles=[Patch(facecolor=fill["below"], label="Below null interval (−)"), Patch(facecolor=fill["within"], label="Within interval"),
                    Patch(facecolor=fill["above"], label="Above null interval (+)"),
                    Patch(facecolor="white", edgecolor=MUTED, hatch="////", label="Interval width ≤ 0.001")],
           loc="lower center", ncol=4, fontsize=7.8, bbox_to_anchor=(0.5, -0.01))
fig.tight_layout(rect=(0, 0.07, 1, 0.97))
fig.savefig(FIG / "fig3_h2_cells.png"); plt.close(fig)

# ---------- Figure 4: single-airport loss vs degree ----------
sa = pd.read_csv(OUT / "a03_single_airport.csv")
part = pd.read_csv(OUT.parent.parent / "02_Optional_Reproducible_Project" / "Results" / "Tables" / "07_single_airport_outcomes.csv")[["Airline", "AirportID", "Participation mean"]]
sa = sa.merge(part, on=["Airline", "AirportID"])
fig, axes = plt.subplots(1, 3, figsize=(W, 2.5), sharey=True)
for ax, a in zip(axes, AIRLINES):
    g = sa[(sa["Airline"] == a) & (sa["Degree"] >= 2)]
    sc = ax.scatter(g["Degree"], g["Efficiency loss"], c=g["Participation mean"], cmap="Blues", vmin=-0.15, vmax=0.85, s=14,
                    edgecolors="white", linewidths=0.4)
    pos = g[g["Survivor damage"] > 1e-12]
    ax.scatter(pos["Degree"], pos["Efficiency loss"], s=30, facecolors="none", edgecolors=ORANGE, linewidths=0.9)
    for _, r in g.nlargest(2, "Survivor damage").iterrows():
        ax.annotate(r["Code"], (r["Degree"], r["Efficiency loss"]), xytext=(-4, 3), textcoords="offset points", ha="right", fontsize=7.5, color=INK)
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_title(a, loc="left")
    grid(ax, "both")
axes[0].set_ylabel("Efficiency loss after removal")
fig.supxlabel("Degree (number of connected airports, log scale)", fontsize=8.5, y=-0.04)
cb = fig.colorbar(sc, ax=axes, shrink=0.85, pad=0.015, aspect=25)
cb.set_label("Mean participation", fontsize=8); cb.ax.tick_params(labelsize=7.5)
cb.set_ticks([0, 0.2, 0.4, 0.6, 0.8]); cb.ax.set_ylim(0, 0.85)
axes[2].legend(handles=[Line2D([], [], marker="o", ls="", mfc="none", mec=ORANGE, ms=6, label="Damages other airports")],
               loc="lower right", fontsize=7.5, handletextpad=0.2)
fig.savefig(FIG / "fig4_h3_loss_degree.png", bbox_inches="tight"); plt.close(fig)

# ---------- Figure 5: Experiment B with captive airports ----------
cap = pd.read_csv(OUT / "a08_captive.csv")
fig, axes = plt.subplots(1, 3, figsize=(W, 2.35))
for ax, a in zip(axes, AIRLINES):
    n = len(observed(a)[0])
    z = np.load(OUT / f"a02_{a}_reciprocal.npz")
    frac = np.array([0] + [removal_count(n, p) / n for p in [1, 2, 5, 10, 15, 20]])
    lim = min(removal_count(len(observed(b)[0]), 2) / len(observed(b)[0]) for b in AIRLINES)
    ret = z["targeted"][:, 0, :, 0] / z["intact"][:, [0]]
    aucs = []
    for r in ret:
        y = np.r_[1, r]; m = frac < lim
        aucs.append(np.trapezoid(np.r_[y[m], np.interp(lim, frac, y)], np.r_[frac[m], lim]) / lim)
    g = cap[(cap["Airline"] == a) & (cap["Family"] == "reciprocal")].sort_values("Network")
    sc = ax.scatter(g["Assortativity"], aucs, c=g["Captive at 2%"], cmap="Blues", s=14, edgecolors="white", linewidths=0.4,
                    vmin=g["Captive at 2%"].min() - 0.3 * (np.ptp(g["Captive at 2%"]) + 1), vmax=g["Captive at 2%"].max())
    ax.set_title(a, loc="left")
    ax.set_xlabel("Degree assortativity")
    ax.ticklabel_format(axis="x", useOffset=False)
    ax.tick_params(axis="x", labelsize=7)
    for lab in ax.get_xticklabels():
        lab.set_rotation(25)
    grid(ax, "both")
    cb = fig.colorbar(sc, ax=ax, pad=0.02, aspect=18)
    cb.ax.tick_params(labelsize=7)
    lo, hi = int(g["Captive at 2%"].min()), int(g["Captive at 2%"].max())
    step = 1 if hi - lo <= 4 else 5
    cb.set_ticks(list(range(lo + (-lo) % step, hi + 1, step)))
    cb.ax.set_ylim(lo, hi)
    cb.ax.set_title("cut off", fontsize=7, color=INK2)
axes[0].set_ylabel("Early efficiency AUC")
fig.tight_layout()
fig.savefig(FIG / "fig5_expB_assortativity.png"); plt.close(fig)
print("figures written")
