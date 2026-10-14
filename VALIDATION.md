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
- Complete packages are stored as build artifacts. Public GitHub release publication remains pending.
- The Mac package is a developer preview, not a signed/notarized UVIE app release.
- Scientific review remains separate from these software and package checks. Tests cover the listed runner environments; broader OS compatibility has not been established.
