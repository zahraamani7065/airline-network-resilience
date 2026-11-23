"""Audit 2: recompute every removal outcome from the saved graphs.

For the observed network and every saved null graph (200 directed, 100 reciprocal)
this script independently rebuilds the degree and betweenness rankings, then
computes
  * targeted outcomes at nominal 1, 2, 5, 10, 15, 20 % (Experiment A + H1/H2 levels),
  * paired random outcomes for the same 100 recorded random orders,
  * the complete static targeted removal curve (one airport at a time), used for the
    exploratory robustness score R and K50.
Results are cached in outputs/a02_<airline>_<family>.npz.
"""
import sys
from multiprocessing import Pool

import networkx as nx
import numpy as np
import pandas as pd

from audit_common import AIRLINES, DATA, OUT, adjacency, after, nulls, observed, outcomes, random_orders, rank_desc, removal_count

ALL_LEVELS = [1, 2, 5, 10, 15, 20]


def analyse(args):
    airline, s, t = args
    ids = observed(airline)[0]
    n = len(ids)
    A = adjacency(s, t, n)
    deg = np.bincount(s, minlength=n) + np.bincount(t, minlength=n)
    G = nx.DiGraph()
    G.add_nodes_from(range(n))
    G.add_edges_from(zip(s.tolist(), t.tolist()))
    bc = nx.betweenness_centrality(G, normalized=True)
    btw = np.array([bc[i] for i in range(n)])
    orders = {"Degree": rank_desc(deg, ids), "Betweenness": rank_desc(btw, ids)}
    intact = np.array(outcomes(A, np.ones(n, bool), n))
    ks = [removal_count(n, p) for p in ALL_LEVELS]
    targeted = np.array([[after(A, orders[st][:k], n) for k in ks] for st in ("Degree", "Betweenness")])
    rnd = np.array([[after(A, o[:k], n) for k in ks] for o in random_orders(airline)])
    curves = np.zeros((2, n + 1, 3))
    for i, st in enumerate(("Degree", "Betweenness")):
        for k in range(n + 1):
            curves[i, k] = after(A, orders[st][:k], n) if k < n else (0, 0, 0)
    return intact, targeted, rnd, curves, np.stack([orders["Degree"], orders["Betweenness"]]), btw


def main(airlines):
    for airline in airlines:
        ids, s, t, _, _ = observed(airline)
        for family in ["observed", "directed", "reciprocal"]:
            graphs = [(s, t)] if family == "observed" else nulls(airline, family)
            with Pool(11) as pool:
                res = pool.map(analyse, [(airline, a, b) for a, b in graphs], chunksize=4)
            np.savez_compressed(OUT / f"a02_{airline}_{family}.npz",
                                levels=np.array(ALL_LEVELS),
                                intact=np.array([r[0] for r in res]), targeted=np.array([r[1] for r in res]),
                                random=np.array([r[2] for r in res]), curves=np.array([r[3] for r in res]),
                                orders=np.array([r[4] for r in res]), betweenness=np.array([r[5] for r in res]))
            print(airline, family, len(res), flush=True)


if __name__ == "__main__":
    main(sys.argv[1:] or AIRLINES)
