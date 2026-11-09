# Airline Network Resilience: Project Handoff

**For:** teammate review before the final MSc report is written.
**Project:** Structural Resilience and Hub Dependence in US Airline Networks (AA, DL, WN; BTS data, 1 April to 30 June 2025).
**Status:** Steps 1 to 7 are complete. The final report has not started. Every number here comes from a saved project table.

## 1. Research questions and findings

**RQ1 (structural determinants of resilience).** To what extent do airline network structural properties influence resilience to random and targeted airport disruptions beyond what is expected from their degree sequences?

**RQ2 (identifying critical airports).** Which network measures best predict the connectivity lost when one airport is removed, and do community-bridging measures add information beyond degree?

### Verdicts at a glance

| Hypothesis | AA | DL | WN |
|---|---|---|---|
| **H1** Targeted removal causes greater connectivity loss than random removal | Supported | Supported | Supported |
| **H2** Resilience differs systematically from the primary degree-preserving null | Not supported | Not supported | Not supported |
| **H3** Stronger bridging goes with larger single-airport loss beyond degree | Partly supported | Partly supported | Partly supported |

### H1: targeted versus random removal

Supported for all three airlines under both degree and betweenness targeting. Targeted loss exceeded the 97.5th percentile of 100 random removals for efficiency, reachability and largest SCC at all four levels. No contrary flags occurred, and all 100 tie-order replicates gave the same verdict.

AA and DL fragment almost completely after removing only 5% of airports by targeting, with efficiency retention below 1%. WN declines more gradually, with retention of 0.78 at 5% and 0.06 to 0.07 at 20%.

### H2: observed versus primary degree-preserving null

Not supported for all three airlines under the approved rule. No strategy showed systematic deviation. Of 108 verdict cells, 77 were within the null interval, 19 above and 12 below.

**This does not show that degrees fully explain resilience.** Twenty cells have zero-width null intervals, and 38 have widths of 0.001 or less. Many AA and DL targeted results sit at a floor, where differences cannot be detected.

Near-misses that do not meet the 3-of-4 rule: WN degree-targeted retention is below the interval at 15% and 20%, WN betweenness-targeted is below at 20%, and AA degree-targeted is below at 5% and 10%. For random removal, largest SCC is above the interval for AA and DL at all four levels and for WN at three, but efficiency retention stays within.

### H3: bridging beyond degree

Partly supported for all three airlines. The Gain condition requires the Gain interval to be above 0 and median Gain to be at least 0.02 R²; it is not met by any airline.

| Airline | Partial rank correlation (2.5 to 97.5%) | Median Gain (2.5 to 97.5%) | Bins with higher loss | Conditions met |
|---|---|---|---|---|
| AA | 0.49 (0.37 to 0.59) | 0.039 (−0.006 to 0.078) | 7 of 7 | Partial correlation, degree-matched |
| DL | 0.56 (0.42 to 0.68) | 0.026 (−0.002 to 0.050) | 7 of 8 | Partial correlation, degree-matched |
| WN | 0.28 (−0.08 to 0.55) | 0.003 (−0.030 to 0.014) | 6 of 8 | Degree-matched only |

Degree alone already predicts loss strongly (median out-of-bag R² of 0.83, 0.91 and 0.94). These are associations and predictive comparisons, not causal claims.

### Supplementary findings

- **Modularity:** observed best Q is above both null ranges for every airline (AA 0.212, DL 0.227, WN 0.190). Only the reciprocal-pair null is like-for-like, and modularity does not decide H2.
- **Reciprocal-pair null:** the AA and DL largest-SCC deviations under the primary null disappear, which suggests lost reciprocity may explain them. WN deviations at high removal persist under both nulls, but remain exploratory.
- **Surviving-airport damage:** only 10 AA, 9 DL and 12 WN airports cause any damage between other airports. WN's HNL has mean participation of 0 and the second-highest damage, which is a useful counterexample.

