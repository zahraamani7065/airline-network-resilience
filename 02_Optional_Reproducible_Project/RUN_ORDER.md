# Run order

Install the environment first (see `requirements.txt`; Python 3.13.5). Start each notebook
in a fresh kernel and run it from top to bottom. Results were produced on Windows 11; Colab
has not been tested with these pinned versions.

| Step | Notebook | Needs | Produces | Time (23 Nov 2026) |
|---|---|---|---|---|
| 1 | NB01 Data Preparation | raw BTS files in `Data/raw` | processed nodes and edges, `01_*` | ~1 min |
| 2 | NB02 Network Structure | step 1 | `02_*` | ~1 min |
| 3 | NB03 Communities and Cohesion | steps 1–2 | Louvain runs, participation, `03_*` | ~6 min |
| 4 | NB04 Null Models | steps 1–3 | null networks, random orders, null modularity, `04_*` | ~2 h |
| 5 | NB05 Removal Setup | steps 1, 2, 4 | rankings, manifests, `05_*` | ~3 min |
| 6 | NB06 Resilience Metrics, Sections 6.1–6.6 | steps 4–5 | H1 and H2, `06_*` | ~17 min |
| 7 | NB06 Section 6.7 (stage 08) | step 6 | early-window AUCs, `08_*` | ~12 min |
| 8 | NB09 Structure and Resilience | steps 2–4 and 7 | Experiment B, `09_*` | ~3 min |
| 9 | NB07 Single Airport and H3 | steps 3 and 6 | H3, `07_*`; Section 7.8: Experiment C, `10_*`; Section 7.9 reads the saved `07_*` tables | ~9 min |

Notes
- There is no NB08 notebook: stage 08 is Section 6.7 of NB06.
- NB07 and NB09 do not depend on each other and can run in either order.
- After rerunning a notebook, rerun every later notebook that depends on it.
  In particular, rerunning NB03 requires rerunning NB04, NB09 and NB07.
- Run each notebook only once per kernel session. Re-executing single cells can append
  duplicate rows to check and seed-registry tables.
- The Louvain runs in NB03 and NB04 depend on the NetworkX version: with the same seeds,
  NetworkX 3.6.1 and 3.7 give different partitions in 65 of the 300 binary runs. Use the
  pinned versions to reproduce the reported values exactly.
