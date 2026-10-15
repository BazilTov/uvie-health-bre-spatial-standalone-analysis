# Validation status — standalone prototype

Date: October 14, 2026

## Executed on Apple-silicon macOS

- Bundled R 4.5.2 runs without a system-wide R installation.
- GeomxTools 3.14.0, NanoStringNCTools 1.18.0, GeoMxWorkflows 1.16.0, Shiny, and dependencies load from the bundle.
- The canonical kidney workflow executes through Q3 normalization.
- Published checkpoints match: 18,642 probes / 229 segments after segment QC; 18,641 / 229 after probe QC; 18,504 targets / 229 after aggregation; 10,131 targets / 221 segments after detection and normalization.
- Independent DCC import: **4,380,870 values, zero mismatches** against GeomxTools.
- Independent Q3 arithmetic: **2,238,951 values**, all within predefined absolute tolerance 1e-8 and relative tolerance 1e-9. RMSE 8.063644622139701e-14; maximum absolute error 4.9112713895738125e-11.
- Ten intake/comparison unit tests pass.
- Raw-explorer browser checks pass on real kidney/endometriosis files.
- The complete Mac package was unpacked into a fresh folder with spaces and launched with only the standard system path. The full UI-triggered pipeline, normalized JSON export, complete ZIP output export, desktop/phone layout, and absence of browser errors passed. The scientific plot redraws at phone width. Desktop and phone renderings were visually inspected.

## Input reconciliation

Vendor ZIP: 281 records, comprising 277 biological compartments and four controls. Canonical workflow annotations: 239 records, comprising 235 biological compartments and four controls. The package omits 42 vendor records. For shared records, nuclei values differ in 235 rows; AOI and segment labels differ in 84; one pathology label differs. Reproduction uses the exact canonical inputs and metadata shipped with GeoMxWorkflows 1.16.0; no silent adjustment is applied. See benchmarks/input-reconciliation.json.

## Limits and remaining release gates

