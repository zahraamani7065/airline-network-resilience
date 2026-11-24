"""Audit 3: single-airport removal, participation, Louvain stability and the H3 rule."""
import networkx as nx
import numpy as np
import pandas as pd
from networkx.algorithms.community import louvain_communities, modularity
from scipy.stats import rankdata, spearmanr
from sklearn.metrics import adjusted_rand_score

from audit_common import AIRLINES, DATA, OUT, TABLES, adjacency, observed
from scipy.sparse.csgraph import shortest_path

EDGES = [2, 3, 4, 5, 7, 10, 15, 30, 60, np.inf]
R12 = lambda x: np.round(np.asarray(x, float), 12)


def inv_dist(A, keep):
    d = shortest_path(A[keep][:, keep], unweighted=True, directed=True)
    np.fill_diagonal(d, np.inf)
    out = np.zeros_like(d)
    f = np.isfinite(d)
    out[f] = 1 / d[f]
    return out


def ranks_in(train, values):
    """Mid-rank position of `values` within the training sample, scaled to (0,1]."""
    o = np.sort(R12(train))
    v = R12(values)
    return (np.searchsorted(o, v, "left") + np.searchsorted(o, v, "right")) / (2 * len(train))


def ols_r2_oob(Xtr, ytr, Xte, yte):
    Xtr = np.column_stack([np.ones(len(ytr)), Xtr])
    Xte = np.column_stack([np.ones(len(yte)), Xte])
    b = np.linalg.lstsq(Xtr, ytr, rcond=None)[0]
    return 1 - ((yte - Xte @ b) ** 2).sum() / ((yte - ytr.mean()) ** 2).sum(), b


def partial_rank(y, x, z):
    ry, rx, rz = (rankdata(R12(v)) for v in (y, x, z))
    a = spearmanr(ry, rx)[0]; b = spearmanr(ry, rz)[0]; c = spearmanr(rx, rz)[0]
    return (a - b * c) / np.sqrt((1 - b * b) * (1 - c * c))


labels_all = pd.read_csv(TABLES / "03_louvain_run_labels_binary.csv")
runs_saved = pd.read_csv(TABLES / "03_louvain_binary_runs.csv")
saved_single = pd.read_csv(TABLES / "07_single_airport_outcomes.csv")
saved_verdict = pd.read_csv(TABLES / "07_h3_verdicts.csv").set_index("Airline")
rows_single, rows_cmp, rows_louv, rows_h3, rows_bins = [], [], [], [], []

