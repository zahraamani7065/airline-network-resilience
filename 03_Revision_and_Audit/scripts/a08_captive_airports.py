"""Audit 8 (exploratory, new): 'hub-captive' airports.

An airport is captive to a hub set H when every one of its neighbours is in H, so it is
cut off as soon as H is removed. We count captive airports for H = the top-K degree hubs
(K at nominal 2% and 5%), in the observed graphs and in every null graph, and relate the
count to early degree-targeted efficiency AUC and to degree assortativity within the
reciprocal ensembles.
"""
import networkx as nx
import numpy as np
import pandas as pd
from scipy.stats import spearmanr

from audit_common import AIRLINES, OUT, nulls, observed, removal_count

b = pd.read_csv(OUT / "a07_experiment_b.csv")
rows, corr = [], []
for a in AIRLINES:
    ids, s0, t0, _, _ = observed(a)
    n = len(ids)
    K2, K5 = removal_count(n, 2), removal_count(n, 5)
    for fam in ["observed", "reciprocal", "directed"]:
        z = np.load(OUT / f"a02_{a}_{fam}.npz")
        graphs = [(s0, t0)] if fam == "observed" else nulls(a, fam)
        for k, (s, t) in enumerate(graphs):
            U = nx.Graph(); U.add_nodes_from(range(n)); U.add_edges_from(zip(s.tolist(), t.tolist()))
            order = z["orders"][k, 0]
            rec = {"Airline": a, "Family": fam, "Network": k, "Assortativity": nx.degree_assortativity_coefficient(U),
                   "Hub-hub links among top K5": U.subgraph(order[:K5].tolist()).number_of_edges()}
            for K, lab in [(K2, "2%"), (K5, "5%")]:
                H = set(order[:K].tolist())
                rec[f"Captive at {lab}"] = sum(1 for i in range(n) if i not in H and U.degree(i) > 0 and all(j in H for j in U.neighbors(i)))
            ret = z["targeted"][k, 0, :, 0] / z["intact"][k, 0]
            rec["Degree retention 2%"], rec["Degree retention 5%"] = ret[1], ret[2]
            rows.append(rec)
d = pd.DataFrame(rows)
d.to_csv(OUT / "a08_captive.csv", index=False)
for a in AIRLINES:
    for fam in ["reciprocal", "directed"]:
        g = d[(d["Airline"] == a) & (d["Family"] == fam)].sort_values("Network")
        auc = b[(b["Airline"] == a) & (b["Null model"] == fam)]  # only for sanity of family size
        corr.append({"Airline": a, "Null": fam,
                     "rho(captive2%, retention2%)": spearmanr(g["Captive at 2%"], g["Degree retention 2%"])[0],
                     "rho(captive2%, assortativity)": spearmanr(g["Captive at 2%"], g["Assortativity"])[0],
                     "rho(hub-hub links, assortativity)": spearmanr(g["Hub-hub links among top K5"], g["Assortativity"])[0],
                     "rho(assortativity, retention2%)": spearmanr(g["Assortativity"], g["Degree retention 2%"])[0],
                     "Captive2% null range": f"{g['Captive at 2%'].min()}-{g['Captive at 2%'].max()}",
                     "Captive2% observed": int(d[(d["Airline"] == a) & (d["Family"] == "observed")]["Captive at 2%"].iloc[0]),
                     "Captive5% null range": f"{g['Captive at 5%'].min()}-{g['Captive at 5%'].max()}",
                     "Captive5% observed": int(d[(d["Airline"] == a) & (d["Family"] == "observed")]["Captive at 5%"].iloc[0])})
c = pd.DataFrame(corr)
c.to_csv(OUT / "a08_captive_correlations.csv", index=False)
pd.set_option("display.width", 250, "display.max_columns", None)
print(c.round(3).to_string())
print(d[d["Family"] == "observed"].round(4).to_string())
