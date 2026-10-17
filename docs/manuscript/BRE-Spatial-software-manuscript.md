# BRE Spatial for reproducible spatial expression exploration and participant aware analysis

Software manuscript draft describing UVIE Health BRE Spatial - Standalone v0.5.0-preview. October 17, 2026. Not submitted or peer reviewed. Authorship and declarations require author confirmation before submission.

## Abstract

Spatial transcriptomics analysis combines expression measurements with specimen geometry, study annotations and processing provenance. Researchers need to inspect these components together without mistaking repeated tissue observations for independent participants or numerical agreement for biological validation. BRE Spatial is a locally running R/Shiny application that packages a canonical GeoMx reference workflow, compatible processed-expression import, measured-coordinate maps, within-section radius neighborhoods and exploratory participant-aware comparisons. Identifier checks align observations across inputs; exports retain source files, settings and limitations. Four native platform jobs verified application workflows and execution after ZIP extraction. A public mouse-brain fixture retained 2,825 measured spots and six selected genes. A separate brute-force calculation reproduced all 242,072 undirected edges at a 1,000-pixel radius, with maximum distance discrepancy 5.12e-13 pixels. Synthetic fixtures checked participant aggregation, paired and Welch calculations, and invariance to repeated observations. Existing reference audits document both agreement and unresolved reproduction limits. The contribution is an inspectable, packaged workflow using established calculations, rather than a new spatial method. Biological validity, comparative usability and performance at larger scales remain unestablished. The public application operates independently of the private Biomedical Reasoning Engine.

## Introduction

Spatial expression data connect molecular measurements to locations in tissue. The interpretation depends on measurement resolution: an area, capture spot and segmented cell are different observational units. Geometry also requires units, section identity and image registration. Preserving these distinctions is necessary when inspecting candidate targets and when comparing samples from the same participant.

Established public packages already provide substantial spatial analysis. Squidpy includes neighborhood graphs, spatial statistics and image-related workflows [1]. Giotto Suite supports multiscale spatial multiomics analysis and visualization [2]. Seurat provides spatial expression analysis, visualization and integration [3]. BRE Spatial is not a replacement for their analytical breadth. It assembles a smaller workflow around local execution, measured tissue context, participant-level summaries and exportable evidence. Whether that assembly improves researcher usability has not yet been evaluated.

This manuscript describes the implemented developer preview and its software verification. The intended task is to inspect a measured RNA target in tissue, summarize nearby measured positions, compare appropriately annotated participants, and retain enough context to inspect the result afterward. Pathway inference, molecule design, drug efficacy prediction and clinical recommendations are outside the released workflow.

## Implementation and architecture

The application is implemented in R with a Shiny interface (`app.R`). The launcher configures the bundled runtime and libraries, then binds the application to the loopback interface. Native release ZIPs include R and analysis libraries for Apple-silicon Mac, Intel Mac, Windows x64 and an Ubuntu 22.04 x64 baseline. Users need a compatible operating system and existing browser. Native CI used macOS 14 ARM, macOS 15 Intel, Windows Server 2022 and Ubuntu 22.04; compatibility with all operating-system versions is not established. Source archives do not include the complete runtime [4].

Input handling separates the canonical GeoMx workflow from already-processed expression. The reference runner (`scripts/run_reference.R`) evaluates the analysis code distributed with GeoMxWorkflows 1.16.0 through Q3 normalization, substituting explicit input and output directories and saving stage matrices, metadata and session information. It uses GeomxTools and NanoStringNCTools rather than reimplementing the entire GeoMx pipeline [5]. Custom raw GeoMx input uses the kidney profile and therefore needs study-specific parameter review.

The processed-data reader (`processed_input.R`) accepts a ZIP containing a gene-by-observation CSV matrix, sample metadata and provenance JSON. Genes and observation identifiers must be unique and nonempty; matrix and metadata identifiers must match exactly. Values must be finite, and linear-scale values nonnegative. Declared control samples are excluded from biological displays while original files remain available in the run archive. Negative-control target rows must be handled upstream: the importer does not infer their identity from names. The dense input limit is ten million expression values and the interface upload limit is 100 MB.

Optional geometry is validated by `spatial_input.R`; neighborhood and participant computations are implemented in `research_analysis.R`. The interface exposes current analyses and downloads. Complete run exports retain original inputs and current derived results. Relevant input, gene or parameter changes invalidate results, and export code removes stale derived files. The public application requires no UVIE account and does not upload data to UVIE. Local execution does not itself establish a comprehensive security audit or suitability for regulated data.