for a in AIRLINES:
    ids, s, t, w, nodes = observed(a)
    n = len(ids)
    A = adjacency(s, t, n)
    U = nx.Graph(); U.add_nodes_from(range(n)); U.add_edges_from(zip(s.tolist(), t.tolist()))
    deg = np.array([U.degree(i) for i in range(n)], float)

    # ---- single-airport removal ----
    full = inv_dist(A, np.ones(n, bool))
    E0 = full.sum() / (n * (n - 1))
    for i in range(n):
        keep = np.ones(n, bool); keep[i] = False
        aft = inv_dist(A, keep)
        rows_single.append({"Airline": a, "AirportID": ids[i], "Code": nodes.set_index("airport_id").loc[ids[i], "code"], "Degree": deg[i],
                            "Efficiency loss": E0 - aft.sum() / (n * (n - 1)),
                            "Own-pair share of loss": (full[i].sum() + full[:, i].sum()) / (n * (n - 1)),
                            "Survivor damage": (full[keep][:, keep].sum() - aft.sum()) / ((n - 1) * (n - 2))})
    single = pd.DataFrame([r for r in rows_single if r["Airline"] == a])
    sv = saved_single[saved_single["Airline"] == a].set_index("AirportID").loc[single["AirportID"]]
    rows_cmp.append({"Airline": a, "Check": "Single-airport efficiency loss", "Max abs diff": float(np.abs(sv["Efficiency loss"].to_numpy() - single["Efficiency loss"].to_numpy()).max())})
    rows_cmp.append({"Airline": a, "Check": "Survivor damage", "Max abs diff": float(np.abs(sv["Surviving-airport damage"].to_numpy() - single["Survivor damage"].to_numpy()).max())})

    # ---- participation from the saved 100 Louvain runs ----
    lab = labels_all[labels_all["Airline"] == a].set_index("AirportID").loc[ids]
    seeds = [c for c in lab.columns if c.startswith("Seed_")]
    P = np.zeros((len(seeds), n)); Q = []
    nbrs = [list(U.neighbors(i)) for i in range(n)]
    for r, col in enumerate(seeds):
        L = lab[col].to_numpy()
        for i in range(n):
            if deg[i] > 0:
                cnt = np.bincount(L[nbrs[i]])
                P[r, i] = 1 - ((cnt / deg[i]) ** 2).sum()
        comms = [set(np.flatnonzero(L == c)) for c in np.unique(L)]
        Q.append(modularity(U, comms))
    Pm = P.mean(0)
    rows_cmp.append({"Airline": a, "Check": "Mean participation", "Max abs diff": float(np.abs(sv["Participation mean"].to_numpy() - Pm).max())})
    qs = runs_saved[runs_saved["Airline"] == a].sort_values("Seed")["Modularity"].to_numpy()
    rows_cmp.append({"Airline": a, "Check": "Louvain run modularity", "Max abs diff": float(np.abs(qs - np.array(Q)).max())})

    # independent fresh Louvain runs with different seeds (stability check)
    fresh = [louvain_communities(U, resolution=1.0, seed=10_000 + k) for k in range(100)]
    fq = [modularity(U, c) for c in fresh]
    flab = []
    for c in fresh:
        L = np.zeros(n, int)
        for j, cc in enumerate(c):
            L[list(cc)] = j
        flab.append(L)
    saved_labs = [lab[c].to_numpy() for c in seeds]
    ari_saved = [adjusted_rand_score(saved_labs[i], saved_labs[j]) for i in range(100) for j in range(i + 1, 100)]
    ari_cross = [adjusted_rand_score(saved_labs[i], flab[j]) for i in range(0, 100, 5) for j in range(0, 100, 5)]
    elig = deg >= 2
    rows_louv.append({"Airline": a, "Saved best Q": max(Q), "Saved mean Q": np.mean(Q), "Fresh best Q": max(fq), "Fresh mean Q": np.mean(fq),
                      "Distinct saved partitions": len({tuple(pd.factorize(x)[0]) for x in saved_labs}),
                      "Pairwise ARI saved mean": np.mean(ari_saved), "ARI saved vs fresh mean": np.mean(ari_cross),
                      "Mean SD of participation across runs (eligible)": P[:, elig].std(0).mean(),
                      "Mean participation (eligible)": Pm[elig].mean(),
                      "Median per-airport range of participation (eligible)": np.median(P[:, elig].max(0) - P[:, elig].min(0))})

    # ---- H3 rule ----
    e = np.flatnonzero(elig)
    loss = single["Efficiency loss"].to_numpy()[e]; d = deg[e]; p = Pm[e]
    pr_full = partial_rank(loss, p, d)
    # per-run partial correlation using each single Louvain run (algorithmic sensitivity)
    pr_runs = np.array([partial_rank(loss, P[r, e], d) for r in range(len(seeds))])
    samples = np.load(DATA / "Processed" / "H3" / f"{a}_bootstrap_inbag_indices.npz")
    assert np.array_equal(samples["airport_ids"], ids[e])
    gains, partials, r2a = [], [], []
    for ib in samples["samples"]:
        m = np.ones(len(e), bool); m[ib] = False
        oob = np.flatnonzero(m)
        ytr, yte = ranks_in(loss[ib], loss[ib]), ranks_in(loss[ib], loss[oob])
        dtr, dte = ranks_in(d[ib], d[ib]), ranks_in(d[ib], d[oob])
        ptr, pte = ranks_in(p[ib], p[ib]), ranks_in(p[ib], p[oob])
        ra, _ = ols_r2_oob(dtr[:, None], ytr, dte[:, None], yte)
        rb, _ = ols_r2_oob(np.column_stack([dtr, ptr]), ytr, np.column_stack([dte, pte]), yte)
        gains.append(rb - ra); r2a.append(ra)
        Z = np.column_stack([np.ones(len(ib)), dtr])
        res_y = ytr - Z @ np.linalg.lstsq(Z, ytr, rcond=None)[0]
        res_p = ptr - Z @ np.linalg.lstsq(Z, ptr, rcond=None)[0]
        partials.append(np.corrcoef(res_y, res_p)[0, 1])
    g_lo, g_med, g_hi = np.percentile(gains, [2.5, 50, 97.5])
    p_lo, p_hi = np.percentile(partials, [2.5, 97.5])
    # degree bins
    bins = pd.cut(d, bins=EDGES, right=False)
    comp = higher = 0
    for b in bins.categories:
        idx = np.flatnonzero(bins == b)
        if len(idx) < 5:
            continue
        pp = R12(p[idx]); med = np.median(pp)
        hi, lo = idx[pp > med], idx[pp < med]
        if len(hi) and len(lo):
            comp += 1
            diff = loss[hi].mean() - loss[lo].mean()
            higher += np.round(diff, 12) > 0
            rows_bins.append({"Airline": a, "Bin": str(b), "n": len(idx), "Mean degree high P": d[hi].mean(), "Mean degree low P": d[lo].mean(), "Loss diff": diff})
    c1, c2, c3 = bool(p_lo > 0), bool((g_lo > 0) and (g_med >= 0.02)), bool(higher / comp >= 2 / 3)
    held = int(c1) + int(c2) + int(c3)
    verdict = "Supported" if held == 3 else ("Partly supported" if held >= 1 and not p_hi < 0 else ("Not supported" if held == 0 else "Mixed"))
    sv_v = saved_verdict.loc[a]
    rows_h3.append({"Airline": a, "Eligible": len(e), "Partial (full)": pr_full, "Partial 2.5%": p_lo, "Partial 97.5%": p_hi,
                    "Median Gain": g_med, "Gain 2.5%": g_lo, "Gain 97.5%": g_hi, "Degree-only median R2": np.median(r2a),
                    "Bins higher/comparable": f"{higher}/{comp}", "Conditions met": held, "Audit verdict": verdict,
                    "Project verdict": sv_v["H3 verdict"],
                    "Diff partial": pr_full - sv_v["Partial rank correlation (full sample)"], "Diff median Gain": g_med - sv_v["Median Gain"],
                    "Per-run partial: min": pr_runs.min(), "Per-run partial: median": np.median(pr_runs), "Per-run partial: max": pr_runs.max(),
                    "Spearman(degree, loss)": spearmanr(d, loss)[0], "Spearman(participation, loss)": spearmanr(p, loss)[0],
                    "Spearman(degree, participation)": spearmanr(d, p)[0]})

