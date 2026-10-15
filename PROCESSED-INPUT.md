# Explore processed compartment expression

This input route works with compatible tissue-compartment data from any disease or healthy tissue. It imports an existing expression matrix and preserves its stated method and QC status. It does not perform or verify upstream QC, normalization, differential expression, or biological annotation. It is included in v0.3.0 preview packages and current source. The earlier v0.2.0 ZIPs do not contain it.

Create a ZIP with these three files at its root. Choose **Processed expression ZIP**, select the ZIP and press **Load processed expression**.

## matrix.csv

Genes are rows, samples are columns. The first column must be named `gene`. All gene and sample identifiers must be unique and nonempty. Values must be finite numbers with no missing entries. Linear expression must be nonnegative. Up to ten million values are supported. Separate negative-control targets from the gene matrix before importing; the importer does not infer which gene names represent assay controls.

```csv
gene,AOI_1,AOI_2
CD68,5.2,7.1
EPCAM,8.3,4.6
```

## metadata.csv

Include exactly one row per matrix sample, using identical identifiers. Column order and row order may differ; the importer aligns by identifiers. Required columns are `Sample_ID`, `participant`, `tissue`, `compartment`, and `is_control`. Do not invent participant or tissue annotations to satisfy this format. Use de-identified participant labels. Mark a declared unknown explicitly, rather than treating it as a measured value. The application does not model participants or test significance.

```csv
Sample_ID,participant,tissue,compartment,is_control
AOI_1,P1,Lung,Epithelium,FALSE
AOI_2,P1,Lung,Immune,FALSE
```

`is_control` must be exactly `TRUE` or `FALSE`. Declared control samples are excluded from plots and gene-evidence exports; the downloaded run archive retains all supplied input files and records the number excluded. Undeclared controls cannot be inferred automatically.

## provenance.json

```json
{
  "schema_version": 1,
  "method": "Published Q3 normalization followed by log2; study-specific selections",
  "value_type": "log2 Q3-normalized RNA",
  "scale": "log2",
  "qc_status": "partial",
  "source": "Study citation or accession",
  "limitations": ["Full sample-selection QC was not independently reproduced"]
}
```

The method, value type, scale, and QC status are required. `scale` is `linear` or `log2`; `qc_status` is `not_assessed`, `partial`, or `completed`. A supplied `completed` value is a declaration, not verification by UVIE. Other provenance fields are retained in the evidence. Linear values display as log2(value + 1); log2 values display directly, without an extra logarithm. Exported numeric values retain their original scale. Gene evidence uses schema version 2 and the generic `expression_value` field.

Rejecting duplicate or unmatched identifiers, nonnumeric values, missing values, or invalid provenance prevents ambiguous inputs from being displayed as usable findings. Passing these checks establishes input integrity only.

## Optional tissue maps

Current source accepts additional measured-coordinate files and registered PNG previews. See [SPATIAL-INPUT.md](SPATIAL-INPUT.md) for the exact contract and measurement limits. Existing three-file expression inputs continue to work without geometry. Published v0.3.0 packages predate tissue maps.