## Methods

### Provenance and geometry

Processed inputs declare their method, value type, scale and QC status. A declaration of completed QC is user supplied and is not independently verified by import. Supported scales are linear and log2. Tissue maps display linear expression as log2(value + 1), while evidence exports preserve original expression values.

Coordinates must match every biological observation exactly, excluding controls; row order may differ. Each section belongs to one participant. Geometry declares pixel or micrometre units and cell, spot or region resolution. Optional PNG registration applies an origin offset and scalar pixels-per-unit factor. Rotations, shears and reflections require an upstream transformation with provenance. Bounds checks reject inconsistent declared image extents, but cannot establish that an in-bounds image is biologically registered correctly. Per-section color limits require numeric legend inspection when comparing maps [6].

### Radius neighborhoods

For each selected section and compartment subset, the graph connects distinct observations whose Euclidean coordinate distance is less than or equal to a positive researcher-selected radius. Each undirected edge is recorded once; no edge crosses sections and no observation connects to itself. Isolated observations remain in the output. Neighbor-expression means use the supplied expression scale and exclude the focal observation; isolated means are null.

The current implementation evaluates candidate pairs within each section and can require quadratic work in section size. It limits a selection to 5,000 positions and 250,000 edges; exceeding a limit fails the calculation without returning a partial graph. The radius is not optimized against biological outcomes. Pixel distances are not converted to physical distances without supplied calibration. Geometry does not account for tissue holes or boundaries between regions and does not establish contact or signaling. The graph module performs no neighborhood enrichment or spatial-significance test [7].

### Participant aware contrasts

Comparisons require explicit participant, condition and compartment labels, one selected gene and compartment, two conditions and a stated paired or independent design. Participant labels represent the declared independent biological units; the application cannot verify their biological independence. Labels must not be invented solely to satisfy input requirements.

Linear values are transformed observation by observation as log2(value + 1); supplied log2 values are retained. With spatial geometry, transformed observations are averaged within participant, condition and section, then section means receive equal weight within participant and condition. Without geometry, observations are averaged within participant and condition. This reduces the effect of unequal spot sampling on participant counts, but equal section weighting is an analysis choice, not a general correction for sampling bias.

Paired comparisons retain participants observed in both conditions and explicitly align their identifiers. Incomplete participants and inclusion flags are exported. Independent comparisons reject any participant appearing in both conditions. The reported effect is the mean of condition B minus the mean of condition A on the analysis scale. It is not a fitted count-model log fold change.

Results are descriptive by default. Inference requires researcher confirmation of comparable normalized expression, appropriate independence/design and t-test assumptions, plus at least three participants per independent group or three complete pairs. R `stats::t.test` supplies two-sided paired or Welch inference and a 95% confidence interval [8]. Too few participants or unavailable tests retain descriptive output. The minimum is a software guard, not a power calculation. P-values are unadjusted; no model adjusts for batch, age, sex, composition or other covariates. Repeated selection of genes or settings requires a separate multiplicity strategy. This is not an all-gene differential-expression workflow.

## Verification design

Verification distinguishes input integrity, calculation agreement, application behavior, packaging and biological interpretation. Expected software behavior was checked using known-value fixtures, identifier reordering, invalid inputs and comparisons with separately implemented arithmetic. These developer-run checks do not constitute independent investigator validation.

The public display and graph fixture uses the 10x Genomics Mouse Brain Serial Section 2, Sagittal-Anterior dataset, processed with Space Ranger 1.0.0 [9]. The vendor reports one donor and 2,825 spots under tissue. The fixture keeps all filtered spots but only six selected genes. It uses source-image pixels and the vendor low-resolution image factor, 0.051635113. It does not perform transcriptome-wide normalization, infer cell annotations or provide biological replicates. Data attribution and CC BY 4.0 terms are retained.

An independent Python standard-library implementation evaluates every possible coordinate pair using `math.hypot` and compares the edge set, distances, neighbor counts and selected-gene neighbor means with the R export. This checks all pairs for the example, rather than only a sampled subset. Known-coordinate synthetic cases additionally check the inclusive radius boundary, section isolation, self-edge exclusion, isolates and graph limits.