single_all = pd.DataFrame(rows_single)
single_all.to_csv(OUT / "a03_single_airport.csv", index=False)
surv = single_all.groupby("Airline").apply(lambda g: pd.Series({
    "Airports": len(g), "Survivor damage > 1e-12": int((g["Survivor damage"] > 1e-12).sum()),
    "Share of summed loss from own pairs": g["Own-pair share of loss"].sum() / g["Efficiency loss"].sum(),
    "Top airport": g.loc[g["Efficiency loss"].idxmax(), "Code"],
    "Top absolute efficiency loss": g["Efficiency loss"].max(),
    "Top-3 survivor damage share of all survivor damage": np.sort(g["Survivor damage"])[::-1][:3].sum() / g["Survivor damage"].sum()}))
surv.to_csv(OUT / "a03_survivor_summary.csv")
for name, rows in [("a03_checks", rows_cmp), ("a03_louvain_stability", rows_louv), ("a03_h3_recomputed", rows_h3), ("a03_bins", rows_bins)]:
    pd.DataFrame(rows).to_csv(OUT / f"{name}.csv", index=False)
pd.set_option("display.width", 250, "display.max_columns", None)
print(pd.DataFrame(rows_cmp).to_string())
print(pd.DataFrame(rows_louv).T.to_string())
print(pd.DataFrame(rows_h3).T.to_string())
print(surv.T.to_string())
print(pd.DataFrame(rows_bins).to_string())