## 2. Methodology (Steps 1 to 7)

**Network definitions.** Airports are nodes, identified by BTS airport ID. A directed edge A → B exists when at least one nonstop flight was scheduled. Edge weight is the number of scheduled flights. Marketing-carrier filtering includes regional partners, and canceled scheduled flights are retained.

| Step | Notebook | What was done |
|---|---|---|
| 1. Data preparation | 01 | 1,985,849 BTS rows, filtered to 1,292,785 AA, DL and WN flights. All 91 days present, no duplicate records. Networks: AA 230 airports and 1,808 routes; DL 212 and 1,506; WN 104 and 1,792. Diverted flights and PR and VI airports retained and documented. |
| 2. Network structure | 02 | Degree, strength, Freeman centralization, out-strength Gini, directed hop-based betweenness, average clustering, transitivity, connectivity and reachability. All observed networks are perfectly reciprocal. |
| 3. Communities, cores, bridges | 03 | Louvain at resolution 1.0 with 100 seeds on the binary undirected projection, with a weighted sensitivity analysis. k-core decomposition. Binary participation and inter-community fraction per run, summarized across 100 runs. Bridging comparisons use degree ≥ 2. |
| 4. Null models | 04 | Primary: directed two-edge swaps preserving each airport's in- and out-degree. Supplementary: reciprocal-pair swaps preserving those degrees and every route's reverse. Pilot of 300 chains; attempts per chain set by the approved rule. 200 primary and 100 supplementary networks per airline. |
| 5. Removal setup | 05 | K from `(2 * N * p + 100) // 200`, with p in percentage points. Rankings fixed on each intact network. Degree ties by ascending BTS ID; betweenness numerical ties (equal after 12-decimal rounding) by ascending BTS ID. 100 paired random orders per airline. |
| 6. Resilience metrics | 06 | Directed efficiency, ordered-pair reachability and largest SCC using the original N and N(N−1). H1 on observed networks; H2 on the primary null; supplementary null separate; 100 observed tie-order replicates. |
| 7. Single-airport and H3 | 07 | Remove each airport once. Primary efficiency loss and supplementary surviving-airport damage. Spearman, top-k, degree-matched comparison, partial rank correlation and 2,000 paired bootstrap out-of-bag model comparisons. |

**Attempted swaps per production chain:** AA primary 452,000, AA supplementary 226,000, DL primary 301,200, DL supplementary 150,600, WN primary 358,400, WN supplementary 179,200.

## 3. Inventory

The complete list with file sizes and SHA-256 hashes is in `file_inventory.csv` in this folder.

| Location | Contents | Files |
|---|---|---|
| Project root | Seven notebooks, and `Airline_Network_Resilience_Proposal.pdf` | 8 |
| `Data/raw/` | BTS monthly CSV files for April, May and June 2025 | 3 |
| `Data/Processed/` | Observed node and edge tables, and `network_summary.csv` | 7 |
| `Data/Processed/Nulls/` | Production null networks and 4T similarity benchmarks | 15 |
| `Data/Processed/Removal_Plans/` | Saved targeted rankings and tie-order replicates | 12 |
| `Data/Processed/Resilience/` | Paired random-trial outcomes | 9 |
| `Data/Processed/H3/` | Recorded bootstrap in-bag samples | 3 |
| `Results/Tables/` | Result tables, prefixed by step (01: 4, 02: 8, 03: 34, 04: 51, 05: 10, 06: 19, 07: 17) | 143 |
| `Results/Figures/` | Figures, prefixed by step | 17 |
| `Backups/` | Earlier notebook copies; not used in any analysis | 4 |

**Notebooks:** `Network_Analysis_01_Data_Preparation (1).ipynb`, `Network_Analysis_02_Network_Structure.ipynb`, `Network_Analysis_03_Communities_and_Cohesion.ipynb`, `Network_Analysis_04_Null_Models.ipynb`, `Network_Analysis_05_Removal_Setup.ipynb`, `Network_Analysis_06_Resilience_Metrics.ipynb`, `Network_Analysis_07_Single_Airport_H3.ipynb`.