The participant fixture contains twelve synthetic observations from three labeled pairs and two genes. For the selected target, participant means are 1, 2 and 3 in A and 2, 4 and 6 in B. Tests cover known paired and Welch arithmetic, equal section weighting, incomplete pairs, invalid independent designs, descriptive defaults and inference guards. Repeating observations fourfold must not change the participant count, effect or p-value. This fixture tests software behavior, not disease biology.

Browser tests check uploads, module execution, errors, downloads, map updates and stale-result removal. Full-run export tests verify that original inputs are unchanged and current analyses are included. Native jobs additionally run existing kidney and processed-lung regressions, tissue-map checks and the new modules before packaging and after extraction. Publication verifies the exact tested archives rather than rebuilding them [10].

## Results

### Public geometry and synthetic statistics

The public example retained all 2,825 filtered spots. At a radius of 1,000 source-image pixels, the graph contained 242,072 undirected edges. Independent recalculation reproduced the complete edge set and expression summaries. Maximum distance discrepancy was 5.115907697472721e-13 pixels against a tolerance of 1e-9 [11]. This result establishes arithmetic and export agreement for the selected coordinates and settings, not an appropriate biological interaction radius.

The synthetic paired example produced a B-minus-A effect of 2, t = 3.46410161513775, 2 degrees of freedom, two-sided unadjusted p = 0.0741799002274485 and 95% confidence interval approximately -0.48413771175 to 4.48413771175. Twelve observations remained three complete pairs. The confidence interval includes zero. Neither the example nor its p-value is evidence about a biological target [7,10].

### Reference audits

| Audit | Numerical result | Scope |
| --- | --- | --- |
| Canonical kidney raw import | 4,380,870 values; zero mismatches | Import agreement with GeomxTools |
| Kidney Q3 arithmetic | 2,238,951 values within absolute 1e-8 and relative 1e-9 tolerance | Retained-matrix normalization, not independent filtering validation |
| Lung raw import | 2,182,540 values; zero mismatches | Additional-dataset import agreement |
| Lung conditional normalization | 930,320 values pass after documented probe-QC handling | Published selections held fixed; full selection provenance unresolved |
| Ovary raw import | 4,873,085 values; exact agreement | Import agreement; sample linkage remains provisional |
| Ovary published centroid comparison | 112,052 of 168,084 values outside absolute 1e-6 tolerance | Failed comparison retained; intended mapping and complete recipe unresolved |

Kidney Q3 residual RMSE was 8.063644622139701e-14, residual sample SD 8.063508027778256e-14, and maximum absolute error 4.9112713895738125e-11. Residual SD is a numerical difference statistic, not between-participant biological variability or a measure of generalization. The canonical reference inputs differ from the larger vendor archive; the reproduction preserves the package inputs rather than treating them as interchangeable [12].

The initial lung diagnostic omitted the authors' documented probe-outlier handling, producing 24 negative-control differences. A recorded follow-up including that stage resolved all 24. The omission was ours and is not evidence of an author error. Remaining sample-selection and annotation provenance questions are distinct. For ovary, a separate implementation reproduced 3,081,540 recorded normalized values and 168,084 group averages within 1e-10, confirming the specified arithmetic without resolving correspondence to the published grouping [12].

### Packaging and export integrity

All four native jobs completed the required application and unpacked-ZIP checks for application revision `35b98a834c6d251cd3a7e62baf84fd23e25e0fdc`. The public release has eighteen attached assets, including four platform ZIPs, manifests, examples, guides and verification files. The release audit records agreement between asset digests, the checksum inventory and tested archive records. Both example ZIPs were downloaded and matched the tested inputs [10]. These results describe the recorded release checks; they are not a new operating-system test performed for this manuscript.

An export test caught an omission before release: a dedicated neighborhood download worked while the complete run ZIP omitted that result. The implementation was corrected and export checks now verify both analyses and stale-file removal. Retaining such failures and corrections makes the verification boundary inspectable.

## Discussion

BRE Spatial's present contribution is a bounded application workflow around established methods. The software joins an executable GeoMx reference example, processed-expression exploration, measured geometry, participant summaries and explicit evidence exports in platform-specific local bundles. The current tests support correctness claims within their stated input and calculation scope. They do not establish that the workflow is easier to use than alternatives, yields better target decisions or covers all spatial assays.

Reference agreement is strongest when inputs, annotations, transformations and selections are fixed. The lung correction demonstrates why a mismatch should first trigger an audit of the reproduction. The unresolved ovary comparison demonstrates that correct arithmetic does not establish intended sample membership. Missing endometriosis area/nuclei measurements similarly limit complete QC reproduction without establishing that the dataset is unusable or its authors made an error [12].

