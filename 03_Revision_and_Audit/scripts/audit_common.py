"""Shared helpers for the independent audit.

Written separately from the project notebooks so that the audit does not reuse
their functions. Inputs are read from the reproducible project folder; outputs
go to 03_Revision_and_Audit/outputs only. Nothing in the original project is
modified.
"""
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import connected_components, shortest_path

ROOT = Path(__file__).resolve().parents[2]
PROJECT = ROOT / "02_Optional_Reproducible_Project"
DATA = PROJECT / "Data"
TABLES = PROJECT / "Results" / "Tables"
SUPP = PROJECT / "Results" / "Supplementary"
OUT = ROOT / "03_Revision_and_Audit" / "outputs"
FIG = ROOT / "03_Revision_and_Audit" / "figures"
AIRLINES = ["AA", "DL", "WN"]
LEVELS = [5, 10, 15, 20]


def removal_count(n, p):
    """Nearest integer to n*p/100 with halves rounded up (p in percentage points)."""
    return int(np.floor(n * p / 100 + 0.5 + 1e-12))


def observed(airline):
    """Observed network as (sorted airport ids, source index, target index, weights)."""
    edges = pd.read_csv(DATA / "Processed" / f"{airline}_edges.csv")
    nodes = pd.read_csv(DATA / "Processed" / f"{airline}_nodes.csv")
    ids = np.sort(nodes["airport_id"].to_numpy(np.int64))
    s = np.searchsorted(ids, edges["source"].to_numpy(np.int64))
    t = np.searchsorted(ids, edges["target"].to_numpy(np.int64))
    return ids, s, t, edges["frequency"].to_numpy(float), nodes


def adjacency(s, t, n):
    return csr_matrix((np.ones(len(s)), (s, t)), shape=(n, n))


def outcomes(A, keep, universe):
    """Efficiency, reachability and largest-SCC fraction of the subgraph on `keep`,
    normalised by the ORIGINAL universe size (removed airports count as lost)."""
    B = A[keep][:, keep]
    if B.shape[0] == 0:
        return 0.0, 0.0, 0.0
    d = shortest_path(B, unweighted=True, directed=True)
    np.fill_diagonal(d, np.inf)
    finite = np.isfinite(d)
    denom = universe * (universe - 1)
    eff = (1.0 / d[finite]).sum() / denom
    reach = finite.sum() / denom
    lab = connected_components(B, directed=True, connection="strong")[1]
    return eff, reach, np.bincount(lab).max() / universe


def after(A, removed, n):
    keep = np.ones(n, bool)
    keep[np.asarray(removed, int)] = False
    return outcomes(A, keep, n)


def rank_desc(values, ids, decimals=12):
    """Descending order of values (rounded), ties by ascending airport id."""
    v = np.round(np.asarray(values, float), decimals)
    return np.lexsort((ids, -v))


def nulls(airline, family):
    """Saved null networks as list of (source index, target index). family: directed|reciprocal."""
    ids = observed(airline)[0]
    files = [DATA / "Processed" / "Nulls" / f"{airline}_{family}_null_networks.npz"]
    if family == "directed":
        files.append(DATA / "Processed" / "Nulls" / f"{airline}_directed_null_networks_expansion_chains_100_199.npz")
    out = []
    for f in files:
        z = np.load(f)
        assert np.array_equal(z["airport_ids"], ids)
        for s, t in zip(z["source"], z["target"]):
            out.append((np.searchsorted(ids, s), np.searchsorted(ids, t)))
    return out


def random_orders(airline):
    ids = observed(airline)[0]
    tab = pd.read_csv(TABLES / "04_random_removal_orders.csv")
    tab = tab[tab["Airline"] == airline].sort_values("Trial")
    return [np.searchsorted(ids, np.array(x.split(), dtype=np.int64)) for x in tab["Airport order (BTS IDs)"]]
