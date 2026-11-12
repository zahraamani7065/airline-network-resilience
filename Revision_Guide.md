# Revision guide and expert review

## Scope and source access

All three requested sources were accessed. The Claude artifact is the project handoff. GitHub HEAD and the local repository both resolve to 46c454da8ea5986419e451fa1ec8c401151d21e1. The teacher's Network Analysis page was checked on 12 November 2026: https://saveriogiallorenzo.com/teaching/#na.

The supplied Teammate_Project_Review_Instructions.pdf is a review brief, not a completed teammate review containing corrections. Its checklist was used to assess the work. Its review-stage instructions not to write the report were not treated as overriding the user's explicit request to finalize it. The supplied report.pdf reproduces the Claude handoff as images; it is not a previous academic report. Original project files and synced course materials remain unchanged.

## Overall assessment

Ready after minor corrections, now applied in this separate copy. The approved research design and numerical findings are defensible within their stated structural scope. No new hypothesis, removal strategy, null-model family or decision threshold was introduced. H1 remains supported, H2 not supported and H3 partly supported for each airline. These verdicts require the qualifications in the report; the labels alone are not an adequate conclusion.

## Exact changes by step

Cell references below use the original zero-based notebook indices. A new opening revision note shifts the corresponding final cell index by one. The machine-readable code_changes.json and exact_changes.diff contain every changed original cell, including the complete replacement code. All seven complete updated notebooks are supplied, rather than only fragments.

1. **Step 1, cell 1:** replaced the unconditional Google Colab import and hardcoded data location with the same environment-variable option used by later steps, plus current-project-folder detection and the original Colab fallback. This fixes the handoff's unsupported claim that every notebook already runs locally. **Cell 11:** added assertions for essential-field completeness and positive scheduled-flight counts before the existing filtering. Current data pass; future invalid records now stop execution rather than being silently removed. Counts and constructed networks are unchanged.

2. **Step 2, cell 2:** applied the same path selection. Degree, strength, Gini, centralization, centrality, clustering, transitivity and connectivity calculations are unchanged. The report now explains why average clustering and transitivity differ rather than treating them as synonyms.

3. **Step 3, cell 2:** added current-project-folder detection and normalized the environment-variable path. No changes to Louvain seeds, resolution, best-partition selection, weighted projection, participation averaging, degree eligibility or k-core calculations. The complete rerun reproduces the original community results within numerical tolerance.

4. **Step 4, cell 2:** applied the consistent local-path handling. Historical markdown saying later steps had not started is explicitly labelled as a historical stage note, preventing it from being mistaken for current status. Null generation, fixed attempted-swap lengths, pilot diagnostics, expansion cap, reciprocity controls and thresholds are unchanged. This notebook remains a complete generation workflow, not a falsely labelled validated end-to-end rerun. Its cached ensembles were audited independently; the historical generator was not rerun in full.

5. **Step 5, cell 2:** applied consistent local-path handling. All removal levels, half-up integer rounding, rankings, pairing, seeds and BTS-ID tie rules are unchanged. No additional targeting experiment was added.

6. **Step 6, cell 2:** applied consistent local-path handling. **Cell 10, reading_text:** replaced “Degrees account for the result under these models” with “Within both empirical null intervals; not evidence of equivalence.” Replaced “Not explained by degrees, even with reciprocal pairs retained” with an explicitly exploratory description of the two interval positions. Added a same-direction/opposite-direction branch so two opposite deviations cannot be conflated. The generated 06_two_null_reading.csv now uses this wording. Metrics, intervals and H1/H2 verdicts are unchanged. Historical closing status is labelled as such.

7. **Step 7, cell 2:** applied consistent local-path handling. **Cell 14:** changed the out-of-bag validation from samples[:200] to samples, checking every one of the 2,000 bootstraps promised by the check label. No estimator, sample, interval or threshold changed. The final report explains the existing training-mean denominator in the rank-prediction score. Historical “report not started” text is labelled as historical.

Across notebooks, stale saved outputs were cleared before execution. Fresh outputs are included for Steps 1–3 and 5–7; Step 4 outputs remain cleared so historical execution is not misrepresented as a fresh run. A revision note explains paths, source preservation and execution scope.

## Expert improvements beyond the review brief

**Applied: fail visibly on invalid input.** The brief requests validation, but does not identify the silent-drop behaviour in Step 1. The added assertions make changes in future source files visible without altering this dataset.

**Applied: make local execution work consistently.** The brief mentions reproducibility generally; it does not identify the unconditional imports in Steps 1 and 2. Consistent path handling fixes an actual execution obstacle with no analytical change.

**Applied: correct generated interpretations, not only report prose.** The brief warns against interpreting H2 non-support as degree sufficiency. The audit located the contradictory claim inside Step 6's exported table. Fixing its generating function prevents the same claim from reappearing on rerun. The extra direction check avoids a second misleading summary.

