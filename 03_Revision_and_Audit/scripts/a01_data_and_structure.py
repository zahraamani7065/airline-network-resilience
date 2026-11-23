"""Audit 1: rebuild the networks from the raw BTS files and recompute Table 1."""
import networkx as nx
import numpy as np
import pandas as pd

from audit_common import AIRLINES, DATA, OUT, TABLES, adjacency, observed, outcomes

raw = pd.concat([pd.read_csv(DATA / "raw" / f"{m} 2025.csv", low_memory=False) for m in ["April", "May", "June"]], ignore_index=True)
report = {"Raw records": len(raw)}
sel = raw[raw["MKT_UNIQUE_CARRIER"].isin(AIRLINES)]
report["Selected records"] = len(sel)
report["Selected scheduled flights (sum FLIGHTS)"] = float(sel["FLIGHTS"].sum())
report["Self-loop records"] = int((sel["ORIGIN_AIRPORT_ID"] == sel["DEST_AIRPORT_ID"]).sum())
report["Days per airline"] = sel.groupby("MKT_UNIQUE_CARRIER")["FL_DATE"].nunique().to_dict()
key = ["FL_DATE", "MKT_UNIQUE_CARRIER", "MKT_CARRIER_FL_NUM", "ORIGIN_AIRPORT_ID", "DEST_AIRPORT_ID"]
report["Duplicate flight keys"] = int(sel.duplicated(key).sum())
sel = sel[sel["ORIGIN_AIRPORT_ID"] != sel["DEST_AIRPORT_ID"]]

rows, monthly = [], []
for a in AIRLINES:
    f = sel[sel["MKT_UNIQUE_CARRIER"] == a]
    e = f.groupby(["ORIGIN_AIRPORT_ID", "DEST_AIRPORT_ID"])["FLIGHTS"].sum().reset_index()
    e.columns = ["source", "target", "frequency"]
    saved = pd.read_csv(DATA / "Processed" / f"{a}_edges.csv")
    m = e.merge(saved, on=["source", "target"], how="outer", suffixes=("_raw", "_saved"), indicator=True)
    report[f"{a}: edges match saved file"] = bool((m["_merge"] == "both").all() and np.allclose(m["frequency_raw"], m["frequency_saved"]))
    # routes that exist only through diverted flights
    nd = f[f["DIVERTED"] == 0].groupby(["ORIGIN_AIRPORT_ID", "DEST_AIRPORT_ID"]).size()
    report[f"{a}: routes only from diverted records"] = int(len(e) - len(nd))
    report[f"{a}: cancelled share of flights"] = float(f["CANCELLED"].sum() / f["FLIGHTS"].sum())

    ids, s, t, w, nodes = observed(a)
    n = len(ids)
    G = nx.DiGraph()
    G.add_nodes_from(range(n))
    G.add_edges_from(zip(s, t))
    U = nx.Graph(G)
    deg = np.array([d for _, d in U.degree()], float)
    outs = np.bincount(s, weights=w, minlength=n)
    x = np.sort(outs)
    gini = 2 * np.sum(np.arange(1, n + 1) * x) / (n * x.sum()) - (n + 1) / n
    core = nx.core_number(U)
    kmax = max(core.values())
    inner = sum(v == kmax for v in core.values())
    eff, reach, scc = outcomes(adjacency(s, t, n), np.ones(n, bool), n)
    lengths = [d for src, ll in nx.all_pairs_shortest_path_length(G) for tgt, d in ll.items() if tgt != src]
    rows.append({
        "Airline": a, "Airports": n, "Directed routes": len(s), "Undirected routes": U.number_of_edges(),
        "Density": len(s) / (n * (n - 1)), "Mean out-degree": len(s) / n, "Reciprocity": nx.reciprocity(G),
        "Strongly connected": nx.is_strongly_connected(G), "Scheduled flights": w.sum(),
        "Max degree": deg.max(), "Max degree share of N-1": deg.max() / (n - 1),
        "Degree centralization": np.sum(deg.max() - deg) / ((n - 1) * (n - 2)),
        "Out-strength Gini": gini, "Top-5 airports share of departures": np.sort(outs)[::-1][:5].sum() / outs.sum(),
        "Avg clustering": nx.average_clustering(U), "Transitivity": nx.transitivity(U),
        "Degree assortativity": nx.degree_assortativity_coefficient(U),
        "Mean path length": np.mean(lengths), "Efficiency": eff, "Reachability": reach,
        "Max core": kmax, "Innermost core size": inner, "Innermost core share": inner / n,
        "Degree-1 airports": int((deg == 1).sum()), "Degree-1 share": float((deg == 1).mean()),
        "Degree>=2 airports": int((deg >= 2).sum()),
        "Low-frequency routes (<=13 flights, directed)": int((w <= 13).sum()),
    })

stats = pd.DataFrame(rows)
stats.to_csv(OUT / "a01_network_structure.csv", index=False)

saved = pd.read_csv(TABLES / "02_final_network_comparison.csv").set_index("Airline")
trans = pd.read_csv(TABLES / "02_clustering_vs_transitivity.csv").set_index("Airline")
kc = pd.read_csv(TABLES / "03_kcore_summary.csv").set_index("Airline")
cmp = []
for _, r in stats.iterrows():
    a = r["Airline"]
    for mine, theirs, val in [("Density", "Density", saved.loc[a, "Density"]),
                              ("Degree centralization", "Degree centralization", saved.loc[a, "Degree centralization"]),
                              ("Out-strength Gini", "Out-strength Gini", saved.loc[a, "Out-strength Gini"]),
                              ("Avg clustering", "Avg clustering", saved.loc[a, "Avg clustering"]),
                              ("Degree assortativity", "Degree assortativity", saved.loc[a, "Degree assortativity"]),
                              ("Mean path length", "Mean reachable path length", saved.loc[a, "Mean reachable path length"]),
                              ("Transitivity", "Transitivity", trans.loc[a, "Transitivity"]),
                              ("Max core", "Maximum core number", kc.loc[a, "Maximum core number"]),
                              ("Innermost core size", "Innermost core size", kc.loc[a, "Innermost core size"])]:
        cmp.append({"Airline": a, "Measure": mine, "Audit": r[mine], "Project": val, "Match (1e-9)": bool(abs(r[mine] - val) < 1e-9)})
cmp = pd.DataFrame(cmp)
cmp.to_csv(OUT / "a01_structure_vs_project.csv", index=False)
pd.Series(report, dtype=object).to_csv(OUT / "a01_data_checks.csv", header=["Value"])
pd.set_option("display.width", 250, "display.max_columns", None)
print(pd.Series(report, dtype=object).to_string())
print(stats.T.to_string())
print("Mismatches:\n", cmp[~cmp["Match (1e-9)"]].to_string())
