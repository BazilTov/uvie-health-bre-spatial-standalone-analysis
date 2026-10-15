# Baylor lung reference: scoped post-release audit

This audit evaluates the released importer and analysis components on an additional public GeoMx dataset, **GSE326968**. It is not an end-to-end validation of the standalone application's custom-data interface, independent reproduction of sample/gene filtering, or evidence of biological or clinical validity. The existing published release ZIPs were not modified by this audit.

## Sources and provenance

- [GEO study and files](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE326968): Baylor College of Medicine human lung WTA data.
- [IRF7 study](https://pmc.ncbi.nlm.nih.gov/articles/PMC13187531/): the methods and data-sharing statement.
- [Paper-linked analysis repository](https://github.com/tatsuhikonaito/CLAD_GeoMx): its README cites a related AP-1 study with overlapping tissue cohorts. Its code is not established as the exact version generating this GEO matrix.
- [Inspected QC script](https://github.com/tatsuhikonaito/CLAD_GeoMx/blob/main/scripts/geomxtools.R): `authors-code-review.json` records its immutable Git blob and SHA-256. It was inspected, not executed wholesale.

The analysis components correspond to application commit `a62687629a36f1b787a75fc657f63b51fb9ff3f0`. `input-manifest.json` pins the four downloaded files by SHA-256 and records their public URLs. No settings were adjusted after viewing the candidate normalized differences. The normalization plan was saved before that calculation; the plan is a local pre-execution record, not an externally timestamped preregistration.

## Initial diagnostic results, including failures

The raw DCC archive contains 116 files, including two GEO-declared controls. The published normalized matrix has 80 sample columns and **11,629 target rows: 11,628 endogenous genes plus one negative-control target**.

| Comparison | Values | Outside tolerance | Residual sample SD | Maximum absolute difference | Result |
|---|---:|---:|---:|---:|---|
| Raw probe import against GeomxTools | 2,182,540 | 0 | 0 | 0 | PASS, exact |
| Conditional log2-Q3, endogenous genes | 930,240 | 0 | 4.301858470273566e-16 | 9.947598300641403e-14 | PASS |
| Conditional log2-Q3, negative control | 80 | 24 | 0.013634032300505257 | 0.05616840880633989 | FAIL |
| Conditional log2-Q3, all targets | 930,320 | 24 | 0.00014061772681318524 | 0.05616840880633989 | FAIL |

The normalized comparison uses an absolute tolerance of **1e-6 log2 units**, with no relative tolerance. Raw import uses zero tolerance. SD describes differences between calculations, not tissue-to-tissue biological variation. Bias, MAE, RMSE, ID coverage, and other metrics are retained in the JSON reports; a small SD alone is not proof of agreement.

`negative-control-differences.csv` contains all 80 control comparisons, including the 24 failures. The follow-up below resolves these differences by adding the authors' documented probe QC, which our initial diagnostic omitted. These initial failures remain preserved as historical results, not as evidence of errors in the authors' normalized matrix.

## Follow-up: negative-control differences resolved

**Correction:** the initial negative-control differences arose when our diagnostic omitted the authors' documented probe QC/outlier-handling stage. They are not evidence of an error in the authors' normalized values. The initial test and its failures remain available above; the follow-up is a separate hypothesis test informed by those initial findings, not a fresh blind validation.

Before running the follow-up, we recorded `probe-qc-followup-plan.json`. We added `setBioProbeQCFlags` with the inspected script's fixed settings (`minProbeRatio=0.1`, `percentFailGrubbs=20`, `removeLocalOutliers=TRUE`) and its global/ratio exclusion rules before aggregation. We did not tune those values against the reference. All other conditional selections and transformations were unchanged.

- The probe stage marked 24 local count measurements as missing. No probes failed the global Grubbs or low-ratio checks.
- **All 930,320 conditional normalized values now pass** the same absolute tolerance of 1e-6 log2 units, with no missing or extra values.
- All 80 negative-control values now match exactly. The initial 24 control differences are resolved.
- Overall residual sample SD: **4.3016735962262953e-16**; maximum absolute difference: **9.947598300641403e-14**.
- The 930,240 endogenous values retain their passing result.

`probe-qc-followup-agreement.json`, `probe-qc-stage-summary.json`, and `probe-qc-followup-control-differences.csv` record the results. This demonstrates consistency with the documented outlier handling under the supplied sample/target selections. It does not independently establish the exact author code provenance or reproduce full QC. The nuclei, segment-detection threshold, area, original annotation, and NTC-label questions below remain unresolved; none is established as author misconduct or a demonstrated error.

## What the initial conditional check actually did

1. Read the public DCC and PKC files with GeomxTools and a metadata table derived from GEO.
2. Apply `shiftCountsOne(useDALogic=TRUE)` as in the paper-linked script.
3. Select exactly the sample IDs present in the published matrix.
4. Aggregate probes to targets, then select exactly the published target IDs, including the negative control.
5. Run GeomxTools Q3 normalization at the 75th percentile and apply plain log2 without an additional pseudocount.
6. Compare by target and sample identifier, keeping endogenous and negative-control results separate.

Supplying the published inclusion sets conditions the test on the authors' choices. It does not verify that our QC would independently select those same samples or genes. The initial calculation did not run the authors' probe-outlier QC, segment QC, or differential-expression analysis. The follow-up adds only probe QC; segment QC and differential-expression analysis remain outside scope. It leaves the public application code and kidney workflow unchanged.

## Discrepancies and unresolved provenance

1. **Nuclei cutoff:** the paper and linked code specify at least 100 nuclei. Eight sample columns in the published matrix have GEO nuclei values below 100. `reference-limitations.json` lists the exact IDs and recorded counts. The inconsistency could reflect different processing stages or metadata versions; it is not proof of an author error or misconduct.
2. **Segment detection:** the paper states a 10% threshold. The linked script has an active 5% threshold, with the 10% line commented out. This related-study script is not confirmed as the exact matrix-generating version.
3. **Area metadata:** no area field was found in the downloaded GEO sample characteristics; the paper's statistics section does not list an area cutoff, but the linked script applies a minimum area of 1,000. No area values were invented and no area-based QC reproduction was claimed.
4. **Missing original annotation workbook:** the linked script expects a local `annotations.xlsx` that was not present among the inspected GEO supplementary files. Our `sample-annotation.csv` is a derived table of public fields, not a replacement claimed to be identical to that workbook.
5. **Control identification:** the initial GeomxTools raw import warned that the slide-column naming did not identify template controls. The conditional run supplied the slide-name alias but still warned that the expected control-label convention was absent. All 116 raw columns were compared for import, while the conditional check used the 80 published columns. No NTC-based QC result was claimed.
6. **Reference contents:** the normalized matrix retains a negative-control row. Calling every row a gene, or omitting that row's failures from an overall pass/fail claim, would be misleading.

Exact full-workflow agreement remains unresolved until the annotation, QC decisions, control processing, cohort, and matrix-generating code version can be reconciled. We have not contacted the authors or changed the reference to force agreement.

## Reproduce the scoped checks

These are maintainer diagnostics requiring Python and the documented R libraries; the full application packages remain usable without installing those separately.

1. Download the four URLs in `input-manifest.json`, using its local filenames in a separate directory. The original data files are not redistributed in this audit folder.
2. Run `python benchmarks/baylor-lung/prepare_inputs.py DATA_DIRECTORY` from the repository root. This verifies file hashes, safely prepares the DCCs, derives annotations from GEO, and runs the unchanged Python importer.
3. In the repository's R environment, run `Rscript benchmarks/baylor-lung/raw-import.R DATA_DIRECTORY` and `Rscript benchmarks/baylor-lung/conditional-normalization.R DATA_DIRECTORY`.
4. Run `python benchmarks/baylor-lung/compare_outputs.py DATA_DIRECTORY` to regenerate the comparison reports.

The pinned session information records the actual GeomxTools 3.14.0 / R 4.5.2 environment. Normalization diagnostics are explicitly separate from the existing full kidney application benchmark.

For the follow-up, run `Rscript benchmarks/baylor-lung/probe-qc-followup.R DATA_DIRECTORY`. Its output has a separate filename and does not overwrite the initial diagnostic. Run `python benchmarks/baylor-lung/compare_outputs.py DATA_DIRECTORY` again to generate a separate follow-up report using the same target/sample alignment and fixed tolerances.
