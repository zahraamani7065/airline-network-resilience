"""Audit 4: rerun Experiment C (repeated stratified CV, ridge, degree spline +/- participation)
from the audit's own single-airport outcomes, and compare with the saved summary."""
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import Ridge
from sklearn.model_selection import GridSearchCV, KFold, StratifiedKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import SplineTransformer, StandardScaler

from audit_common import AIRLINES, OUT, SUPP, TABLES

SEED = 20261118  # supplementary seed recorded in supplementary_helpers.py
mine = pd.read_csv(OUT / "a03_single_airport.csv")
part = pd.read_csv(TABLES / "07_single_airport_outcomes.csv")[["Airline", "AirportID", "Participation mean"]]
data = mine.merge(part, on=["Airline", "AirportID"])
data = data[data["Degree"] >= 2]


def model(flexible, participation):
    deg = [("spline", SplineTransformer(n_knots=4, degree=2, include_bias=False)), ("scale", StandardScaler())] if flexible else [("scale", StandardScaler())]
    tr = [("degree", Pipeline(deg), [0])] + ([("p", StandardScaler(), [1])] if participation else [])
    return Pipeline([("features", ColumnTransformer(tr)), ("ridge", Ridge())])


rows = []
for ai, a in enumerate(AIRLINES):
    g = data[data["Airline"] == a].sort_values("AirportID").reset_index(drop=True)
    X = np.column_stack([np.log1p(g["Degree"]), g["Participation mean"]])
    strata = (g["Survivor damage"] > 1e-12).astype(int)
    for rep in range(5):
        split = list(StratifiedKFold(5, shuffle=True, random_state=SEED + 100 * ai + rep).split(X, strata))
        for outcome, col in [("Efficiency loss", "Efficiency loss"), ("Surviving-airport damage", "Survivor damage")]:
            y = g[col].to_numpy()
            r2 = {}
            for flex in (False, True):
                for p in (False, True):
                    pred = np.empty(len(g))
                    for fold, (tr, te) in enumerate(split):
                        f = GridSearchCV(model(flex, p), {"ridge__alpha": [.1, 1., 10., 100.]}, cv=KFold(3, shuffle=True, random_state=SEED + fold),
                                         scoring="neg_mean_squared_error").fit(X[tr], y[tr])
                        pred[te] = f.predict(X[te])
                    r2[(flex, p)] = 1 - ((y - pred) ** 2).sum() / ((y - y.mean()) ** 2).sum()
            for flex, name in [(False, "Linear log-degree"), (True, "Spline degree")]:
                rows.append({"Airline": a, "Outcome": outcome, "Degree baseline": name, "Repeat": rep,
                             "Baseline R2": r2[(flex, False)], "R2 gain": r2[(flex, True)] - r2[(flex, False)]})
res = pd.DataFrame(rows)
summ = res.groupby(["Airline", "Outcome", "Degree baseline"]).agg(Median_baseline_R2=("Baseline R2", "median"), Median_R2_gain=("R2 gain", "median"),
                                                                 Positive_repeats=("R2 gain", lambda x: int((x > 0).sum()))).reset_index()
saved = pd.read_csv(SUPP / "Tables" / "10_prediction_gain_summary.csv")
summ = summ.merge(saved[["Airline", "Outcome", "Degree baseline", "Median_R2_gain"]], on=["Airline", "Outcome", "Degree baseline"], suffixes=("", " (project)"))
summ["Abs diff"] = (summ["Median_R2_gain"] - summ["Median_R2_gain (project)"]).abs()
summ.to_csv(OUT / "a04_experiment_c.csv", index=False)
pd.set_option("display.width", 250)
print(summ.to_string())
