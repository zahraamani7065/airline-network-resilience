# Validation record

Source revision: 46c454da8ea5986419e451fa1ec8c401151d21e1.

- Steps 01, 02, 03, 05, 06 and 07: all code cells executed sequentially, using a fresh namespace per notebook. See execution_status.json for counts and timings. This was Python execution, not a browser-driven Jupyter/Colab test.
- Step 04: syntax checked; cached ensembles independently audited. Full end-to-end regeneration was not performed. No claim is made that this historical execution limitation has been resolved.
- 88 analytical CSV tables: match original values at rtol=1e-10, atol=1e-12, with exact text comparison except the intentionally revised Reading column in 06_two_null_reading.csv. Runtime and environment metadata are excluded. See output_comparison.csv.
- Processed source network CSVs: equal to originals.
- Independent saved-evidence audit: 1,365 checks passed, including all 900 null networks and 144 H2 intervals. See independent_audit.csv.
- All 2,000 bootstraps per airline have out-of-bag airports; original seeds and H3 values reproduced.
- Original project files: hashes unchanged after reruns.
- Colab: untested.

The numeric content of the report uses these verified results. Updated notebooks contain fresh outputs for executed steps; Step 04 has cleared outputs to avoid implying fresh execution.
