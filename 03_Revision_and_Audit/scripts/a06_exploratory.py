"""Audit 6 (exploratory, new): robustness score R, K50, adaptive attacks, mechanism of
early collapse, monthly and route-frequency sensitivity, and a few spot checks.

None of these results changes an H1/H2/H3 decision rule; all are labelled exploratory.
"""
import networkx as nx
import numpy as np
import pandas as pd
from networkx.algorithms.community import louvain_communities, modularity

from audit_common import AIRLINES, DATA, OUT, TABLES, adjacency, after, nulls, observed, outcomes, random_orders, rank_desc

EXTRA_SEED = 20261122  # seed for the new random orders used only in the monthly/frequency checks


def r_and_k50(curve):
    """curve: (N+1) x 3 array of efficiency, reachability, SCC fraction after k removals."""
    n = curve.shape[0] - 1
    ret = curve[:, 0] / curve[0, 0]
    R_E = ret[1:].sum() / n
    R_S = curve[1:, 2].sum() / n
    k50 = int(np.argmax(ret <= 0.5))
    return R_E, R_S, k50


def full_curve(A, order, n):
    c = np.zeros((n + 1, 3))
    for k in range(n):
        c[k] = after(A, order[:k], n)
    return c


def adaptive_curve(s, t, ids, kind):
    n = len(ids)
    A = adjacency(s, t, n)
    alive = np.ones(n, bool)
    c = np.zeros((n + 1, 3))
    c[0] = outcomes(A, alive, n)
    for k in range(1, n + 1):
        idx = np.flatnonzero(alive)
        B = A[idx][:, idx]
        if kind == "Degree":
            v = np.asarray(B.sum(0)).ravel() + np.asarray(B.sum(1)).ravel()
        else:
            G = nx.from_scipy_sparse_array(B, create_using=nx.DiGraph)
            bc = nx.betweenness_centrality(G, normalized=True)
            v = np.array([bc[i] for i in range(len(idx))])
        pick = idx[rank_desc(v, ids[idx])[0]]
        alive[pick] = False
        c[k] = outcomes(A, alive, n) if alive.any() else (0, 0, 0)
    return c


rows_R, rows_mech = [], []
curves_store = {}
for a in AIRLINES:
    ids, s, t, w, nodes = observed(a)
    n = len(ids)
    A = adjacency(s, t, n)
    codes = nodes.set_index("airport_id").loc[ids, "code"].to_numpy()
    for fam in ["observed", "directed", "reciprocal"]:
        z = np.load(OUT / f"a02_{a}_{fam}.npz")
        for si, st in enumerate(["Degree", "Betweenness"]):
            vals = np.array([r_and_k50(c) for c in z["curves"][:, si]])
            for j, name in enumerate(["R_E", "R_S", "K50"]):
                rows_R.append({"Airline": a, "Family": fam, "Strategy": st + " (static)", "Measure": name,
                               "Value": vals[0, j] if fam == "observed" else np.nan,
                               "Mean": vals[:, j].mean(), "2.5%": np.percentile(vals[:, j], 2.5), "97.5%": np.percentile(vals[:, j], 97.5),
                               "Min": vals[:, j].min(), "Max": vals[:, j].max()})
        if fam == "observed":
            curves_store[a, "Degree (static)"] = z["curves"][0, 0]
            curves_store[a, "Betweenness (static)"] = z["curves"][0, 1]
    # random full curves for the observed network (100 recorded orders)
    rc = np.array([full_curve(A, o, n) for o in random_orders(a)])
    curves_store[a, "Random"] = rc
    vals = np.array([r_and_k50(c) for c in rc])
    for j, name in enumerate(["R_E", "R_S", "K50"]):
        rows_R.append({"Airline": a, "Family": "observed", "Strategy": "Random", "Measure": name, "Value": np.median(vals[:, j]),
                       "Mean": vals[:, j].mean(), "2.5%": np.percentile(vals[:, j], 2.5), "97.5%": np.percentile(vals[:, j], 97.5),
                       "Min": vals[:, j].min(), "Max": vals[:, j].max()})
    # adaptive attacks (observed only)
    for kind in ["Degree", "Betweenness"]:
        c = adaptive_curve(s, t, ids, kind)
        curves_store[a, kind + " (adaptive)"] = c
        v = r_and_k50(c)
        for j, name in enumerate(["R_E", "R_S", "K50"]):
            rows_R.append({"Airline": a, "Family": "observed", "Strategy": kind + " (adaptive)", "Measure": name, "Value": v[j]})

    # mechanism: airports cut off when the top-k degree hubs are removed
    U = nx.Graph(); U.add_nodes_from(range(n)); U.add_edges_from(zip(s.tolist(), t.tolist()))
    deg = np.array([U.degree(i) for i in range(n)])
    order = rank_desc(np.bincount(s, minlength=n) + np.bincount(t, minlength=n), ids)
    for k in range(1, 6):
        gone = set(order[:k].tolist())
        H = U.subgraph([i for i in range(n) if i not in gone])
        comps = sorted(nx.connected_components(H), key=len, reverse=True)
        isolated = sum(1 for c in comps if len(c) == 1)
        rows_mech.append({"Airline": a, "Hubs removed": k, "Hubs": ", ".join(codes[order[:k]]),
                          "Efficiency retention": curves_store[a, "Degree (static)"][k, 0] / curves_store[a, "Degree (static)"][0, 0],
                          "Largest component share of N": len(comps[0]) / n, "Isolated airports": isolated,
                          "Isolated share of N": isolated / n, "Components": len(comps)})
    top = order[0]
    rows_mech.append({"Airline": a, "Hubs removed": 0, "Hubs": "degree-1 airports attached to top hub " + codes[top],
                      "Isolated airports": int(sum(1 for i in range(n) if deg[i] == 1 and U.has_edge(i, top))),
                      "Isolated share of N": float((deg == 1).mean())})

