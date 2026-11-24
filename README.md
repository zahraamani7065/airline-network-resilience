
<p align="center">
  <img src="https://upload.wikimedia.org/wikipedia/commons/d/d0/Seal_of_the_University_of_Bologna.svg" alt="University of Bologna" width="150">
</p>

<h1 align="center">
Structural Resilience and Hub Dependence in US Airline Networks
</h1>

<p align="center">
  <strong>University of Bologna</strong><br>
  MSc Artificial Intelligence — Network Analysis<br>
  Academic Year 2026/2027
</p>

<p align="center">
  Zahra Amani Aghbolagh · Seyeddanial Azimi · Farzam Manafzadeh · Kianaz Narehei
</p>

---

## Overview

This repository contains our Network Analysis research project investigating structural resilience and hub dependence in the domestic route networks of three major US airlines.

The repository includes the final research paper, analysis notebooks, raw and processed datasets, experimental results, figures and a separate computational audit.

## Project Documents

- **Final research paper:** [Final Report](04_Final_Report/)
- **Computational audit:** [Audit Report](03_Revision_and_Audit/Audit_Report.pdf)
- **Reproducibility instructions:** [RUN_ORDER.md](02_Optional_Reproducible_Project/RUN_ORDER.md)

The manuscript in `04_Final_Report/` is the authoritative final version. Earlier manuscript versions and computational audit materials are retained in `03_Revision_and_Audit/` for transparency and reproducibility.

## Research Questions and Hypotheses

We investigate how the domestic route networks of American Airlines (AA), Delta Air Lines (DL) and Southwest Airlines (WN) respond to simulated airport removals.

### Research Questions

- **RQ1.** How does the organisation of each network relate to its structural resilience when airports are removed, and does the observed resilience differ from what the airports' degrees alone would produce?
- **RQ2.** Which airport-level measures identify the airports whose individual removal causes the largest loss?

### Hypotheses

- **H1.** Removing airports in order of degree or betweenness causes more damage than removing the same number of airports at random.
- **H2.** Observed resilience differs systematically from that of random networks with the same degrees.
- **H3.** Airports with more evenly distributed routes across communities cause larger losses than airports of similar degree, as assessed by community participation.

The hypotheses are evaluated using the decision rules documented in the analysis notebooks.

Hub concentration, clustering, assortativity, cores and communities are investigated as potential explanations of resilience rather than as independent descriptive objectives.

Supplementary analyses are distinguished from the primary hypothesis tests and interpreted as exploratory evidence.

## Data

**Source:** US Bureau of Transportation Statistics (BTS), *Marketing Carrier On-Time Performance (Beginning January 2018)*, April–June 2025.

