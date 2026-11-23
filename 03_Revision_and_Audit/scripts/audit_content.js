// Content of the audit report (same block format as paper_content.js).
const TITLE = "Audit Report: Verification and Revision of the Airline Network Resilience Project";
const AUTHORS = ["Prepared for: Amani, Azimi, Manafzadeh, Narehei", "Date: 23 November 2026"];
const REFS = {};
const B = [];
const h1 = (t) => B.push({ type: "h1", text: t });
const p = (t) => B.push({ type: "p", text: t });
const li = (t) => B.push({ type: "bullet", text: t });
const table = (caption, header, rows, widths) => B.push({ type: "table", caption, header, rows, widths });

h1("1. Scope and approach");
p("This audit checked the whole project: the data preparation, the three networks, all null models, the H1–H3 experiments, Experiments A–C, the figures and tables, and the paper. We did not assume that the existing outputs were correct. Instead we wrote a new set of scripts (03_Revision_and_Audit/scripts, files a01–a10) that re-implement the analyses from their specifications instead of reusing the notebook code. They start from the raw BTS files and reuse the saved null graphs, random removal orders, Louvain partitions, bootstrap samples and recorded seeds, so they check the calculations rather than the random draws or the design choices. Section 6 lists the steps that were not re-run. The data were not modified. The project code changed in three ways, none of which changes a computed value: an exploratory Section 7.9 was appended to NB07 during the H3 revision; the unpinned %pip install cells in NB07 were replaced by an environment note and a version check, and one printed file name was corrected; and supplementary_helpers.py now uses np.trapezoid when NumPy provides it and np.trapz otherwise, because recent NumPy versions no longer provide np.trapz (all 16,254 AUC values are unchanged). A full rerun of all notebooks in a newer environment (23 November) reproduced exactly every result that does not depend on the Louvain runs. Individual Louvain runs changed, and so did the values derived from them (participation, the H3 statistics, null-network modularity and the Experiment B tests that use it), without changing any verdict or conclusion. The reported values were updated to this rerun (Section 4).");

h1("2. Summary");
p("We found no programming or methodological error that changes any number, verdict or conclusion. Every quantity we recomputed matches the project outputs to within floating-point precision (the original outputs of 19 November, or the final outputs of 23 November for the scripts re-run against them; see Table A1), except permutation-based p-values, which agree up to Monte Carlo error. The problems we found are in how the results were reported: one omission, one rounding error, one selectively reported analysis, an understated floor effect, weak figures for AA and DL, and a thin literature base. We fixed all of them in the revised paper. We also added several clearly labelled exploratory analyses. They support the original verdicts and give a much clearer explanation of why AA and DL collapse so early.");

h1("3. What was re-implemented and checked");
table("Table A1. Re-implementation from the specifications. “Match” means equal to the project output within floating-point precision (largest difference about 10^{−14}) unless stated otherwise. Rows a03, a04 and a07 were re-run on 23 November against the final outputs; the other rows compare with the original outputs of 19 November, which are identical for those components.",
  ["Component", "What was recomputed", "Result"],
  [["Data (a01)", "Raw records, carrier filter, duplicates, self-loops, diverted-only routes, edge lists and weights", "Match (1,985,849 records; 1,292,785 flights; edge lists identical)"],
   ["Table 1 (a01)", "Density, centralisation, Gini, clustering, transitivity, assortativity, path length, efficiency, cores", "Match"],
   ["Null graphs (a10)", "Degree preservation, simplicity, reciprocity, uniqueness of all 900 graphs", "All pass; directed reciprocity 0.70/0.66/0.62 as reported"],
   ["Rankings (a02, a05)", "Degree and betweenness orders for all 903 networks", "Identical orders and removed sets"],
   ["H1 (a02, a05)", "Targeted and paired random outcomes; percentile rule; verdicts", "Match; all six strategy verdicts Supported"],
   ["H2 (a05)", "144 null intervals and positions; 108 decision cells; verdicts", "Match; 77 within, 19 above, 12 below; 20 zero-width, 38 ≤ 0.001"],
   ["Experiment A (a05)", "1% and 2% removal for all networks", "Match"],
   ["Single-airport loss (a03)", "Loss and survivor damage for every airport", "Match"],
   ["Louvain and participation (a03)", "Modularity of the 100 saved runs; participation; 100 fresh runs with new seeds", "Match; fresh runs give the same best Q to within 0.003 and ARI to within about 0.02"],
   ["H3 (a03)", "Partial rank correlation, 2,000 OOB bootstraps, degree bins, verdicts", "Match; all three Partly supported"],
   ["Experiment B (a07)", "Structural predictors, AUCs, 756 Spearman tests, new permutations, BY", "ρ identical; reciprocal family 33 significant (same); directed 37 in the audit vs 42 in the project (Monte Carlo)"],
   ["Experiment C (a04)", "Repeated stratified CV ridge models", "Match"]],
  [2000, 4100, 2972]);

