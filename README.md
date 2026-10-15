# UVIE Health BRE Spatial - Standalone

A standalone spatial-transcriptomics analysis prototype for GeoMx tissue compartments. No UVIE account or private reasoning engine is required. Established GeoMx software performs the analysis; our application adds a local interface, evidence exports, reproducibility records, and scoped benchmark checks.

## Full package for researchers

The platform-specific developer-preview releases include **R, the analysis libraries, and the wired pipeline**. Unzip the full release and open `launch.command`. Your existing browser displays the local interface. The full package needs no separate Python, R, Docker, or analysis-library installation.

Choose **Packaged kidney reference**, then **Run reference pipeline**. Example inputs are supplied by the bundled reference package. Choose a gene or compartment after processing and download its evidence or complete run outputs.

Runs bind to your computer's loopback interface. No account, cloud processing, automatic package installation, or data upload to UVIE occurs. Closing the launch terminal ends the application. Download run outputs before closing it.

Full releases are platform-specific. Windows uses `launch.bat`; Linux and Mac use `launch.command`. Native build, application, and unpacked-ZIP checks passed for Apple-silicon Mac (macos-14), Intel Mac (macos-15-intel), Windows (windows-2022), and Linux (ubuntu-22.04). [Verification run](https://github.com/BazilTov/uvie-health-bre-spatial-standalone-analysis/actions/runs/38672756904). Complete packages, checksums, and launch instructions are available in the [v0.3.0 developer-preview release](https://github.com/BazilTov/uvie-health-bre-spatial-standalone-analysis/releases/tag/v0.3.0-preview). Only platforms with successful native execution checks should be offered as ready-to-use public downloads. Linux compatibility depends on the tested distro/glibc baseline; this is not a promise for every OS.

**A source ZIP differs from a full release.** It contains code and build tooling, not hundreds of megabytes of runtime libraries. End users who want no dependency installation should select a complete platform release.

## Pipeline

The R runner evaluates the code distributed with GeoMxWorkflows 1.16.0 through Q3 normalization using that package's own kidney inputs. It saves import, QC, aggregation, retained-count, and normalized matrices, a reference object, flat sample metadata, stage counts, and session information.

The interface explores normalized compartment expression and exports JSON and ZIP results. It does not calculate differential-expression significance or infer drug effectiveness. The custom GeoMx ZIP option applies the kidney QC profile; another study requires review of parameters and experimental design. Expected layout: one dataset folder with `dccs/`, `pkcs/`, and an `annotation/` XLSX containing a `Template` sheet. Reference fields include sample identifiers, tissue/slide, group, compartment, segment area, and nuclei.

## Processed data from other studies

The v0.3.0 preview and current source also accept a [processed expression ZIP](PROCESSED-INPUT.md), preserving the supplied method, scale, and QC limitations. It aligns sample identifiers, rejects invalid or ambiguous inputs, separates declared control samples, and exports full-precision values. This route explores already-processed data; it does not run or verify upstream QC or normalization. The v0.2.0 release ZIPs predate this feature. The updated native checks passed on Apple-silicon Mac, Intel Mac, Windows x64 and Ubuntu 22.04 x64, including the real-data processed-input flow and execution from unpacked packages. Gene evidence now uses schema version 2 with an explicit scale and generic expression_value field; consumers of version 1 must update.

## Benchmark evidence

- Four published dimensional checkpoints match through normalization.
- **4,380,870 raw probe values** match our independent reader exactly.
- **2,238,951 normalized values** agree with independent Q3 arithmetic within predefined absolute tolerance 1e-8 and relative tolerance 1e-9.
- Executed software and interface checks are recorded in `VALIDATION.md` and accompanying artifacts.

Input versions matter. The vendor ZIP has 277 biological compartments; the canonical package annotations have 235. The package omits 42 vendor records. The shared-record annotations also differ, including nuclei values and some segment labels. We reproduce the exact canonical package and metadata rather than calling the larger archive identical. See benchmarks/input-reconciliation.json.

Agreement is scoped. It does not independently validate biological findings, the complete filtering ground truth, clinical performance, or scientific novelty. This is a reproducible developer prototype, not parity with Stanford's virtual biotech system.

## Second-dataset audit: agreement and discrepancies

A [Baylor lung reference audit](benchmarks/baylor-lung/README.md) checks released analysis components on an additional public dataset. Raw import matched 2,182,540 values exactly. Conditional normalization matched 930,240 endogenous gene values within the predeclared tolerance, using the published sample and target selections. **An initial diagnostic omitted documented probe QC and had 24 negative-control differences. Adding that stage in a separately planned follow-up resolved all 24; all 930,320 conditional normalized values pass.** Both the initial failure and its resolution are preserved. Full QC reproduction remains unresolved because of nuclei/threshold differences and missing original annotation provenance. This is not end-to-end validation of the application on Baylor data. Reports, input hashes, all negative-control differences, and reproduction scripts are included in the audit folder.

## Ovary atlas intake and diagnostic

The [University of Michigan ovary atlas assessment](benchmarks/ovary-atlas/README.md) matched all 4,873,085 raw count values to GeomxTools. Its annotation workbook includes area and nuclei measurements, but the row-to-AOI linkage remains provisional. A prospectively specified donor 2 centroid comparison failed: 112,052 of 168,084 values exceeded the 1e-6 tolerance. Three clusters match and six do not. These results do not establish an author error or full pipeline validation. The failed diagnostic, source hashes, assumptions and reproduction scripts are preserved. Dataset completeness requires reliable identifier linkage as well as populated metadata columns.

## Scientific boundaries

- GeoMx compartments are measured areas, not individually positioned cells.
- This prototype has no tissue-coordinate file and calculates no cell distances.
- RNA counts do not establish protein abundance, binding, causation, or efficacy.
- ROI repeats are not independent participants; inferential claims need participant-aware modeling.
- Unknown or filtered values must not be described as absent biology.
- Public endometriosis data GSE263897 cover 60 compartments and five participant labels. They have been imported into the raw explorer, not fully QC-reviewed or statistically analyzed. Missing area/nuclei metadata need a study-specific solution.

## Developer source usage

Python intake/comparison utilities need Python 3.10+ and no third-party Python packages. These are development tools; the full research package uses bundled R.

```sh
python3 spatial.py fetch --dataset kidney
python3 spatial.py build --dataset kidney --output output/kidney
python3 -m unittest discover -s tests -v
```

Open the generated `output/kidney/explorer.html` for raw-count inspection. Choose embedded genes with `--genes C3 CD68 EPCAM`; the full endogenous raw matrix is always exported. A full `evidence.json` can load into another raw explorer; a single-gene view export is not a complete dataset.

```sh
python3 spatial.py compare reference.csv candidate.csv --atol 1e-8 --rtol 1e-6 --output agreement.json
python3 benchmarks/check_q3.py output/reference
```

Matrices use genes as rows and sample identifiers as columns. Comparisons align identifiers. Duplicate, missing, extra, or non-finite inputs fail checks. Report RMSE, mean absolute error, maximum absolute error, bias, and residual SD together; zero residual SD can coexist with constant bias.

## Building complete releases

The native build workflow installs dependencies **at build time**, copies them into the runtime, executes application tests, and packages only after tests pass. It is manually triggered and uploads artifacts; it does not publish a public GitHub release automatically.

For an already-prepared and tested runtime:

```sh
python3 scripts/package_release.py --output output/UVIE-Spatial-full.zip
```

Versions and licenses are recorded in `runtime/package-versions.csv`. The Mac launcher locates the bundled framework without modifying R executable binaries. Additional native-platform tests are mandatory before calling other platforms supported. Docker is an optional, untested maintainer configuration; full-release users do not need it.

## Attribution

See `THIRD_PARTY.md` and preserved dependency license files. Our MIT license does not replace R's GPL or dependency licenses. Source distribution excludes endometriosis downloads and compiled runtimes. The full release contains the example data shipped with the upstream workflow package.

- GeomxTools: https://bioconductor.org/packages/GeomxTools/
- GeoMxWorkflows: https://bioconductor.org/packages/GeoMxWorkflows/
- Kidney workflow: https://www.bioconductor.org/packages/release/workflows/vignettes/GeoMxWorkflows/inst/doc/GeomxTools_RNA-NGS_Analysis.html
- Endometriosis data: https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE263897
- Endometriosis paper: https://doi.org/10.1016/j.isci.2025.111790

No synced project source documents are available in this local mirror. Private-engine integration remains optional and does not assume an unavailable contract. The repository and developer-preview packages are public. The application has not been signed or notarized.
