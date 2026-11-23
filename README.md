# Structural Resilience and Hub Dependence in US Airline Networks

Zahra Amani Aghbolagh, Seyeddanial Azimi, Farzam Manafzadeh and Kianaz Narehei, MSc Artificial Intelligence

This repository contains the complete final version of our network analysis project: the research paper, the notebooks that produce every result, the data, all result tables and figures, and a separate re-implementation (audit) of the analyses.

- **Paper:** [`03_Revision_and_Audit/Amani_Azimi_Manafzadeh_Narehei_Revised_Paper.pdf`](03_Revision_and_Audit/Amani_Azimi_Manafzadeh_Narehei_Revised_Paper.pdf) (also `.docx`)
- **Audit Report:** [`03_Revision_and_Audit/Audit_Report.pdf`](03_Revision_and_Audit/Audit_Report.pdf) (also `.docx`)
- **Run order and dependencies:** [`02_Optional_Reproducible_Project/RUN_ORDER.md`](02_Optional_Reproducible_Project/RUN_ORDER.md)

## Research questions and hypotheses

We study how the domestic route networks of American Airlines (AA), Delta Air Lines (DL) and Southwest Airlines (WN) respond to the loss of airports.

- **RQ1.** How does the organisation of each network relate to its structural resilience when airports are removed, and does the observed resilience differ from what the airports' degrees alone would produce?
- **RQ2.** Which airport-level measures identify the airports whose individual removal causes the largest loss?

- **H1.** Removing airports in order of degree or betweenness causes more damage than removing the same number of airports at random.
- **H2.** Observed resilience differs systematically from that of random networks with the same degrees.
- **H3.** Airports whose routes span more communities cause larger losses than airports of similar degree.

The decision rules for H1–H3 were fixed before the main experiments. All analyses added later are labelled exploratory.

## Data