h1("4. Issues found and corrections made");
li("Omission in the H2 results. The original text listed the observed values outside their null interval but left out AA betweenness targeting at 5%, which is also below its interval. Corrected in Section 5.3; Figure 3 now shows every cell.");
li("Selective reporting of Experiment C. The original paper reported only the spline-degree baseline, where participation adds nothing. With a linear log-degree baseline, participation improves held-out R² for AA and DL in all five repeats, by a median of about 0.02. Both results are now reported, with the interpretation that participation mostly stands in for the nonlinear effect of degree.");
li("Understated floor effect in H2. All 38 decision cells with a null interval no wider than 0.001 are AA or DL targeted cells. In practice the H2 verdict for these two airlines rests mainly on random removal. The revised paper says this directly, shows it in Figure 3 and adds a full-curve robustness score that is less affected by the floor (Table 2). The verdict itself is unchanged.");
li("Monte Carlo-dependent q-values. Both the project and our rerun use 19,999 permutations per test, but from different random streams, so permutation p-values differ by Monte Carlo error while the 756 Spearman coefficients are identical. For the WN full-window test in Experiment B, one permutation in the project was as extreme as the observed value (p = 2/20,000) and none in our rerun (p = 1/20,000, the smallest possible), so the BY-adjusted q-value was 0.0082 in the project and 0.0044 in our rerun. For the same reason the number of significant directed-family tests was 42 in the project and 37 in our rerun (37 against 35 before the full rerun, which changed the null-network modularity values): five directed tests lie close to q = 0.05 and fall on different sides of it. All 378 reciprocal-family tests agree. The paper therefore reports q < 0.01 and only the reciprocal-family count (33).");
li("Uninformative figures. The original Figures 1 and 2 used only the four fixed removal levels, so the AA and DL panels showed flat lines at zero. They were replaced by full-resolution removal curves (Figure 1), a mechanism figure (Figure 2) and an overview of all H2 cells (Figure 3). Figure 3 of the original (Experiment B) was restyled and now also shows the hub-captive count. A new figure for H3 was added (Figure 5).");
li("Literature and references. The original cited six sources, only three of them research papers, and none on airline network robustness. Fifteen references were added, each checked against the publisher, DOI or arXiv record. During checking we also found that the Lordan et al. survey appeared in the Journal of Transport Geography, not the Journal of Air Transport Management as suggested in our earlier evaluation.");
li("Presentation. The original had no abstract, used internal workflow terms (“Steps 1–3 and 5–7”, “Colab remains untested”), reported values to six decimals and mentioned the exclusion of strength targeting without giving a reason. The paper was fully rewritten with an abstract, a related-work section, a methods section that can be read without the notebooks, rounded values and a verification paragraph.");
li("Library-version dependence of Louvain runs. The original outputs were produced with NetworkX 3.6.1 and NumPy 1.26.4, under Python 3.11.14 for the main notebooks (as recorded by NB03, NB04 and NB07) and Python 3.12.14 for the supplementary stages 08–10. The full rerun used Python 3.13.5, NetworkX 3.7 and NumPy 2.5.5. The analysis code was unchanged apart from the NumPy compatibility change described in Section 1, yet 17, 34 and 14 of the 100 binary Louvain runs gave different partitions, and the best modularity of 249 of the 900 null networks changed by up to 0.006. Best partitions, weighted runs and all verdicts were unchanged. Ten rounded values in the paper (in twelve places) changed and were updated. Permutation p-values not involving modularity were reproduced exactly across NumPy versions.");
li("Rounding error in the null-model description. The paper gave the mean reciprocity of the directed null networks as 0.70, 0.66 and 0.63. The WN value is 0.6249, which rounds to 0.62. Corrected in Section 4.3.");
li("Coarse early AUC in Experiment B. The early window covers only two removal points per airline and is interpolated in between. We kept the original measure, because changing it would alter a completed analysis, but the full-resolution curves now available would allow a finer version.");