The application remains limited by dense CSV expression, quadratic radius construction, graph caps, simple image registration and selected-gene inference. It does not provide cell segmentation, deconvolution, pathway analysis, ligand-receptor inference, spatial autocorrelation or automated annotation. A public gene symbol alone does not establish a stable protein identifier or drug target. RNA expression does not establish protein abundance, binding, causation or efficacy.

A future private adapter could attach spatial observations and their provenance to a BRE investigation for authorized users. No such adapter is released. Public packages contain neither private engine access nor a biomedical reasoning service. Any future mapping must preserve observation versus inference, rather than automatically promoting expression or proximity to causal knowledge.

Independent researcher reproduction, usability evaluation, harmonized comparisons with established tools and larger multi-participant datasets would strengthen the contribution. Runtime and memory comparisons should use matched inputs and definitions; they have not been measured here. A real biological use case and external critique are needed before claiming decision utility. Journal selection and submission remain later decisions.

## Availability and declarations

Source code, platform packages, checksums and the exact reproduction examples are available from the public repository and v0.5.0-preview release [4]. The tested application revision is pinned above; supplementary guides may receive documentation-only updates. The consolidated REPRODUCE.md supplies interface steps, expected results and an optional standard-library checker. No new binary version is introduced by this manuscript.

Application code is distributed under MIT terms. Bundled R and third-party dependencies retain their own licenses; MIT does not describe the entire dependency bundle. Public 10x example data require attribution. No new tissue collection or human-participant experiment was performed for these software checks. Source-study ethics statements are not replaced by this manuscript. Author names, affiliations, contributions, funding, competing interests and any required AI-assistance disclosure must be confirmed by the authors before submission. No author identity or declaration is inferred from a GitHub account.

## References

1. Squidpy developers. Spatial Single Cell Analysis in Python. Official documentation. https://squidpy.readthedocs.io/en/stable/ (accessed October 17, 2026).
2. Giotto Suite developers. Spatial multiomics analysis ecosystem. Official documentation. https://giottosuite.com/ (accessed October 17, 2026).
3. Satija Lab. Analysis, visualization, and integration of spatial datasets with Seurat. https://satijalab.org/seurat/articles/spatial_vignette.html (accessed October 17, 2026).
4. UVIE Health. BRE Spatial source and v0.5.0-preview release. https://github.com/BazilTov/uvie-health-bre-spatial-standalone-analysis/releases/tag/v0.5.0-preview
5. GeomxTools maintainers. Bioconductor package documentation. https://bioconductor.org/packages/GeomxTools/ . Exact workflow and bundled dependency versions are recorded with the release.
6. UVIE Health. Spatial input and image-coordinate contract. https://github.com/BazilTov/uvie-health-bre-spatial-standalone-analysis/blob/c45ffb45e3def32ed4d62c330e8f158203a249c8/SPATIAL-INPUT.md
7. UVIE Health. Neighborhood and participant methods. https://github.com/BazilTov/uvie-health-bre-spatial-standalone-analysis/blob/c45ffb45e3def32ed4d62c330e8f158203a249c8/RESEARCH-ANALYSIS.md
8. R Core Team. Student's t-Test, stats::t.test documentation. https://stat.ethz.ch/R-manual/R-devel/library/stats/html/t.test.html (accessed October 17, 2026).
9. 10x Genomics. Mouse Brain Serial Section 2 (Sagittal-Anterior), Space Ranger 1.0.0. https://www.10xgenomics.com/datasets/mouse-brain-serial-section-2-sagittal-anterior-1-standard-1-0-0 (accessed October 17, 2026).
10. UVIE Health. Native, unpacked-package, browser, export and release records. https://github.com/BazilTov/uvie-health-bre-spatial-standalone-analysis/tree/c45ffb45e3def32ed4d62c330e8f158203a249c8/benchmarks/research-analysis
11. UVIE Health. Independent public radius-graph comparison. https://github.com/BazilTov/uvie-health-bre-spatial-standalone-analysis/blob/c45ffb45e3def32ed4d62c330e8f158203a249c8/benchmarks/research-analysis/public-radius-graph-checks.json
12. UVIE Health. Validation record and linked kidney, lung, ovary and endometriosis audits. https://github.com/BazilTov/uvie-health-bre-spatial-standalone-analysis/blob/c45ffb45e3def32ed4d62c330e8f158203a249c8/VALIDATION.md
