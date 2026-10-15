# Measured-coordinate tissue map check

The first spatial display milestone uses the official 10x Genomics mouse-brain sagittal anterior section 2 Visium dataset (Space Ranger 1.0.0). Sources, archive SHA-256 hashes, dimensions and subset scope are recorded in `fixture-intake.json`.

The fixture preserves all **2,825 filtered spots** and selects six genes in advance: C3, Gfap, Mbp, Slc17a7, Aqp4 and Pecam1. The original sparse count matrix has 31,053 features and 14,167,739 nonzero entries. This display subset is not a claim that the dense application supports this entire transcriptome or modern whole-slide single-cell datasets. No upstream normalization, cell-type assignment, spatial statistical test or treatment inference is performed.

## Executed checks

Local Apple-silicon checks on 15 October 2026 passed:

- R importer tests: identifier joins, section/participant separation, finite positions, declared units and resolution, duplicate rejection, image bounds and unsafe paths.
- Real-data browser test: registered image overlay, gene switching, all 2,825 original count values and all 2,825 positions preserved in gene evidence despite reversed annotation rows, map PNG download, run ZIP download, missing coordinate rejection and stale-map clearing.
- Every original spatial fixture input file was retained byte-for-byte in the exported run ZIP.

The asymmetric raster unit fixture checks corner colors, and the public overlay was visually inspected. These checks are not an independent assessment of the vendor's biological registration quality. The public example uses source-image pixels and the vendor preview scale; no physical distance calibration is asserted.

Native checks are wired for the four release platforms, including the public spatial browser flow from the unpacked full ZIP. The local report does not establish those jobs have passed. Existing published v0.3.0 full packages predate this feature.

## Reproduce

From the repository root:

```sh
python tests/prepare_spatial_fixture.py output/spatial-input --download
Rscript tests/check_spatial_input.R
```

Launch the application and run `node tests/check_spatial_app.mjs output/spatial-input` with `UVIE_TEST_URL` set to its local address. Developer browser tests require Playwright. End users do not need test dependencies. Load `output/spatial-input/visium-spatial.zip` using Processed expression ZIP, then select Tissue map.

## Attribution

Data: [10x Genomics public dataset, CC BY 4.0](https://www.10xgenomics.com/datasets/mouse-brain-serial-section-2-sagittal-anterior-1-standard-1-0-0). [Official image-coordinate definitions](https://www.10xgenomics.com/support/software/space-ranger/2.1/analysis/outputs/spatial-outputs). This is one mouse and one tissue section; spots are not independent donors or individually localized cells.
