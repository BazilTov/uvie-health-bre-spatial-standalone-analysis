# Reproduce the released spatial workflow

This walkthrough reproduces specific software results in **v0.5.0-preview**. It uses a real public mouse-brain section for tissue maps and neighborhoods, and a **separate synthetic dataset** for participant comparisons. No UVIE account, private Biomedical Reasoning Engine access, or separate R installation is required for the full application package.

Successful reproduction establishes agreement for these inputs and settings. It does not validate a drug target, disease effect, biological mechanism or clinical use.

## 1. Download the application and examples

Open the [v0.5.0-preview release](https://github.com/BazilTov/uvie-health-bre-spatial-standalone-analysis/releases/tag/v0.5.0-preview). Under Assets, download:

| Your computer | Full application ZIP |
| --- | --- |
| Apple-silicon Mac | `UVIE-Health-BRE-Spatial-Standalone-v0.5.0-Mac-AppleSilicon.zip` |
| Intel Mac | `UVIE-Health-BRE-Spatial-Standalone-v0.5.0-Mac-Intel.zip` |
| Windows x64 | `UVIE-Health-BRE-Spatial-Standalone-v0.5.0-Windows-x64.zip` |
| Linux x64, tested Ubuntu 22.04 baseline | `UVIE-Health-BRE-Spatial-Standalone-v0.5.0-Linux-Ubuntu22.04-x64.zip` |

Also download these assets from that same release:

- [Visium-mouse-brain-six-gene-example.zip](https://github.com/BazilTov/uvie-health-bre-spatial-standalone-analysis/releases/download/v0.5.0-preview/Visium-mouse-brain-six-gene-example.zip)
- [Synthetic-participant-verification-example.zip](https://github.com/BazilTov/uvie-health-bre-spatial-standalone-analysis/releases/download/v0.5.0-preview/Synthetic-participant-verification-example.zip)
- [SHA256SUMS.txt](https://github.com/BazilTov/uvie-health-bre-spatial-standalone-analysis/releases/download/v0.5.0-preview/SHA256SUMS.txt)
- [PACKAGE-VERIFICATION.json](https://github.com/BazilTov/uvie-health-bre-spatial-standalone-analysis/releases/download/v0.5.0-preview/PACKAGE-VERIFICATION.json)

GitHub's automatically generated **Source code** archives do not contain the full runtime. Fully extract the application ZIP; leave both dataset ZIPs zipped for upload.

Before launching, compare your application ZIP's SHA-256 to its filename in SHA256SUMS.txt. Mac: `shasum -a 256 YOUR-PACKAGE.zip`; Linux: `sha256sum YOUR-PACKAGE.zip`; Windows PowerShell: `Get-FileHash .\YOUR-PACKAGE.zip -Algorithm SHA256`. Repeat for the example ZIPs. File-integrity agreement does not establish scientific validity. The example digests and expected results are also recorded in [expected-results.json](docs/reproducibility/expected-results.json).

## 2. Launch locally

Open the extracted `UVIE-Spatial` folder. Mac uses `launch.command`; Windows uses `launch.bat`. Linux users open a terminal in that folder, run `chmod +x launch.command`, then `./launch.command`. Keep the launcher terminal open.

The application binds to `http://127.0.0.1:8765`. If a browser does not open automatically, enter that address. The bundle is an unsigned developer preview; follow your operating system's normal trust controls and local policy. Compatibility beyond the [tested platforms](DOWNLOAD-AND-LAUNCH.md) is not established. If that port is occupied, close an earlier instance or use the alternative-port instructions in the launch guide.

## 3. Reproduce the public tissue map

1. In **Input**, choose **Processed expression ZIP**.
2. Upload `Visium-mouse-brain-six-gene-example.zip` and press **Load processed expression**.
3. Confirm the status reports **6 targets across 2825** biological observations.
4. Select gene **Gfap**, keep **Compartment = All**, and open **Tissue map**. Select section **sagittal_anterior_section_2** if necessary.
5. Confirm the map reports **spot** resolution and **pixel** units, and shows expression over the tissue image. Change opacity to inspect registration.
6. Download the tissue map and gene evidence. Keep these files in a folder named `visium-results`.

Expected result: all **2,825 filtered spots**, six explicitly selected genes, one donor and one section. Coordinates are full-resolution source-image pixels mapped to a PNG preview using the vendor factor **0.051635113**. The map displays `log2(count + 1)`; exported original expression remains UMI counts. An image that is within bounds is not independently proven to be correctly registered.

The source is the [10x Genomics Mouse Brain Serial Section 2, Sagittal-Anterior dataset](https://www.10xgenomics.com/datasets/mouse-brain-serial-section-2-sagittal-anterior-1-standard-1-0-0), processed by Space Ranger 1.0.0, CC BY 4.0, attribution **10x Genomics**. Our six-gene subset retains every filtered spot, not the full transcriptome. No cell identity or physical micrometre scale is inferred. See the release's EXAMPLE-PROVENANCE.json and [fixture preparation script](tests/prepare_spatial_fixture.py).

## 4. Reproduce the public neighborhood graph

With the same dataset, gene, section and All-compartment selection:

1. Open **Neighborhoods**.
2. Set the radius to **1000** in the supplied **pixel** units and press **Calculate neighborhoods**.
3. Expect **2,825 positions** and **242,072 undirected edges**.
4. Download neighborhood evidence into `visium-results`. Its graph must contain no self edges or cross-section edges. Neighbor-expression means exclude the focal position.
5. Download run outputs **after** calculating the graph. The complete ZIP must include `neighborhoods.json` along with the original input files. A run export made before calculation will not contain that later result.

The map colors positions by neighbor count. Changing the gene changes expression summaries, not graph geometry. A 1000-pixel radius is a reproducibility setting, not a biologically optimized neighborhood. Proximity does not establish cell contact or communication.

The [independent graph record](benchmarks/research-analysis/public-radius-graph-checks.json) evaluates every possible spot pair. It reports the same edge set and a maximum distance difference of approximately **5.12e-13 pixels**, below the declared **1e-9** tolerance. This is a separate calculation, not an independent laboratory evaluation.

## 5. Reproduce participant comparisons using synthetic data

Download/save the public-data results before changing inputs. Uploading another dataset clears previous analyses.

1. Keep **Input = Processed expression ZIP**. Upload `Synthetic-participant-verification-example.zip` and press **Load processed expression**.
2. Confirm **2 targets across 12** observations. Select gene **Target**.
3. Open **Participant comparison**. Select compartment **stroma**, **Condition A = A**, **Condition B = B**, and **Paired participants**.
4. Press **Compare participants** without enabling inference. Expect descriptive results with three participants per condition, three complete pairs, and effect **B minus A = 2** on the supplied log2 scale. There must be no p-value yet.
5. This fixture is synthetic and deliberately constructed to test the calculation. After reviewing the displayed assumptions, enable the inference confirmation and calculate again.
6. Download participant comparison and complete run outputs into a separate `synthetic-results` folder.

| Quantity | Expected value |
| --- | --- |
| Independent biological units | 3 synthetic pairs, not 12 participants |
| Participant means A | 1, 2, 3 |
| Participant means B | 2, 4, 6 |
| Mean paired difference B minus A | 2 |
| Paired t statistic | 3.46410161513775 |
| Degrees of freedom | 2 |
| Two-sided unadjusted p-value | 0.0741799002274485 |
| 95% confidence interval | approximately -0.48413771175 to 4.48413771175 |

Compare floating-point quantities with tolerances, not exact displayed strings; [expected-results.json](docs/reproducibility/expected-results.json) defines them. This example is not a biological finding or a claim of adequate statistical power. Do not use the one-donor public brain example to demonstrate between-participant inference.

Optional geometry check on the synthetic input: select section **P1_A**, keep all compartments, and calculate radius **5 um**. Expect two positions and one edge of length 5. Radius **1 um** yields no edges and two retained isolates with null neighbor means. These coordinates are synthetic.

## 6. Check exports and stale-result clearing

Gene evidence uses schema version **2**; neighborhood and participant exports use schema version **1**. Do not assume the schemas are interchangeable. Preserve the supplied provenance and scientific limitations.

Open the downloaded run ZIP without modifying its contents. The Visium run should retain the five input CSV/JSON files plus `tissue.png`, and its current `neighborhoods.json`. The synthetic comparison run should retain its five original inputs and `comparison.json`. If a synthetic neighborhood was also calculated and remains current, that run can include both analyses.

Change the selected gene or a relevant setting. The previous result should clear; calculate again before downloading a new current result. An export made after invalidation must not contain an old analysis file. Changing datasets must also remove the previous tissue map and analyses.

## 7. Optional kidney reference reproduction

Choose **Packaged kidney reference**, then **Run reference pipeline**. Wait for completion, which may take several minutes. Expect **10,131 targets across 221 retained compartments** and four matching dimensional checkpoints under **Benchmark checkpoints**. Download gene evidence and run outputs into a third folder.

Historical independent checks matched **4,380,870 raw probe values** exactly and **2,238,951 normalized values** within absolute tolerance 1e-8 and relative tolerance 1e-9. These full-matrix checks are not re-executed merely by observing the four interface checkpoints. See [VALIDATION.md](VALIDATION.md), [raw agreement](benchmarks/full-import-agreement.json) and [Q3 agreement](benchmarks/q3-arithmetic-agreement.json). Use canonical GeoMxWorkflows 1.16.0 package inputs; the larger vendor archive has different records and annotations.

## 8. Record and share your reproduction

Record the release, downloaded ZIP digest, operating system/processor, input example, settings and expected/observed results. Retain the evidence JSON and run ZIP. For a mismatch, report the exact step, error text and settings in a [GitHub issue](https://github.com/BazilTov/uvie-health-bre-spatial-standalone-analysis/issues). Do not upload participant identifiers, private tissue data or credentials to a public issue.

Researchers can perform the walkthrough through the interface without programming. An optional Python 3.10+ standard-library checker is available for developers:

```sh
python scripts/check_walkthrough.py --downloads /path/to/downloads
python scripts/check_walkthrough.py --visium-example /path/to/Visium-mouse-brain-six-gene-example.zip --neighborhood /path/to/neighborhood-evidence.json
python scripts/check_walkthrough.py --comparison /path/to/participant-comparison.json
```

Supply actual downloaded filenames if your browser renamed them. The checker is source tooling, not included in the unchanged v0.5.0 binary bundles; Python is optional and only needed for this additional check. It recomputes the public graph from pinned example inputs and checks the synthetic paired result. It does not verify biological validity or all package behavior.

For exact historical test scope, see [native verification](benchmarks/research-analysis/native-verification.json), [unpacked-package checks](benchmarks/research-analysis/local-unpacked-checks.json), [release digest verification](benchmarks/research-analysis/release-verification.json), and the [methods guide](RESEARCH-ANALYSIS.md). The [manuscript draft](docs/manuscript/BRE-Spatial-software-manuscript.md) and [evidence gaps](docs/manuscript/EVIDENCE-GAPS.md) describe the contribution and what remains untested.