US Bureau of Transportation Statistics, *Marketing Carrier On-Time Performance (Beginning January 2018)*, monthly files for April, May and June 2025 ([BTS TranStats](https://transtats.bts.gov/DL_SelectFields.aspx?QO_fu146_anzr=b0-gvzr&gnoyr_VQ=FGK)). The three files contain 1,985,849 flight records; selecting AA, DL and WN as marketing carriers keeps 1,292,785 scheduled flights.

The raw files are included in [`02_Optional_Reproducible_Project/Data/raw/`](02_Optional_Reproducible_Project/Data/raw/) (82–86 MB each, stored as ordinary Git files), so the project can be reproduced without downloading anything else. They are public US government data.

For each airline we build one directed network: airports are nodes, and an arc from *i* to *j* exists if at least one nonstop flight was scheduled during the quarter. The networks have 230 airports and 1,808 routes (AA), 212 airports and 1,506 routes (DL), and 104 airports and 1,792 routes (WN); all three are fully reciprocal and strongly connected.

## Methods in brief

- **Structure and communities:** degree, betweenness, clustering, assortativity, k-cores, and Louvain communities from 100 seeded runs; participation coefficients are averaged over the runs.
- **Removal experiments:** airports are removed by degree, by betweenness (rankings fixed on the intact network) or at random (100 recorded orders), at 5%, 10%, 15% and 20% of the airports. Damage is measured with directed global efficiency, reachability and the largest strongly connected component.
- **Null models:** 200 degree-preserving directed rewirings per airline (primary null) and 100 reciprocity-preserving rewirings (supplementary null).
- **H3:** single-airport removals; partial rank correlation of participation with loss given degree, out-of-bag predictive gain over 2,000 bootstrap samples, and degree-matched comparisons.
- **Exploratory analyses:** Experiment A (1% and 2% removal), Experiment B (structure versus resilience inside the null ensembles, with permutation tests and Benjamini–Yekutieli adjustment), Experiment C (cross-validated ridge models), full-curve robustness scores, hub-captive airports, adaptive attacks, monthly networks and a loss decomposition based on harmonic centrality.

## Main findings

- **H1 is supported** for all three airlines: targeted removal is far more damaging than random removal. The effect differs sharply: three hub closures halve the efficiency of AA and DL, whereas WN needs ten.
- The main reason is simple: a quarter of AA's airports and a third of DL's have a single route partner, and removing the top four or five hubs leaves more than 40% of their airports with no route at all.
- **H2 is not supported** for any airline. For AA and DL the test has little power, because targeted removal drives real and randomized networks alike to near-zero efficiency; a full-curve robustness score suggests that WN's real arrangement is slightly more fragile than random.
- **H3 is partly supported** for all three airlines: degree identifies the most damaging single-airport closures better than community participation, which adds association but no reliable predictive value.

See the paper for the full results, figures and limitations.

## Repository structure

```
02_Optional_Reproducible_Project/      the reproducible project (folder name kept from the original submission package)
├── Network_Analysis_01_Data_Preparation.ipynb … Network_Analysis_07_Single_Airport_H3.ipynb
├── Network_Analysis_09_Structure_Resilience.ipynb
├── supplementary_helpers.py           shared code for NB06 Section 6.7, NB07 Section 7.8 and NB09
├── requirements.txt                   pinned Python environment
├── RUN_ORDER.md                       execution order and dependencies
├── Generator_Settings.json            settings of the null-network generator
├── Data/raw/                          BTS input files
├── Data/Processed/                    networks, null networks, removal plans, resilience outcomes, H3 bootstrap samples
└── Results/                           all result tables and figures (Tables/, Figures/, Supplementary/)
03_Revision_and_Audit/
├── Amani_Azimi_Manafzadeh_Narehei_Revised_Paper.docx / .pdf
├── Audit_Report.docx / .pdf
├── figures/                           the five figures of the paper
├── outputs/                           tables and arrays recomputed by the audit scripts
└── scripts/                           audit scripts a01–a10, figure script a09, document builder, package.json
```

There is no NB08: stage 08 is Section 6.7 of NB06.

## Reproducing the analysis

1. Create an environment with **Python 3.13.5** and install the pinned packages:
   ```
   python -m pip install -r 02_Optional_Reproducible_Project/requirements.txt
   ```
2. Open the notebooks from `02_Optional_Reproducible_Project/` (or set the environment variable `NETWORK_ANALYSIS_LOCAL_ROOT` to that folder) and run them in the order given in [`RUN_ORDER.md`](02_Optional_Reproducible_Project/RUN_ORDER.md): NB01 → NB02 → NB03 → NB04 → NB05 → NB06 (including Section 6.7) → NB09 → NB07. Start each notebook in a fresh kernel and run it from top to bottom. A full run takes about three hours, two of them in NB04.
3. NB07 begins with a version check that warns if the installed packages differ from `requirements.txt`.

All results in the repository come from a full run on 23 November 2026 with the pinned environment. The Louvain runs depend on the NetworkX version: with the same seeds, NetworkX 3.6.1 and 3.7 give different partitions in 65 of the 300 binary runs, so the pinned version is needed to reproduce the reported values exactly. Only Windows 11 was tested.

## Audit and documents

The scripts in `03_Revision_and_Audit/scripts/` re-implement the analyses from their specifications and compare the results with the project outputs; the Audit Report describes what was checked, what was corrected, what was not re-run, and the limitations of the audit. The audit scripts use the same Python packages as the notebooks.

The paper and the Audit Report are generated from `paper_content.js` and `audit_content.js`:

```
cd 03_Revision_and_Audit/scripts
npm install
npm run build:paper
npm run build:audit
```

The PDFs were exported from the DOCX files with Microsoft Word.

## Citation

Amani Aghbolagh, Z., Azimi, S., Manafzadeh, F. and Narehei, K. (2026). *Structural Resilience and Hub Dependence in US Airline Networks.* https://github.com/zahraamani7065/airline-network-resilience
