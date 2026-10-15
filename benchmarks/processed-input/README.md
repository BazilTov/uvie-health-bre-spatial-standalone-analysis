# Processed-expression interface checks

The development source adds a processed matrix/metadata/provenance import route, documented in [PROCESSED-INPUT.md](../../PROCESSED-INPUT.md). It does not run or verify upstream normalization or sample-selection QC. No disease-specific assumptions are used for this route. Raw GeoMx processing still uses the existing explicitly labeled kidney reference profile.

Local Apple-silicon Mac checks passed using checksum-pinned public Baylor lung expression: 11,628 endogenous genes across 80 compartments. Metadata order was reversed deliberately. All 80 C3 values were verified in the downloaded evidence within absolute tolerance 1e-12. The evidence retains the declared log2 scale, partial upstream QC and supplied provenance. The run ZIP preserved matrix.csv, metadata.csv and provenance.json byte for byte and added an import audit. Mismatched sample identifiers were rejected and old findings were cleared.

The R integrity tests also check negative log-scale values, invalid linear values, duplicate genes and samples, nonfinite and nonnumeric expression, incomplete metadata, explicit control-sample separation and invalid provenance.

After the change, the full kidney interface test passed all four published dimensional checkpoints, exports and phone-width layout. These are local development checks; the original v0.2.0 release archives are unchanged. Native build tests now include processed-input integrity checks and the real-data browser flow before packaging. A future release still requires successful native and unpacked-package checks.

## Reproduction

Run `Rscript tests/check_processed_input.R`. For the browser test, run `python tests/prepare_processed_fixture.py output/processed-input --download`, start the app locally, then run `node tests/check_processed_app.mjs output/processed-input` with Playwright available and UVIE_TEST_URL set to the local app URL. Downloads are developer test setup only, not application behavior. Input hashes come from the existing Baylor benchmark manifest.

Gene evidence now uses schema version 2, a generic expression_value field and an explicit scale. JSON exports retain full numeric precision instead of display rounding. Existing schema-version-1 consumers must update for the new field.
