# Neighborhoods and participant-aware comparisons

These modules are exploratory selected-gene research analyses. They do not infer drug efficacy, cell communication or clinical outcomes. They add no connection or access to the private BRE.

## Neighborhoods

Load processed expression with valid `coordinates.csv` and `spatial.json`. Choose a section on **Tissue map**, a compartment filter in the sidebar, then a positive radius on **Neighborhoods** and press **Calculate neighborhoods**.

The graph is undirected and uses Euclidean distance <= radius on the supplied coordinate positions. It never connects sections, includes no self edges, and retains isolated positions. Both endpoints must be in the selected section and compartment subset. The map colors positions by number of neighbors, independent of selected gene; gene selection changes expression summaries rather than the geometry. The full download contains all edges, distances, counts, coordinates, settings and selected-gene expression. Neighbor mean expression excludes the focal observation, uses the original supplied expression scale, and is null for an isolated observation.

A radius in `pixel` units remains pixels; it is not a physical tissue distance. A radius in `um` uses the supplied micrometre calibration, which is not independently verified. Region-coordinate proximity refers to the supplied representative positions, not boundary contact; spots are not individual cells. Coordinate proximity does not establish tissue connectivity across holes, cell contact or signaling. There are no enrichment, spatial autocorrelation or significance tests in this module. The radius is researcher selected, not automatically optimized for an outcome.

Preview limits: 5,000 selected positions and 250,000 undirected edges. Larger graphs fail without exporting a partial result. The importer may accept more positions than this analysis supports. A spatial index and large-data support remain future work.

Method reference: [Squidpy spatial graph documentation](https://squidpy.readthedocs.io/en/stable/api/squidpy.gr.spatial_neighbors.html), including section/library separation and exclusion of self-neighbors. This implementation is a separately tested R radius graph, not a Squidpy installation or a claim of identical behavior for every Squidpy mode.

## Participant-aware comparison

Use the processed-expression route. Add a complete `condition` column to `metadata.csv` alongside `Sample_ID`, `participant`, `tissue`, `compartment`, and `is_control`. Condition is not inferred from tissue names. Every biological observation must have a condition. Participant labels must identify the actual independent biological units; animals may serve as those units in an animal study. Unique labels alone do not establish independence.

Select exactly one compartment, two different conditions, and the correct study design. This comparison uses the whole imported dataset for that compartment, not the Tissue map section selector or sidebar compartment filter. It does not compare neighborhood summaries.

1. For `linear` inputs, transform each value to `log2(value + 1)`. Supplied `log2` values are used unchanged.
2. With spatial sections, average the transformed observations within each participant/condition/section, then equally weight section means within that participant/condition. This prevents a densely sampled section from receiving more weight simply because it has more spots.
3. Without spatial sections, average observations within each participant/condition. No section identifiers are inferred from slide or tissue labels.
4. Compare participant summaries, never individual spots as independent replicates. The effect is mean condition B minus mean condition A on the analysis scale, not a fitted count-model log fold change.

**Paired design:** retain only participants measured in both conditions and align them explicitly by identifier. Export every excluded incomplete participant and the inclusion flags. Each complete participant contributes one paired difference.

**Independent design:** reject any participant that appears in both selected conditions. Each participant contributes one value in its condition; use Welch's unequal-variance test if inference is enabled.

Results are descriptive by default. To enable exploratory inference, the researcher must explicitly confirm that normalized expression is comparable across samples, identities indicate independent biological units, and the design and t-test assumptions are appropriate. Confirmation is recorded, not independently verified. The application cannot determine whether a normalization protocol adequately removes library-size or batch differences. Raw UMI counts generally need appropriate upstream normalization; the public six-gene mouse example is for display and graph verification, not a multi-participant inferential benchmark.

Inference requires at least three participants per condition or three complete pairs in this preview. This is a software guard, not a guarantee of power or validity. Too few participants, no complete pairs or essentially constant data remain descriptive. Tests are two-sided, with a 95% confidence interval for B minus A and an **unadjusted** p-value. R's established `stats::t.test` performs inference; see [official documentation](https://stat.ethz.ch/R-manual/R-devel/library/stats/html/t.test.html).

These are exploratory selected-gene tests, not an all-gene differential-expression pipeline. No adjustment is made for batch, age, sex, cell composition, other confounders or multiple comparisons. Repeatedly testing genes or settings requires a prespecified multiplicity strategy. No causal or therapeutic claim follows from a p-value. Participant aggregation reduces spot-level pseudoreplication but does not resolve confounding, sampling bias or heterogeneous compartments.

## Evidence and invalidation

Dedicated JSON downloads contain the complete current analysis, settings, source scale, inclusion counts, assumptions and limitations. Current analyses are also included in gene evidence and complete run exports. Gene, input and relevant setting changes clear previous results; stale derived files are removed from run exports. Run outputs retain original input files unchanged. Original expression remains unchanged outside the explicitly reported comparison transformation.

## Verification scope

- Known-distance synthetic graph: exact inclusive boundary, no cross-section edges or self edges, isolates preserved, identifier order independence.
- Known paired and Welch arithmetic, confidence interval and p-value; identifier alignment; repeated observation counts cannot inflate biological sample counts; equal weighting of spatial sections; incomplete-pair exclusion; inference consent and sample-count guards.
- Browser uploads, calculation, error display, downloads and stale-state clearing.
- Existing kidney, processed-lung and measured-coordinate tissue-map workflows remain regression gates.

Synthetic checks establish software behavior, not biological validation. All supported native packages must pass before a release is published. See `VALIDATION.md` for actual executed results; source changes are not equivalent to distributed release changes.