h1("5. Analyses added during the revision (all exploratory)");
li("Full-curve robustness score R_{E} and K_{50} for the observed networks, all 900 null graphs and 100 random orders (a02, a06). Result: K_{50} = 3, 3 and 10; AA and DL inside both null ranges; WN below all 300 nulls for both targeted strategies.");
li("Hub-captive airports (a06, a08). Removing the top four or five hubs cuts off 43–45% of AA and DL airports; in WN, removing the top three hubs isolates none and the top five isolate three. Within the reciprocal nulls the captive count is almost perfectly related to early retention (ρ = −0.99 for AA and DL), partly by construction, because cut-off airports lose all their access, and moderately related to assortativity (ρ = −0.55 and −0.50). It is therefore consistent with, and partly accounts for, the Experiment B assortativity result.");
li("Adaptive attacks (a06). Recalculating the rankings after each removal changes R_{E} by less than 0.01 and K_{50} not at all. Reported in one sentence.");
li("Monthly networks and a route-frequency threshold (a06). K_{50} is 3, 3 and 9–10 in every month and with routes of fewer than 13 flights removed, so the airline contrast is not an artefact of pooling the quarter.");
li("Sensitivity of H3 to Louvain instability (a03). Using single Louvain runs instead of the 100-run average, the partial correlation ranges from 0.19 to 0.54 (AA), 0.20 to 0.62 (DL) and 0.07 to 0.40 (WN).");
li("Loss decomposition and neighbour-degree sensitivity of H3 (NB07, Section 7.9). For 388 of the 419 airports in the H3 sample, removal damages no path between other airports, so the loss is exactly proportional to harmonic centrality. Adding mean neighbour degree as a second control lowers the partial correlation between participation and loss from 0.49 to 0.30 [0.16, 0.43] for AA, from 0.56 to 0.43 [0.26, 0.58] for DL and from 0.28 to 0.06 [−0.14, 0.33] for WN. The degree-only version reproduces the official H3 values exactly, and the H3 verdicts are unchanged.");
p("We considered and did not add flight-weighted outcomes, strength-targeted removal, Burt's constraint as an alternative bridging measure, and additional null draws. Each would have added a new set of choices or tests without addressing a question the paper needs to answer, and the H3 results already show that degree dominates single-airport loss.");

h1("6. What was not re-run");
li("Generation of the null graphs (the swap chains). We verified the constraints of all 900 saved graphs but did not replay the chains.");
li("The precision diagnostics E1 and E2 (11 and 6 flagged cells of 144). These are quoted from the project tables.");
li("The 100 tie-order sensitivity replicates for H1. The project table reports Supported in 100 of 100 replicates for every strategy.");
li("Best Louvain modularity of the 900 null graphs, which Experiment B uses as a predictor. We spot-checked 10 reciprocal nulls per airline, and all matched exactly, both against the original values and, after the full rerun, against the final values.");
li("Pilot and chain-length diagnostics, weighted participation and other supplementary tables that the paper does not use.");