[BTS TranStats Dataset](https://transtats.bts.gov/DL_SelectFields.aspx?QO_fu146_anzr=b0-gvzr&gnoyr_VQ=FGK)

The three monthly CSV files contain 1,985,849 flight records. Filtering by marketing carrier retains 1,292,785 scheduled flights, including services operated by regional partners.

| Airline | Scheduled flights | Airports | Directed routes |
|---|---:|---:|---:|
| American Airlines (AA) | 514,206 | 230 | 1,808 |
| Delta Air Lines (DL) | 418,790 | 212 | 1,506 |
| Southwest Airlines (WN) | 359,789 | 104 | 1,792 |

The original datasets are included in [`Data/raw/`](02_Optional_Reproducible_Project/Data/raw/).

Data validation checks found:

- No missing essential fields.
- No duplicate records under the applied duplicate definitions.
- No self-loops or diversion-only routes.
- Coverage of all 91 days for each airline.

Cancelled flights are retained because the project investigates scheduled network structure.

## Network Construction

We construct three monomodal, directed and weighted networks, one per airline.

- **Nodes:** Airports identified by BTS airport IDs.
- **Directed edges:** Scheduled nonstop routes between airports.
- **Weights:** Number of scheduled flights on each directed route during the quarter.

All three observed networks are fully reciprocal and strongly connected.

Structural measures such as degree, clustering, transitivity, assortativity, k-cores and communities are computed on the undirected binary projection. Path-based measures are computed on the directed graph.

Flight frequencies are used descriptively, while the resilience experiments use binary connectivity.

The project measures structural accessibility rather than actual passenger disruption, economic losses or operational recovery.

## Methodology

### Network Structure and Communities

The structural analysis includes:

- Degree distributions and hub concentration.
- Degree and betweenness centrality.
- Freeman degree centralisation.
- Gini coefficient of scheduled departures.
- Clustering and transitivity.
- Shortest-path lengths and global efficiency.
- Degree assortativity.
- K-core decomposition.
- Louvain community detection.
- Community participation coefficients.

Louvain modularity maximisation is performed at resolution 1 using 100 seeded runs. Partition agreement is evaluated using the adjusted Rand index (ARI), and participation coefficients are averaged across runs.

The same modularity optimisation procedure is applied to observed and randomised networks.

### Airport Removal Experiments

Airports are removed using three strategies:

- Degree-targeted removal.
- Betweenness-targeted removal.
- Random removal using 100 recorded orders.

The primary experiments use nominal removal fractions of 5%, 10%, 15% and 20%.

Structural damage is measured through:

- Directed global efficiency (compactness).
- Reachability.
- Largest strongly connected component (SCC).

The original network size is retained in the normalisation so that removed airports contribute to lost accessibility.

Targeted rankings are fixed on each intact network for the primary experiments. Adaptive targeting is examined separately.

### Degree-Preserving Null Models

Each airline is compared against:

- 200 directed degree-preserving randomised networks.
- 100 degree- and reciprocity-preserving randomised networks.

A total of 900 null networks are generated.

The randomisation procedures preserve degree sequences while changing the arrangement of connections. Self-loops and duplicate edges are rejected.

Independently seeded chains, pilot diagnostics and longer-chain comparisons are used to assess practical ensemble stability.

Uniform sampling of the entire fixed-degree graph space is not claimed.

The reciprocal null provides a more closely matched benchmark because all observed networks are fully reciprocal.

### Single-Airport Criticality

Single-airport removal experiments are conducted for all 546 airport–airline instances.

The primary H3 analysis considers the 419 instances with at least two route partners.

The additional contribution of community participation is evaluated through:

- Partial rank correlation controlling for degree.
- Out-of-bag predictive improvement over 2,000 bootstrap samples.
- Degree-matched comparisons.
- Sensitivity analyses using alternative degree baselines.

Efficiency loss is decomposed into own-access loss associated with the removed airport and survivor damage experienced by the remaining airports.

### Supplementary Analyses

Additional exploratory and sensitivity analyses include:

- Experiment A: early removal at nominal 1% and 2%.
- Experiment B: structural associations with resilience within degree-preserving null ensembles.
- Experiment C: cross-validated ridge models.
- Early-window and longer-window efficiency AUC.
- Full-sequence robustness scores.
- Hub-captive airport analysis.
- Adaptive centrality-targeted removal.
- Monthly network reconstruction.
- Minimum flight-frequency threshold sensitivity.
- Harmonic-centrality-based efficiency loss decomposition.

Experiment B uses permutation tests and Benjamini–Yekutieli adjustment for multiple comparisons.

## Main Findings

### H1 — Supported for All Three Airlines

Targeted airport removal causes substantially greater structural damage than random removal.

K50 denotes the first removal count at which efficiency falls to or below half its intact value.

| Airline | Degree-targeted K50 | Median random K50 |
|---|---:|---:|
| AA | 3 | 60.5 |
| DL | 3 | 52.5 |
| WN | 10 | 30 |

American Airlines and Delta Air Lines experience rapid efficiency collapse, whereas Southwest Airlines degrades more gradually.

### Hub Dependence and Structural Redundancy

| Measure | AA | DL | WN |
|---|---:|---:|---:|
| Airports with one route partner | 55 | 70 | 2 |
| Percentage of airports | 23.9% | 33.0% | 1.9% |
| Degree centralisation | 0.767 | 0.703 | 0.681 |
| Innermost k-core share | 7.4% | 8.0% | 26.9% |

Removing the five highest-degree airports isolates 104 AA airports. Removing the four highest-degree airports isolates 91 DL airports.

In contrast, removing the three highest-degree WN airports isolates none.

These findings support hub captivity as a structural mechanism explaining part of the observed vulnerability, although network size and density also differ.

### H2 — Not Supported Under the Primary Decision Rule

The primary hypothesis test does not establish systematic differences between observed and degree-preserving randomised networks.

For AA and DL, both observed and randomised networks approach the efficiency floor rapidly, limiting the discriminatory ability of the primary comparison.

Supplementary comparisons at nominal 1% and 2% degree-targeted removal show that all six observed efficiency retention values fall within the corresponding reference intervals of both null families.

These findings support a degree-based explanation without proving that degree alone determines resilience.

Additional exploratory findings indicate that:

- Observed modularity exceeds the reciprocal-null reference intervals.
- Less negative assortativity is associated with greater resilience within degree-matched AA and DL ensembles.
- WN's observed full-sequence targeted robustness is below every corresponding sampled null score under both targeted strategies.

These results suggest that higher-order topology matters without establishing independent causal effects of individual structural properties.

### H3 — Partially Supported for All Three Airlines

Community participation is associated with airport criticality, particularly for AA and DL, but provides limited reliable predictive improvement beyond degree.

| H3 outcome | AA | DL | WN |
|---|---:|---:|---:|
| Partial rank correlation | 0.49 | 0.56 | 0.28 |
| Median predictive R² gain | 0.040 | 0.026 | 0.003 |
| Conditions satisfied | 2/3 | 2/3 | 1/3 |
| Verdict | Partial | Partial | Partial |

Degree and betweenness identify most of the ten airports producing the largest total efficiency losses.

Own-access loss accounts for approximately 82%, 77% and 98% of summed single-airport losses in AA, DL and WN respectively.

Survivor damage is concentrated among relatively few airports.

See the [final research paper](04_Final_Report/) for the complete results, mathematical definitions, figures and discussion.

## Validity and Limitations

The project explicitly distinguishes structural accessibility from operational airline performance.

Principal limitations include:

- Quarterly aggregation does not guarantee time-feasible passenger connections.
- Flight frequencies, seat capacity and passenger demand are not incorporated into the removal experiments.
- Airport removals do not model rerouting or recovery.
- Three airlines in one quarter constitute comparative case studies rather than a representative sample.
- Differences in network size and density limit attribution to network design alone.
- Early efficiency collapse limits the primary H2 comparison.
- Uniform exploration of the complete fixed-degree graph space is not guaranteed.
- Louvain partitions exhibit variability across runs.
- Airport-level observations are structurally dependent.

Bootstrap and held-out prediction results are interpreted as within-network stability diagnostics rather than population-level statistical inference.

The primary percentile-based hypothesis rules are operational reference comparisons, not tests calibrated to an overall 5% significance level.

Monthly network reconstruction and minimum flight-frequency threshold sensitivity analyses support the main airline resilience contrast.

## Repository Structure

```text
airline-network-resilience/
│
├── 02_Optional_Reproducible_Project/
│   ├── Network_Analysis_01_Data_Preparation.ipynb
│   ├── Network_Analysis_02_Network_Structure.ipynb
│   ├── Network_Analysis_03_Communities_and_Cohesion.ipynb
│   ├── Network_Analysis_04_Null_Models.ipynb
│   ├── Network_Analysis_05_Removal_Setup.ipynb
│   ├── Network_Analysis_06_Resilience_Metrics.ipynb
│   ├── Network_Analysis_07_Single_Airport_H3.ipynb
│   ├── Network_Analysis_09_Structure_Resilience.ipynb
│   ├── supplementary_helpers.py
│   ├── requirements.txt
│   ├── RUN_ORDER.md
│   ├── Generator_Settings.json
│   ├── Data/
│   │   ├── raw/
│   │   └── Processed/
│   └── Results/
│       ├── Tables/
│       ├── Figures/
│       └── Supplementary/
│
├── 03_Revision_and_Audit/
│   ├── Earlier manuscript versions
│   ├── Audit_Report.pdf
│   ├── figures/
│   ├── outputs/
│   └── scripts/
│
├── 04_Final_Report/
│   └── Final research paper
│
├── .gitattributes
├── .gitignore
└── README.md
```

The original directory names are retained for compatibility with the analysis notebooks and submission package.

There is no separate NB08: stage 08 is implemented in Section 6.7 of NB06.

## Reproducing the Analysis

### Requirements

- Python 3.13.5
- NetworkX 3.7
- Packages specified in `requirements.txt`

Install the pinned dependencies from the repository root:

```bash
python -m pip install -r 02_Optional_Reproducible_Project/requirements.txt
```

### Notebook Execution Order

Open the notebooks from `02_Optional_Reproducible_Project/`, or set the environment variable `NETWORK_ANALYSIS_LOCAL_ROOT` to that folder.

Run the notebooks in the following order:

```text
NB01 → NB02 → NB03 → NB04 → NB05 → NB06 → NB09 → NB07
```

Include Section 6.7 of NB06.

Start each notebook in a fresh kernel and execute all cells from top to bottom.

Detailed dependencies and execution instructions are documented in [RUN_ORDER.md](02_Optional_Reproducible_Project/RUN_ORDER.md).

A complete run previously required approximately three hours, with most of the computational cost associated with null-model generation. Execution time depends on the hardware.

### Environment and Reliability

The saved final notebook results were generated on 23 November 2026 using the pinned environment.

All randomised procedures use recorded seeds.

Louvain results depend on the NetworkX version. With identical seeds, NetworkX 3.6.1 and 3.7 produced different partitions in 65 of the 300 binary runs, although the hypothesis verdicts remained unchanged.

The pinned environment should therefore be used to reproduce the reported values.

NB07 includes a package-version check.

The original execution environment was tested on Windows 11.

## Computational Audit

The scripts in [`03_Revision_and_Audit/scripts/`](03_Revision_and_Audit/scripts/) provide a separate implementation of the analyses and compare their outputs against the original notebook results.

The audit covers:

- Raw-data aggregation.
- Network construction and structural measures.
- Null-model constraints.
- Airport removal outcomes.
- Hypothesis decision rules.
- Single-airport criticality.
- Supplementary resilience analyses.
- Numerical consistency and version sensitivity.

The audit reproduces the principal structural results and H1–H3 verdicts. Independent permutation runs reproduce the correlations, with 99.0% agreement in adjusted significance decisions.

The [Audit Report](03_Revision_and_Audit/Audit_Report.pdf) documents the verification procedures, corrections, limitations and analyses that were not fully rerun.

The audit scripts use the same Python dependencies as the original notebooks.

## Final Report and Earlier Documents

The final research paper is maintained in LaTeX and is available in [`04_Final_Report/`](04_Final_Report/).

Earlier manuscript versions and the original JavaScript and DOCX document-building workflow are retained in `03_Revision_and_Audit/` for historical reproducibility.

These earlier documents are not the authoritative final research paper.

The computational audit remains available as supplementary verification documentation.

## Citation

Amani Aghbolagh, Z., Azimi, S., Manafzadeh, F. and Narehei, K. (2026). *Structural Resilience and Hub Dependence in US Airline Networks*. Network Analysis project, MSc Artificial Intelligence, University of Bologna.

https://github.com/zahraamani7065/airline-network-resilience

## Acknowledgements

This project was developed as part of the Network Analysis course taught by Professor Saverio Giallorenzo at the University of Bologna.

The project uses publicly available flight records from the US Bureau of Transportation Statistics.
