# Human ovary atlas: dataset intake and prospective diagnostic

This assessment uses public data from the University of Michigan human ovary atlas, **GSE260686**. It is a workflow test using healthy tissue, not a disease-association study or evidence of treatment efficacy.

## Sources and scope

- Study: https://doi.org/10.1126/sciadv.adm7506
- GEO: https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE260686
- Article: https://pmc.ncbi.nlm.nih.gov/articles/PMC10997207/
- Journal supplements: https://www.ebi.ac.uk/europepmc/webservices/rest/PMC10997207/supplementaryFiles

The raw archive contains all 259 count files listed in GEO: 94 for donor 1 and 165 for donor 2. Supplementary Data S1 has the same per-donor row totals and supplies positive tissue area and nonnegative integer nuclei counts for every row. Eight rows report zero nuclei; these are retained as recorded measurements, not silently replaced or interpreted as an automatic QC pass.

**Annotation linkage is provisional.** GEO titles number AOIs within each donor, whereas Data S1 identifies ROIs and subregions without explicit DCC file identifiers. The diagnostic maps worksheet row order to donor-specific AOI numbering and records this assumption. Matching totals alone does not establish that this mapping is correct. Repeated or blank ROI labels must not be treated as unique sample identifiers.

The paper uses CPM, log2 transformation and quantile normalization, with donor-specific analysis and some ROI consolidation. Its methods differ from the packaged kidney/Q3 workflow. We do not apply kidney cutoffs and label that a reproduction of this study.

## Prospective checks

`plan.json` was written before calculating candidate normalization values. It specifies an independent raw-import comparison and a conditional donor 2 centroid comparison against Data S2, with absolute tolerance 1e-6 and no relative tolerance. The latter checks 18,676 genes across nine published clusters. This does not independently reproduce unspecified author default-QC settings, spatial cell annotation or the original clustering procedure.

The released application's kidney/Q3 runner is unchanged by this diagnostic. This folder does not imply that the ovary workflow has been added to the full release packages.

## Recorded results

- Raw import: **4,873,085 values matched exactly**, with zero missing, extra or different values. GeomxTools adds a terminal `.dcc` extension to sample names; this extension was removed only for identifier alignment. Omitted probe entries were zero-filled and this behavior agrees with GeomxTools.
- Conditional donor 2 centroid comparison: **failed** the recorded absolute tolerance of 1e-6. All 168,084 values were compared; 112,052 were outside tolerance. Residual SD was 0.0853805180, RMSE 0.0853926219 and maximum absolute difference 1.4192713356 on the log2 CPM quantile scale. These are computational residuals, not donor biological variability.
- Clusters 1, 4 and 5 match within tolerance; clusters 2, 3, 6, 7, 8 and 9 do not. This pattern does not establish its cause. Annotation linkage and exact author processing remain unresolved. No claim of author error is supported.

**This is not a completed independent full-pipeline validation or an approved ready-to-use ovary input package.** Matching sample totals and having area/nuclei columns do not establish an unambiguous DCC-to-annotation mapping. The public files remain useful, and the exact raw-import match is a successful scoped check.

## Reproduction

Download the raw archive, GEO family SOFT, probe panel and original Data S1/S2 workbooks into one directory as `raw.tar`, `family.soft.gz`, `panel.pkc.gz`, `adm7506_Data_S1.xlsx`, `adm7506_Data_S2.xlsx`. Verify `input-hashes.json`. The original supplementary ZIP is inside the Europe PMC supplementary-files archive.

The developer-only preparer requires Python with openpyxl. Run `python benchmarks/ovary-atlas/prepare_inputs.py DATA_DIRECTORY`, then `Rscript benchmarks/ovary-atlas/check-ovary.R DATA_DIRECTORY` with GeomxTools 3.14.0 and limma 3.66.0 available. The script records R session information and the donor 2 normalized matrix. `compare_outputs.py` produces the two separate agreement reports, using the unchanged intake/comparison utilities. The diagnostics are not called by the released application.
