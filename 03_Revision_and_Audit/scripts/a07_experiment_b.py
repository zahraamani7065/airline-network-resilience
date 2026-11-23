"""Audit 7: recompute Experiment B (within-null structure vs resilience AUC).

Structure (clustering, transitivity, assortativity, cores) is recomputed from the saved
graphs; best Louvain modularity is reused from the project table (recomputing 100 Louvain
runs on 900 graphs is out of scope; a10-graph spot check is in a06). AUCs are rebuilt
from the audit's own removal outcomes (a02). Permutation p-values use the audit's own
seed, so they agree with the project only up to Monte Carlo error.
"""
import networkx as nx
import numpy as np
import pandas as pd
from scipy import stats

from audit_common import AIRLINES, OUT, SUPP, TABLES, nulls, observed, removal_count

PRED = ["Modularity", "Average clustering", "Transitivity", "Maximum coreness", "Mean coreness", "Innermost-core fraction", "Degree assortativity"]
LV = [1, 2, 5, 10, 15, 20]
NPERM = 19999
rng = np.random.default_rng(20261122)
mod = pd.read_csv(TABLES / "04_null_modularity_by_network.csv")

frac = {a: np.array([removal_count(len(observed(a)[0]), p) / len(observed(a)[0]) for p in LV]) for a in AIRLINES}
lim = {"Early AUC": min(frac[a][1] for a in AIRLINES), "Full AUC": min(frac[a][5] for a in AIRLINES)}


def auc(x, y, limit):
    m = x < limit
    xx = np.r_[x[m], limit]; yy = np.r_[y[m], np.interp(limit, x, y)]
    return np.trapezoid(yy, xx) / limit


def ranks(M):
    r = stats.rankdata(np.round(M, 12), axis=0); r -= r.mean(0)
    nrm = np.sqrt((r * r).sum(0))
    return np.divide(r, nrm, out=np.zeros_like(r), where=nrm > 0)


rows = []
for a in AIRLINES:
    for fam in ["reciprocal", "directed"]:
        z = np.load(OUT / f"a02_{a}_{fam}.npz")
        nets = nulls(a, fam)
        X = []
        for k, (s, t) in enumerate(nets):
            U = nx.Graph(); U.add_nodes_from(range(len(observed(a)[0]))); U.add_edges_from(zip(s.tolist(), t.tolist()))
            cv = np.array(list(nx.core_number(U).values()))
            q = mod[(mod["Airline"] == a) & (mod["Model"] == fam) & (mod["Network"] == k)]["Best modularity"].iloc[0]
            X.append([q, nx.average_clustering(U), nx.transitivity(U), cv.max(), cv.mean(), (cv == cv.max()).mean(), nx.degree_assortativity_coefficient(U)])
        X = np.array(X)
        cols, Y = [], []
        x = np.r_[0, frac[a]]
        for si, st in enumerate(["Degree", "Betweenness", "Random"]):
            v = z["targeted"][:, si] if si < 2 else z["random"].mean(1)        # nets x levels x metrics
            ret = np.stack([v[:, :, 0] / z["intact"][:, [0]], v[:, :, 1] / z["intact"][:, [1]], v[:, :, 2] / z["intact"][:, [2]]], -1)
            for mi, met in enumerate(["Efficiency retention", "Reachability retention", "Largest SCC retention"]):
                for win, L in lim.items():
                    Y.append([auc(x, np.r_[1, ret[j, :, mi]], L) for j in range(len(nets))])
                    cols.append((st, met, win))
        Y = np.array(Y).T
        usable_x = np.ptp(np.round(X, 12), 0) > 0
        usable_y = np.ptp(np.round(Y, 12), 0) > 0
        xr, yr = ranks(X), ranks(Y)
        rho = xr.T @ yr
        ext = np.zeros(rho.shape, int)
        for off in range(0, NPERM, 500):
            P = np.array([rng.permutation(len(X)) for _ in range(min(500, NPERM - off))])
            ext += (np.abs(np.transpose(xr[P], (0, 2, 1)) @ yr) >= np.abs(rho)[None] - 1e-14).sum(0)
        p = (1 + ext) / (NPERM + 1)
        for i, pr in enumerate(PRED):
            for j, c in enumerate(cols):
                ok = usable_x[i] and usable_y[j]
                rows.append({"Airline": a, "Null model": fam, "Predictor": pr, "Strategy": c[0], "Metric": c[1], "Window": c[2],
                             "Spearman rho": rho[i, j] if ok else np.nan, "Permutation p": p[i, j] if ok else np.nan,
                             "Predictor min": X[:, i].min(), "Predictor max": X[:, i].max()})
        print(a, fam, flush=True)

res = pd.DataFrame(rows)
res["BY q"] = np.nan
for fam in ["reciprocal", "directed"]:
    m = (res["Null model"] == fam) & res["Permutation p"].notna()
    res.loc[m, "BY q"] = stats.false_discovery_control(res.loc[m, "Permutation p"], method="by")
saved = pd.read_csv(SUPP / "Tables" / "09_auc_associations.csv")
key = ["Airline", "Null model", "Predictor", "Strategy", "Metric", "Window"]
mm = res.merge(saved[key + ["Spearman rho", "BY q"]], on=key, suffixes=("", " (project)"))
res.to_csv(OUT / "a07_experiment_b.csv", index=False)
summary = {
    "Tests per family": res.groupby("Null model").size().to_dict(),
    "Max |rho audit - project|": float(np.nanmax(np.abs(mm["Spearman rho"] - mm["Spearman rho (project)"]))),
    "Significant (q<0.05) audit": res[res["BY q"] < 0.05].groupby("Null model").size().to_dict(),
    "Significant (q<0.05) project": saved[saved["BY q"] < 0.05].groupby("Null model").size().to_dict(),
    "Agreement of significance calls": float(((mm["BY q"] < 0.05) == (mm["BY q (project)"] < 0.05)).mean()),
    "Reciprocal significant predictors (audit)": res[(res["BY q"] < 0.05) & (res["Null model"] == "reciprocal")]["Predictor"].value_counts().to_dict(),
    "Directed significant predictors (audit)": res[(res["BY q"] < 0.05) & (res["Null model"] == "directed")]["Predictor"].value_counts().to_dict(),
}
pd.Series(summary, dtype=object).to_csv(OUT / "a07_summary.csv", header=["Value"])
print(pd.Series(summary, dtype=object).to_string())
sel = res[(res["Predictor"] == "Degree assortativity") & (res["Strategy"] == "Degree") & (res["Metric"] == "Efficiency retention") & (res["Null model"] == "reciprocal")]
print(sel[["Airline", "Window", "Spearman rho", "Permutation p", "BY q", "Predictor min", "Predictor max"]].to_string())