**Applied: verify the full bootstrap collection.** The original validation label overstated its scope. Checking all saved samples is inexpensive and verifies the actual claim.

**Applied in report: clarify the prediction target and reference.** The score predicts training-transformed ranks and uses the training mean as the baseline. A value near 0.94 is not 94% of raw efficiency-loss variance explained. Keeping the estimator and describing it precisely is preferable to changing the approved analysis after seeing its results.

**Applied in report: qualify broad degree matching.** Matching degree bins such as 30–59 or 60+ does not make degree identical between groups. Residual confounding remains possible; the matched-bin condition is complementary evidence rather than an exact controlled experiment. Replacing bins now would change the approved H3 rule.

**Applied in report: distinguish rule-based verdicts from calibrated tests.** Correlated metrics, nested removal sets and multiple comparisons mean a 95% pointwise simulation interval does not imply a 5% family-wise error rate for the final decision rule. No post hoc correction or replacement threshold was imposed.

**Applied in report: explain singleton SCCs and time aggregation.** A surviving isolated airport yields SCC fraction 1/N even when efficiency is zero. Quarterly paths need not be simultaneous or timetable-feasible. These small explanations prevent plausible misreadings without changing the model.

**Not added:** adaptive attacks, stronger targeting, alternative community methods, additional airline samples, changed bootstrap models or expanded null ensembles. These would widen scope or change the approved design. Uniformity/irreducibility of the directed two-edge sampler is not claimed; diagnostics cannot establish that property.

## Review findings and disposition

| Concern | Evidence and disposition |
|---|---|
| Data totals and scope | Raw-data rerun reproduces node/edge tables. Cancelled and diverted scheduled records retained; PR/VI documented. |
| Community stability | Best partition is not recurrent; retain 100-run participation summary and label run variability as algorithmic. |
| Null validation | Independently checked all 900 cached graphs for exact degree sequences, simplicity and ensemble uniqueness; reciprocal graphs also checked for reverse edges. |
| NetworkX comparison | Reproduced failure with a bounded one-swap attempt. Official source confirms the blocking reverse-edge condition. Remains incomplete, not a successful validation. |
| Monte Carlo precision | E1 remains 11/144 and E2 6/144. The report defines both and retains the limitation. No additional nulls generated. |
| H1 collapse | Quantified retention, integer removals and concentration context. Random removal remains a reference rather than a risk model. |
| H2 floors and null mismatch | Distinguished zero/narrow intervals, initial efficiencies, reciprocity loss and exploratory comparison. Non-support is not equivalence. |
| H3 partial support | Listed each condition met, no reliable Gain, rank-score semantics, dependent-airport intervals, broad bins and HNL counterexample. |
| Betweenness ties | Deterministic primary ranking retained. Observed tie sensitivity supports stable H1 verdicts; null ties remain a limitation, especially AA/DL at 15–20%. |
| Reporting | New searchable PDF meets course page specifications. Changelog compares with the actual handoff baseline. |

## How to use the final package

The full seven notebooks and their Data and Results folders are together. Open a notebook from this folder or set NETWORK_ANALYSIS_LOCAL_ROOT to this folder's absolute path. For local execution, use Python and the recorded requirements.txt; install Jupyter separately if needed. The verification environment is recorded in verification_environment.json. Use a new kernel for each notebook and run in order 01–07.

Steps 05–07 can use the supplied cached Step 04 outputs; full null regeneration is unnecessary to reproduce their calculations. Step 04 is computationally expensive and was not tested end to end in this revision. Colab fallback retains the historical Google Drive path (including the trailing space in “Network Analysis ”); Colab itself was not tested. Run on a copy if you want to retain the delivered outputs.

Read Step 6 categorical verdict files with pandas.read_csv(path, keep_default_na=False): the literal “None” denotes no systematic deviation. Numeric files with genuinely empty numeric cells should retain normal numeric missing-value handling.

Final_Report.md is the editable report source. The PDF is the submission-format version. The surname order in the PDF filename is Amani Aghbolagh, Azimi, Manafzadeh, Narehei. The report has not been submitted or published. The Changelog of major report revisions is included in the report itself; this guide supplies the detailed code changes and expert recommendations separately.

## Verification boundaries

All Python cells in all seven notebooks parse successfully. Steps 1–3 and 5–7 executed top to bottom in fresh namespaces using a local Python cell runner, not a live Jupyter or Colab session. All 88 compared analytical tables match with relative tolerance 1e-10 and absolute tolerance 1e-12; intentional interpretation changes and runtime/environment metadata are excluded. Processed node/edge CSVs match the originals. The independent audit contains 1,365 passing checks. All original project-file hashes were checked after execution and are unchanged.

The revised report does not turn the earlier Step 4 sectional execution into an end-to-end run. It also does not claim proof of null-chain uniformity, statistical independence of airports, or operational validity of hypothetical closures. These remain substantive limitations, not issues that a wording correction can eliminate.