R = pd.DataFrame(rows_R)
R.to_csv(OUT / "a06_robustness_R_K50.csv", index=False)
mech = pd.DataFrame(rows_mech)
mech.to_csv(OUT / "a06_early_collapse_mechanism.csv", index=False)
np.savez_compressed(OUT / "a06_observed_curves.npz", **{f"{a}|{k}": v for (a, k), v in curves_store.items()})

# ---------- monthly and frequency-threshold sensitivity (observed only) ----------
raw = pd.concat([pd.read_csv(DATA / "raw" / f"{m} 2025.csv", usecols=["MONTH", "MKT_UNIQUE_CARRIER", "ORIGIN_AIRPORT_ID", "DEST_AIRPORT_ID", "FLIGHTS"])
                 for m in ["April", "May", "June"]])
raw = raw[raw["MKT_UNIQUE_CARRIER"].isin(AIRLINES) & (raw["ORIGIN_AIRPORT_ID"] != raw["DEST_AIRPORT_ID"])]
rng = np.random.default_rng(EXTRA_SEED)
rows_sens = []


def summarise(a, label, e):
    ids = np.unique(np.r_[e["ORIGIN_AIRPORT_ID"].to_numpy(), e["DEST_AIRPORT_ID"].to_numpy()])
    n = len(ids)
    s = np.searchsorted(ids, e["ORIGIN_AIRPORT_ID"].to_numpy()); t = np.searchsorted(ids, e["DEST_AIRPORT_ID"].to_numpy())
    A = adjacency(s, t, n)
    G = nx.DiGraph(); G.add_nodes_from(range(n)); G.add_edges_from(zip(s.tolist(), t.tolist()))
    U = nx.Graph(G)
    deg = np.array([U.degree(i) for i in range(n)])
    d_order = rank_desc(np.bincount(s, minlength=n) + np.bincount(t, minlength=n), ids)
    bc = nx.betweenness_centrality(G, normalized=True); b_order = rank_desc([bc[i] for i in range(n)], ids)
    rd = r_and_k50(full_curve(A, d_order, n)); rb = r_and_k50(full_curve(A, b_order, n))
    rr = np.array([r_and_k50(full_curve(A, rng.permutation(n), n)) for _ in range(50)])
    rows_sens.append({"Airline": a, "Network": label, "Airports": n, "Directed routes": len(s), "Density": len(s) / (n * (n - 1)),
                      "Reciprocity": nx.reciprocity(G), "Strongly connected": nx.is_strongly_connected(G),
                      "Degree-1 share": float((deg == 1).mean()), "Assortativity": nx.degree_assortativity_coefficient(U),
                      "R_E degree": rd[0], "K50 degree": rd[2], "f50 degree": rd[2] / n,
                      "R_E betweenness": rb[0], "K50 betweenness": rb[2],
                      "R_E random median": np.median(rr[:, 0]), "K50 random median": np.median(rr[:, 2])})


for a in AIRLINES:
    f = raw[raw["MKT_UNIQUE_CARRIER"] == a]
    q = f.groupby(["ORIGIN_AIRPORT_ID", "DEST_AIRPORT_ID"])["FLIGHTS"].sum().reset_index()
    summarise(a, "Quarter (all routes)", q)
    summarise(a, "Quarter, routes with >=13 flights", q[q["FLIGHTS"] >= 13])
    for m, name in [(4, "April"), (5, "May"), (6, "June")]:
        summarise(a, name, f[f["MONTH"] == m].groupby(["ORIGIN_AIRPORT_ID", "DEST_AIRPORT_ID"])["FLIGHTS"].sum().reset_index())
sens = pd.DataFrame(rows_sens)
sens.to_csv(OUT / "a06_monthly_frequency_sensitivity.csv", index=False)

# ---------- spot checks of reported null summaries ----------
spot = []
for a in AIRLINES:
    ids = observed(a)[0]
    rec = [nx.reciprocity(nx.DiGraph(list(zip(s.tolist(), t.tolist())))) for s, t in nulls(a, "directed")]
    spot.append({"Airline": a, "Check": "Directed-null reciprocity mean", "Value": np.mean(rec)})
    sample = nulls(a, "reciprocal")[:10]
    best = []
    for s, t in sample:
        U = nx.Graph(); U.add_nodes_from(range(len(ids))); U.add_edges_from(zip(s.tolist(), t.tolist()))
        best.append(max(modularity(U, louvain_communities(U, seed=k)) for k in range(100)))
    saved = pd.read_csv(TABLES / "04_null_modularity_by_network.csv")
    sv = saved[(saved["Airline"] == a) & (saved["Model"] == "reciprocal")].sort_values("Network")["Best modularity"].to_numpy()
    spot.append({"Airline": a, "Check": "Reciprocal-null best Q (first 10 nets): max |audit - project|", "Value": float(np.max(np.abs(np.array(best) - sv[:10])))})
    spot.append({"Airline": a, "Check": "Reciprocal-null best Q project 2.5-97.5%", "Value": f"{np.percentile(sv, 2.5):.4f}-{np.percentile(sv, 97.5):.4f}"})
pd.DataFrame(spot).to_csv(OUT / "a06_spot_checks.csv", index=False)

pd.set_option("display.width", 250, "display.max_columns", None)
print(R.pivot_table(index=["Airline", "Strategy", "Family"], columns="Measure", values=["Value", "2.5%", "97.5%"]).round(4).to_string())
print(mech.to_string())
print(sens.round(4).to_string())
print(pd.DataFrame(spot).to_string())
