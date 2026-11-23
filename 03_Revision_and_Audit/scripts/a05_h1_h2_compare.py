"""Audit 5: compare recomputed removal outcomes with the project, re-derive H1/H2 and
Experiment A, and quantify the efficiency floor."""
import numpy as np
import pandas as pd

from audit_common import AIRLINES, DATA, OUT, SUPP, TABLES, observed, removal_count

LV = [1, 2, 5, 10, 15, 20]
MAIN = [2, 3, 4, 5]  # indices of 5..20 in LV
MET = ["Efficiency", "Reachability", "Largest SCC"]
ST = ["Degree", "Betweenness"]
L = {}
for a in AIRLINES:
    for fam in ["observed", "directed", "reciprocal"]:
        L[a, fam] = dict(np.load(OUT / f"a02_{a}_{fam}.npz"))

checks = []
saved_out = pd.read_csv(TABLES / "06_network_outcomes.csv")
for a in AIRLINES:
    ids = observed(a)[0]
    for fam in ["observed", "directed", "reciprocal"]:
        z = L[a, fam]
        plan = np.load(DATA / "Processed" / "Removal_Plans" / f"{a}_{fam}_targeted_rankings.npz")
        for si, st in enumerate(ST):
            mine = ids[z["orders"][:, si]]
            theirs = plan[f"{st.lower()}_order"]
            same_order = (mine == theirs).all(1).mean()
            same_sets = np.mean([all(set(m[:removal_count(len(ids), p)]) == set(t[:removal_count(len(ids), p)]) for p in [5, 10, 15, 20]) for m, t in zip(mine, theirs)])
            checks.append({"Check": f"{a}/{fam}/{st}: identical full ranking", "Value": same_order})
            checks.append({"Check": f"{a}/{fam}/{st}: identical removed sets at 5-20%", "Value": same_sets})
        # targeted outcomes vs saved table
        s = saved_out[(saved_out["Airline"] == a) & (saved_out["Network set"] == fam)]
        diffs = []
        for si, st in enumerate(ST):
            for li, p in zip(MAIN, [5, 10, 15, 20]):
                ss = s[(s["Strategy"] == st) & (s["Level"] == p)].sort_values("Network")
                diffs.append(np.abs(ss[MET].to_numpy() - z["targeted"][:, si, li, :]).max())
        checks.append({"Check": f"{a}/{fam}: targeted outcomes max abs diff", "Value": max(diffs)})
        saved_r = np.load(DATA / "Processed" / "Resilience" / f"{a}_{fam}_paired_random_trials.npz")["values"]
        checks.append({"Check": f"{a}/{fam}: random trials max abs diff", "Value": np.abs(saved_r - z["random"][:, :, MAIN, :]).max()})
        early = np.load(SUPP / "Arrays" / f"08_{a}_{fam}_early_trials.npz")
        checks.append({"Check": f"{a}/{fam}: Exp A targeted 1-2% max abs diff", "Value": np.abs(early["targeted"] - z["targeted"][:, :, :2, :]).max()})
        checks.append({"Check": f"{a}/{fam}: Exp A random 1-2% max abs diff", "Value": np.abs(early["trials"] - z["random"][:, :, :2, :]).max()})

# ---------- H1 ----------
h1 = []
for a in AIRLINES:
    z = L[a, "observed"]
    intact = z["intact"][0]
    rl = intact[None, None, :] - z["random"][0]          # trials x levels x metrics (losses)
    hi, lo = np.percentile(rl, 97.5, axis=0), np.percentile(rl, 2.5, axis=0)
    for si, st in enumerate(ST):
        tl = intact[None, :] - z["targeted"][0, si]
        met = tl > hi
        e, r, c = met[MAIN, 0].sum(), met[MAIN, 1].sum(), met[MAIN, 2].sum()
        verdict = "Supported" if (e == 4 and r >= 3 and c >= 3) else ("Partly supported" if e >= 2 else "Not supported")
        h1.append({"Airline": a, "Strategy": st, "Eff met": e, "Reach met": r, "SCC met": c, "Contrary": (tl < lo)[MAIN, 0].sum() >= 2, "Verdict": verdict})
h1 = pd.DataFrame(h1)
saved_h1 = pd.read_csv(TABLES / "06_h1_verdicts.csv")
checks.append({"Check": "H1 verdicts identical", "Value": (h1["Verdict"].to_numpy() == saved_h1["H1 verdict (official, ID ties)"].to_numpy()).all()})

# ---------- H2 ----------
def values(a, fam, strategy, li):
    z = L[a, fam]
    intact = z["intact"]
    if strategy == "Random":
        v = z["random"][:, :, li, :].mean(1)
    else:
        v = z["targeted"][:, ST.index(strategy), li, :]
    return {"Efficiency retention": v[:, 0] / intact[:, 0], "Efficiency": v[:, 0], "Reachability": v[:, 1], "Largest SCC": v[:, 2]}

cells = []
for a in AIRLINES:
    for strategy in ST + ["Random"]:
        for li, p in zip(MAIN, [5, 10, 15, 20]):
            o, n = values(a, "observed", strategy, li), values(a, "directed", strategy, li)
            rec = values(a, "reciprocal", strategy, li)
            for m in ["Efficiency retention", "Efficiency", "Reachability", "Largest SCC"]:
                lo, hi = np.percentile(n[m], [2.5, 97.5])
                rlo, rhi = np.percentile(rec[m], [2.5, 97.5])
                v = o[m][0]
                cells.append({"Airline": a, "Strategy": strategy, "Level": p, "Measure": m, "Observed": v, "Null mean": n[m].mean(),
                              "Null 2.5%": lo, "Null 97.5%": hi, "Width": hi - lo,
                              "Position": "below" if v < lo else ("above" if v > hi else "within"),
                              "Rec 2.5%": rlo, "Rec 97.5%": rhi, "Rec position": "below" if v < rlo else ("above" if v > rhi else "within"),
                              "Null share below 0.05 retention": float((n["Efficiency retention"] < 0.05).mean())})