**Most useful results to read first:**

| Topic | Table |
|---|---|
| H1 verdicts and cells | `06_h1_verdicts.csv`, `06_h1_cells.csv` |
| H2 verdicts, strategy deviation and cells | `06_h2_verdicts.csv`, `06_h2_strategy_deviation.csv`, `06_h2_primary_cells.csv` |
| Tie-order sensitivity | `06_tie_sensitivity_verdict_counts.csv`, `06_tie_sensitivity_value_summary.csv` |
| H3 verdicts and models | `07_h3_verdicts.csv`, `07_h3_model_performance.csv`, `07_h3_partial_correlation.csv` |
| Airport-level loss and measures | `07_single_airport_outcomes.csv`, `03_airport_master.csv` |
| Null structure and precision | `04_null_structural_summary.csv`, `04_expansion_200_cell_assessment.csv` |
| Supplementary null reading | `06_two_null_reading.csv`, `04_modularity_null_comparison.csv` |

## 4. Validation and reproducibility

| Stage | Recorded checks | Result |
|---|---|---|
| Step 3 | 50 | All passed |
| Step 4 pilot | 22 | 21 passed; 1 recorded as not completed (NetworkX comparison) |
| Step 4 remaining analyses | 23 | All passed |
| Step 4 modularity | 10 | All passed |
| Step 5 | 23 | All passed |
| Step 6 | 35 | All passed |
| Step 7 | 76 | All passed |

**Network validation.** All 900 null networks passed exact in- and out-degree, route-count, self-loop and duplicate-route checks, and every reciprocal-pair network has each route's reverse. All were distinct, and none equalled its observed network. Approved similarity limits were met.

**Reproducibility.**

| Check | Result |
|---|---|
| Step 1 networks rebuilt from raw BTS data | Exact match to processed files |
| Step 3 tables across two separate executions | Identical |
| Step 4 long-chain networks regenerated from recorded seeds | All 3,600 chain-checkpoints reproduced |
| Step 5 setup, two complete runs | All 22 outputs identical |
| Step 6 primary-null outcomes against Step 4 records | All 600 networks matched |
| Step 7, two complete runs | All 21 analytical outputs identical |

SciPy results were checked against NetworkX on samples. Accepted Step 2 betweenness and Step 3 participation were reproduced where they were reused.

## 5. Limitations, decisions and unresolved issues

### Limitations

- This is a structural study. It does not measure passengers, capacities, rerouting or operational losses.
- Three airlines are case studies, so there is no inference to airlines in general. Findings are observational.
- Random removal is a baseline, not a model of real disruptions.
- Efficiency loss includes each airport's own pairs, which rises with degree and favours degree-only prediction.
- Airports within a network are not independent, so bootstrap intervals describe stability across airports.
- Community and bridging results vary between Louvain runs; across-run ranges are algorithmic variation, not confidence intervals.
- Null intervals use empirical percentiles and are not confidence intervals. Null networks control degrees, not weights.

### Key methodological decisions

| Decision | Why |
|---|---|
| Directed degree-preserving null is the only null deciding H2 | Approved protocol and revised proposal |
| Binary undirected projection is primary for communities; weighted is supplementary | Consistent with binary topology used for nulls and removals |
| Bridging summarized across 100 Louvain runs | No run reliably reproduces the selected partition |
| Bridging comparisons use degree ≥ 2 | Degree-1 participation is mechanically 0 |
| 200 primary nulls, 100 supplementary | E1 and E2 triggered at 100; expansion approved, stopping at 200 |
| Fixed attempted swaps per chain | Stopping at a fixed number of successes would bias sampling |
| ID-order tie rule is official; 100 tie orders are sensitivity only | Deterministic primary ranking, with reported dependence |
| 0.02 R² Gain threshold | Project-specific practical-effect threshold, not a universal standard |
| Strength-targeted removal not run | Excluded by decision in Steps 5 and 6 |

