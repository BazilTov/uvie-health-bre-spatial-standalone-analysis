# Tissue-coordinate maps

The current source adds an optional tissue map to processed-expression input. Previously published v0.3.0 packages do not contain this feature. This first milestone visualizes measured positions and optional registered PNG previews; it does not calculate neighborhoods, distances, differential expression or signaling.

Keep the three required processed-input files. Add `coordinates.csv` and `spatial.json` at the ZIP root, plus declared PNG files. Coordinates must match **every biological expression sample exactly**, excluding controls. Row order may differ. Each section must belong to one participant. A section identifier must identify one specimen section, not a repeated generic label such as “slide1” across participants.

```csv
Sample_ID,section_id,x,y
spot_A,donor1_section1,125,240
spot_B,donor1_section1,225,240
```

```json
{
  "schema_version": 1,
  "units": "pixel",
  "resolution": "spot",
  "y_direction": "down",
  "source": "Dataset accession and coordinate provenance",
  "images": [
    {
      "section_id": "donor1_section1",
      "file": "tissue.png",
      "pixels_per_unit": 0.05,
      "x_origin": 0,
      "y_origin": 0
    }
  ]
}
```

Supported units are `um` (micrometres) or `pixel` (source-image pixels). Resolution is `cell`, `spot` or `region` and is a user-supplied measurement description, not a verified cell annotation. The coordinate origin is the upper left; y increases downward. An image mapping uses `image_x = (x - x_origin) * pixels_per_unit` and the analogous y equation. No rotations, shears or reflected coordinate systems are supported in this milestone. Transform such datasets upstream and document the transformation. Pixel inputs are not physical distance measurements; no physical calibration is invented.

Images are optional. Each uses a unique known section, a root-level filename containing letters, numbers, underscores or hyphens and `.png`, and at most sixteen million pixels. Positions outside the declared image bounds fail loading. This detects inconsistent bounds, not incorrect biological registration that happens to remain inside the image. Inspect image alignment yourself. A missing image does not prevent a coordinate scatter plot when no image is declared.

The map shows the selected gene, section and compartment filter. Linear expression is displayed as log2(value+1); log2 input is displayed unchanged. Color limits are computed per displayed section; compare the numeric legend rather than assuming identical colors mean identical values across sections. Markers indicate positions, not cell outlines or measured spot diameters. Opacity can be changed to inspect underlying histology. Evidence exports preserve original expression values and supplied geometry; run ZIPs retain the input files. Map PNGs support visual inspection, not an inference of protein activity or therapeutic response.

## Public example

`tests/prepare_spatial_fixture.py` prepares a six-gene display subset of the official [10x mouse-brain sagittal anterior section 2 dataset](https://www.10xgenomics.com/datasets/mouse-brain-serial-section-2-sagittal-anterior-1-standard-1-0-0). It keeps every filtered spot, uses vendor image coordinates and preview scale, and intentionally reverses annotation rows to exercise identifier matching. Source archives and hashes are recorded. This is one mouse and one section; it cannot establish disease differences or between-participant consistency.

The fixture uses source-image pixels and the exact vendor low-resolution scale factor. It does not derive a micrometre scale from spot diameter: physical capture diameter and the diameter used in image registration can differ. The source data are CC BY 4.0; attribute 10x Genomics. See the [official spatial output definitions](https://www.10xgenomics.com/support/software/space-ranger/2.1/analysis/outputs/spatial-outputs).