h1("7. Limitations of this audit");
li("Independence. The re-implementation was written by the project team from the same specifications as the notebooks. It can detect programming errors, but not errors in the specifications or in the design choices themselves.");
li("Shared random inputs. The audit reuses the saved null graphs, random removal orders, Louvain partitions and bootstrap samples, so it checks the calculations made with them, not the random draws. The swap chains that generated the null graphs were not replayed (Section 6).");
li("Software environments. Scripts a03, a04 and a07 and the spot checks in a06 were re-run on 23 November in the pinned environment of requirements.txt (Python 3.13.5, NetworkX 3.7). The other audit outputs (a01, a02, a05, the remaining a06 analyses, a08 and a10) were computed on 22 November in an earlier environment whose versions were not recorded. Its Louvain results matched those of NetworkX 3.6.1, not 3.7. These outputs do not use Louvain community detection and agree with the final outputs to within floating-point precision.");
li("Monte Carlo variation. Our permutation p-values come from a random stream independent of the project's, so tests close to q = 0.05 can fall on different sides of it (Section 4). The paper reports only conclusions that agree between the two streams.");
li("Exploratory analyses. The analyses added during the revision (Section 5) were computed once and are not part of the pre-specified tests. Only Windows 11 with the pinned Python 3.13.5 environment was tested.");

h1("8. Remaining items before submission");
li("Done: reference [20] of the paper now gives the repository link (https://github.com/zahraamani7065/airline-network-resilience).");
li("Read the paper as a team and adjust anything that does not match how you would explain the work in an oral discussion.");
li("Check the course rules on length (the paper has about 5,900 words including the abstract, on 14 A4 pages) and on disclosing the use of AI tools.");
li("Done (23 November): the software environment is pinned in requirements.txt (Python 3.13.5 and seven packages), the run order is documented in RUN_ORDER.md, and the %pip cells in NB07 were replaced by an environment note and a version check that installs nothing. Without rerunning any notebook, we checked the pinned environment both in the existing installation and in a new, clean environment installed from requirements.txt (test T3). In both, all versions matched and pip reported no conflicts. The 300 binary Louvain runs of NB03 (compared as partitions), the best modularity of 60 null networks, all 756 Experiment B permutation p-values and all 16,254 AUC values were reproduced exactly, and NB07 Sections 7.8 and 7.9 reproduced their saved outputs byte for byte. With NetworkX 3.6.1, but a different Python and NumPy, the same code instead reproduces all 300 original binary Louvain runs of 19 November, so the NetworkX version alone accounts for the change in these runs. The changes in null-network modularity come from the same Louvain routine and are attributed to the same cause, but were not tested separately.");
li("Done: the repository includes the audit scripts (03_Revision_and_Audit/scripts), including the exploratory analyses a06 and a08, so that every number in the paper has a runnable source.");

h1("9. Files");
table("Table A2. Files produced by the audit and the revision.",
  ["Path (inside 03_Revision_and_Audit unless stated)", "Content"],
  [["Amani_Azimi_Manafzadeh_Narehei_Revised_Paper.docx / .pdf", "Revised paper"],
   ["Audit_Report.docx / .pdf", "This report"],
   ["scripts/a01–a08, a10, audit_common.py", "Re-implementation checks and exploratory analyses (Python; environments in Section 7)"],
   ["scripts/a09_figures.py", "Figures of the revised paper"],
   ["scripts/build_paper.js, paper_content.js, audit_content.js, package.json", "Document generation (Node.js with docx 9.5.1; PDFs exported from Word)"],
   ["outputs/", "All recomputed tables (CSV) and cached removal outcomes (NPZ); a03, a04, a07 and the a06 spot checks regenerated on 23 November"],
   ["figures/", "Figures 1–5 of the revised paper (300 dpi PNG); fig4_h3_loss_degree.png is Figure 5 and fig5_expB_assortativity.png is Figure 4"],
   ["02_Optional_Reproducible_Project/requirements.txt, RUN_ORDER.md", "Pinned software environment and notebook run order"]],
  [4600, 4472]);

module.exports = { TITLE, AUTHORS, REFS, B };