### Unresolved issues

- **NetworkX comparison not completed.** Its three-edge move cannot act on a perfectly reciprocal network. This is a structural limitation of the comparison and says nothing about the validity of the project's swap methods.
- **E1 remains above 5% at 200 networks** (11 of 144 cells, 7.6%). E2 is 6 of 144 (4.2%). Further expansion was not authorized. Most flagged cells are near collapse or have very narrow intervals.
- **Notebook 04 has not been run from top to bottom in one kernel session.** Later sections were executed with their own setup cells. The saved outputs come from those runs.
- **Notebooks have not been tested on Colab.** Results were produced in one local environment: Python 3.14.5, NetworkX 3.6.1, NumPy 2.4.6, pandas 3.0.5, SciPy 1.18.1. A different NetworkX version can change Louvain partitions.
- **Zero-betweenness ties in nulls** are handled by ID order only, and affect many AA and DL networks at 15% and 20%.
- **"None" in Step 6 deviation tables** means no systematic deviation. Reading with pandas requires `keep_default_na=False`.

## 6. Navigation and reproduction

**Start here:** read Sections 1 and 5 of this document, then the most useful result tables listed in Section 3. Notebooks 06 and 07 hold the hypothesis analyses.

**Notebook order:** 01 → 02 → 03 → 04 → 05 → 06 → 07. Each step reads saved outputs from the previous steps, so each can be reviewed without rerunning earlier ones.

**On Colab.** Open the project folder at `/content/drive/MyDrive/Network Analysis /Data`, keeping the trailing space in `Network Analysis `. The notebooks mount Drive automatically.

**Locally.** Set the environment variable `NETWORK_ANALYSIS_LOCAL_ROOT` to the project root before running a notebook.

**Before rerunning anything:** reviewing does not require reruns. If you do rerun, use a copy of the project, because the notebooks overwrite saved outputs and a different NetworkX version can change Louvain results.

**Approximate local runtimes:** Step 4 pilot and long-chain test 31 minutes; Step 4 modularity 30 minutes; Step 6 metrics 15 minutes; Step 7 about 6 minutes.

**Seeds.** The master seed is 20250401. Child seeds use NumPy `SeedSequence` with recorded spawn keys, stored in the seed registry tables.

## 7. Points to review

**H1**
- Is random removal with 100 orders a fair reference given how strongly hubs dominate AA and DL?
- Does near-total collapse at 5% targeted removal need more explanation in the report?

**H2 and the null models**
- Is the "Not supported" wording clear that it means no systematic deviation under the approved rule, and not that degrees explain resilience?
- How much weight should the floor and zero-width cells receive for AA and DL?
- Primary-null networks lose reciprocity (about 0.70, 0.66 and 0.63). Is it presented clearly that this makes the primary null a strict reference?
- Should the supplementary null reading be discussed as exploratory only?
- Is the ID-order rule adequate given the large zero-betweenness ties in nulls?
- E1 stays above 5% at 200 networks. Is the planned description of those imprecise cells sufficient?

**H3**
- Is "Partly supported" stated carefully, given that the Gain interval includes 0 for all airlines?
- Does the report separate association and predictive improvement from causal claims?
- Is the 0.02 threshold explained as project-specific?
- Should the participation limitations be highlighted, including the HNL counterexample and the low top-10 overlap with loss?
- Are coreness and degree being treated as nearly redundant for AA and DL?

**Across the project**
- Do the limitations appear early enough in the report?
- Are the NetworkX comparison and the untested Colab execution disclosed clearly?
- Is any tie-order, rounding or eligibility decision unclear to a reader who has not seen the protocol?
