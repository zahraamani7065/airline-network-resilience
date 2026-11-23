"""Audit 10: structural constraints of the 900 saved null graphs."""
import numpy as np
import pandas as pd

from audit_common import AIRLINES, OUT, nulls, observed

rows = []
for a in AIRLINES:
    ids, s0, t0, _, _ = observed(a)
    n = len(ids)
    din0, dout0 = np.bincount(t0, minlength=n), np.bincount(s0, minlength=n)
    obs_set = set(zip(s0.tolist(), t0.tolist()))
    for fam in ["directed", "reciprocal"]:
        G = nulls(a, fam)
        keys = set()
        ok_deg = ok_simple = ok_recip = 0
        overlap = []
        recips = []
        for s, t in G:
            e = set(zip(s.tolist(), t.tolist()))
            ok_deg += np.array_equal(np.bincount(t, minlength=n), din0) and np.array_equal(np.bincount(s, minlength=n), dout0)
            ok_simple += (len(e) == len(s)) and not (s == t).any()
            r = np.mean([(y, x) in e for x, y in e])
            recips.append(r)
            ok_recip += r == 1.0
            keys.add(frozenset(e))
            overlap.append(len(e & obs_set) / len(e))
        rows.append({"Airline": a, "Family": fam, "Graphs": len(G), "Degree sequence preserved": ok_deg, "Simple (no loops/multi-arcs)": ok_simple,
                     "Fully reciprocal": ok_recip, "Mean reciprocity": np.mean(recips), "Unique graphs": len(keys),
                     "Mean share of observed routes kept": np.mean(overlap), "Min share kept": np.min(overlap), "Max share kept": np.max(overlap)})
d = pd.DataFrame(rows)
d.to_csv(OUT / "a10_null_constraints.csv", index=False)
pd.set_option("display.width", 250, "display.max_columns", None)
print(d.round(4).to_string())
