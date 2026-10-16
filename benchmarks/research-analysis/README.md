# Neighborhood and participant-analysis verification

This folder records software verification of selected-gene analysis. It does not establish biological validity, clinical performance, or superiority over other packages.

## Local results

- R known-distance tests pass section isolation, exact inclusive radius, self-edge exclusion, isolates, identifier reordering, and graph size/edge limits.
- Participant tests use fixed known values to verify paired and Welch statistics, the paired confidence interval and p-value, explicit pair alignment, incomplete-pair exclusion, descriptive defaults, sample-count and inference-confirmation guards, and equal section weighting. Repeating each observation four times leaves the effect, p-value and participant count unchanged.
- Local browser checks verify uploads, both modules, downloads, invalid-design errors and stale-state clearing. Complete-run checks additionally verify both derived JSON files are included, original inputs are unchanged, and invalidated files are removed.
- The public 10x Visium six-gene example retains all **2,825 measured spots**. With a **1,000 source-image-pixel radius**, the selected section has **242,072 undirected edges**. A separate Python stdlib brute-force implementation evaluates every possible pair directly from source coordinate CSV and verifies every exported edge, distance, count and selected-gene mean. Maximum distance discrepancy is approximately **5.12e-13 pixels**, within the 1e-9 tolerance. This does not infer physical calibration, cell contact or communication.

The synthetic participant fixture has three complete pairs and twelve observations. Expected B-minus-A effect is 2 on the supplied log2 scale, paired t = sqrt(12), df = 2, p = 0.0741799002274485, with 95% confidence interval approximately [-0.48413771172, 4.48413771172]. This intentionally is not a significant biological finding; all expression and coordinates in this fixture are synthetic.

## Reproduce

From the repository root with the bundled runtime configured:

```sh
Rscript tests/check_research_analysis.R
python tests/prepare_research_fixture.py output/research-input
# With the application running and Playwright available:
node tests/check_research_app.mjs output/research-input
python tests/check_research_exports.py output/research-input
# The public Visium fixture is prepared by tests/prepare_spatial_fixture.py:
node tests/check_spatial_app.mjs output/spatial-input
python tests/check_public_neighbors.py output/spatial-input
```

See [method and input guide](../../RESEARCH-ANALYSIS.md). Local report names explicitly identify scope. Four-platform verification and tests from actual unpacked packages are required before publishing the new preview. Existing v0.4.0 package verification does not cover these new modules.