cells = pd.DataFrame(cells)
cells.to_csv(OUT / "a05_h2_cells.csv", index=False)
dec = cells[cells["Measure"].isin(["Efficiency retention", "Reachability", "Largest SCC"])]
saved_cells = pd.read_csv(TABLES / "06_h2_primary_cells.csv")
mrg = cells.merge(saved_cells, on=["Airline", "Strategy", "Level", "Measure"], suffixes=("", "_p"))
checks.append({"Check": "H2 144 cells: max abs diff in null limits", "Value": max(np.abs(mrg["Null 2.5%"] - mrg["Null 2.5%_p"]).max(), np.abs(mrg["Null 97.5%"] - mrg["Null 97.5%_p"]).max())})
checks.append({"Check": "H2 144 cells: positions identical", "Value": (mrg["Position"] == mrg["Position_p"]).all()})
checks.append({"Check": "H2 108 decision cells: within/above/below", "Value": dec["Position"].value_counts().to_dict()})
checks.append({"Check": "H2 108: zero-width (<=1e-12)", "Value": int((dec["Width"] <= 1e-12).sum())})
checks.append({"Check": "H2 108: width <= 0.001", "Value": int((dec["Width"] <= 0.001).sum())})
checks.append({"Check": "H2 144: zero-width (<=1e-12)", "Value": int((cells["Width"] <= 1e-12).sum())})
checks.append({"Check": "H2 144: width <= 0.001", "Value": int((cells["Width"] <= 0.001).sum())})

h2 = []
for a in AIRLINES:
    dirs = []
    for strategy in ST + ["Random"]:
        f = dec[(dec["Airline"] == a) & (dec["Strategy"] == strategy)]
        d = "None"
        for direction in ["above", "below"]:
            g = f[f["Position"] == direction].groupby("Measure").size()
            if g.get("Efficiency retention", 0) >= 3 and max(g.get("Reachability", 0), g.get("Largest SCC", 0)) >= 3:
                d = direction
                break
        dirs.append(d)
    up, down = dirs.count("above"), dirs.count("below")
    h2.append({"Airline": a, "Degree": dirs[0], "Betweenness": dirs[1], "Random": dirs[2],
               "Verdict": "Supported" if max(up, down) >= 2 else ("Mixed" if up and down else "Not supported")})
h2 = pd.DataFrame(h2)
saved_h2 = pd.read_csv(TABLES / "06_h2_verdicts.csv")
checks.append({"Check": "H2 verdicts identical", "Value": (h2["Verdict"].to_numpy() == saved_h2["H2 verdict (primary null)"].to_numpy()).all()})

# ---------- floor diagnostics ----------
floor = []
for a in AIRLINES:
    for strategy in ST + ["Random"]:
        f = dec[(dec["Airline"] == a) & (dec["Strategy"] == strategy)]
        r = f[f["Measure"] == "Efficiency retention"]
        floor.append({"Airline": a, "Strategy": strategy,
                      "Decision cells": len(f), "Cells width<=0.001": int((f["Width"] <= 0.001).sum()),
                      "Observed retention 5%": r[r["Level"] == 5]["Observed"].iloc[0],
                      "Null mean retention 5%": r[r["Level"] == 5]["Null mean"].iloc[0],
                      "Null 97.5% retention 5%": r[r["Level"] == 5]["Null 97.5%"].iloc[0],
                      "Positions": "".join(x[0] for x in f.sort_values(["Measure", "Level"])["Position"])})
floor = pd.DataFrame(floor)
floor.to_csv(OUT / "a05_floor.csv", index=False)

# ---------- Experiment A numbers ----------
expa = []
for a in AIRLINES:
    zo, zr, zd = L[a, "observed"], L[a, "reciprocal"], L[a, "directed"]
    n = len(observed(a)[0])
    for li, p in [(0, 1), (1, 2)]:
        ret = zo["targeted"][0, 0, li, 0] / zo["intact"][0, 0]
        rr = zr["targeted"][:, 0, li, 0] / zr["intact"][:, 0]
        dr = zd["targeted"][:, 0, li, 0] / zd["intact"][:, 0]
        expa.append({"Airline": a, "Level": p, "K": removal_count(n, p), "Observed degree retention": ret,
                     "Obs - reciprocal mean": ret - rr.mean(), "Within reciprocal 95%": np.percentile(rr, 2.5) <= ret <= np.percentile(rr, 97.5),
                     "Within directed 95%": np.percentile(dr, 2.5) <= ret <= np.percentile(dr, 97.5)})
expa = pd.DataFrame(expa)
expa.to_csv(OUT / "a05_experiment_a.csv", index=False)

pd.DataFrame(checks).to_csv(OUT / "a05_checks.csv", index=False)
h1.to_csv(OUT / "a05_h1.csv", index=False)
h2.to_csv(OUT / "a05_h2.csv", index=False)
pd.set_option("display.width", 250, "display.max_columns", None, "display.max_colwidth", 80)
print(pd.DataFrame(checks).to_string())
print(h1.to_string()); print(h2.to_string()); print(floor.to_string()); print(expa.to_string())
eff = dec[dec["Measure"] == "Efficiency retention"]
print(eff[eff["Position"] != "within"][["Airline", "Strategy", "Level", "Observed", "Null mean", "Null 2.5%", "Null 97.5%", "Position", "Rec position"]].to_string())
print(dec[dec["Position"] != "within"].groupby(["Airline", "Strategy", "Measure", "Position"]).size().to_string())