- Checks establish raw import agreement, published dimensional agreement, and independent normalization arithmetic agreement. They do not independently establish biology or full filtering ground truth.
- No differential-expression model, participant-level inference, single-cell neighborhood inference, protein binding, or treatment efficacy has been evaluated.
- Endometriosis was imported, not run through a study-reviewed full QC/statistical workflow. Missing area/nuclei metadata need attention.
- Docker has not been built here.
- Native build, full application benchmark/export checks, and tests from the unpacked release ZIP passed on macos-14 (Apple silicon), macos-15-intel, windows-2022, and ubuntu-22.04. [Completed verification run](https://github.com/BazilTov/uvie-health-bre-spatial-standalone-analysis/actions/runs/38638835108), tested commit a62687629a36f1b787a75fc657f63b51fb9ff3f0.
- An additional Apple-silicon artifact was downloaded from GitHub, its artifact and inner-release checksums verified, and its unpacked application/benchmark/exports tested locally.
- The Linux setup now installs libuv and GLPK, and the bundle materializes runtime links. Intel analysis and archive-export checks allow longer execution while retaining the same dimensional and export assertions. Windows temporary test-folder cleanup is separate from application results.
- The four complete packages were published in the [v0.2.0 developer-preview release](https://github.com/BazilTov/uvie-health-bre-spatial-standalone-analysis/releases/tag/v0.2.0-preview). The publishing workflow verified original build checksums and ZIP integrity, then attached those exact package bytes with manifests, SHA256SUMS.txt, launch instructions, and provenance. Public asset digests agree with the published checksum file.
- The Mac package is a developer preview, not a signed/notarized UVIE app release.
- Scientific review remains separate from these software and package checks. Tests cover the listed runner environments; broader OS compatibility has not been established.

## Post-release second-dataset audit: Baylor lung

**Current conclusion: the negative-control discrepancy originated in our initial diagnostic, which omitted documented probe QC. The follow-up resolves it and all conditional normalized values pass. The historical failure below does not establish an error by the authors.**

[Full methods, reports, and discrepancies](benchmarks/baylor-lung/README.md). This audit uses released analysis components; it does not modify the published ZIPs or establish end-to-end custom-data application validation.

- Raw import: 2,182,540 values matched GeomxTools exactly, including all 116 raw records and the two GEO-declared controls.
- Conditional Q3/log2: 930,240 endogenous values passed absolute tolerance 1e-6; residual sample SD 4.301858470273566e-16, maximum error 9.947598300641403e-14. Published sample/target selection was supplied rather than independently reproduced.
- **Initial conditional normalized comparison FAIL:** 24 of 930,320 values exceed tolerance. All 24 are among the 80 negative-control values; maximum difference 0.05616840880633989 log2 units. Overall residual SD 0.00014061772681318524. The gene-only pass must not be presented as an overall matrix pass.
- Eight included samples have GEO nuclei counts below the stated 100-nuclei cutoff. The paper states 10% segment detection; the paper-linked, related-study script uses 5%. The linked code also uses an area filter, but area is absent from the inspected GEO sample characteristics, and its original annotation workbook was not supplied there.
- Control-label conventions were not recovered; no NTC-QC result is claimed. The linked code is associated with a related overlapping-cohort paper, not established as the exact GEO-matrix-generating version.
- These are unresolved provenance/processing differences, not evidence of misconduct. No biological or clinical validity is inferred.

### Correction and probe-QC follow-up

The initial negative-control differences were caused by our diagnostic omitting the documented probe QC/outlier-handling stage, not an established error in the authors' normalized matrix. A separately recorded follow-up added the authors' fixed probe-QC settings, without tuning them. All 930,320 conditional values now pass the same absolute tolerance of 1e-6; all 80 negative-control values match exactly. Overall residual sample SD is 4.3016735962262953e-16 and maximum absolute error is 9.947598300641403e-14. The initial failure reports remain published as history. Full QC/sample selection, metadata and provenance reconciliation remain unresolved. See the audit folder's follow-up reports and scripts.


## Development update: processed-expression input

The development source adds a study-method-preserving processed-input route. [Local browser checks and reproduction instructions](benchmarks/processed-input/README.md) cover the published 11,628-gene, 80-compartment lung matrix, keyed metadata alignment, full-precision gene export, retained upstream-processing limitations, run downloads and invalid-input rejection. The full kidney UI regression also passed after these changes. These local checks do not update the existing release ZIPs or establish native validation of a new release.

The separate [ovary atlas diagnostic](benchmarks/ovary-atlas/README.md) passed exact raw import but failed the predeclared donor 2 centroid comparison. Its metadata linkage remains provisional. It is not a completed full-pipeline benchmark and supplies no evidence of author error.


## v0.3.0 native verification

All four native runners passed the reference UI benchmark, processed-input integrity tests, the checksum-pinned 11,628-gene/80-compartment lung browser flow, and execution from unpacked ZIPs in [the pinned build](https://github.com/BazilTov/uvie-health-bre-spatial-standalone-analysis/actions/runs/38672756904). Tested application commit: e37725ec86864362a2254ef58850026cd94f2535. Release promotion verifies successful jobs and preserves the exact tested archive bytes; PACKAGE-VERIFICATION.json records package checksums and both browser-test scopes. These checks establish software behavior on the named runners, not independent biological or clinical validity. Earlier local-only language above records the development stage before these native checks.

## Tissue-map source milestone — 15 October 2026

The current source adds optional measured-coordinate maps and registered PNG previews. Local Apple-silicon verification passed the spatial input suite, public Visium browser flow (all 2,825 filtered spots; six selected genes), original kidney full UI benchmark, public lung processed-input regression, and ten Python intake/comparison tests. The exported spatial counts and coordinates match the fixture exactly; source input files survive the run ZIP byte-for-byte. See [spatial-map checks](benchmarks/spatial-map/README.md).

This is not full-transcriptome spatial processing, a neighborhood statistical method, independent biological validation, or validation of other native platforms. Four-platform workflow and unpacked-package tests now include spatial checks; their results must be inspected before publishing updated full downloads. Existing v0.3.0 packages predate tissue maps. No BRE access or credentials are included.
