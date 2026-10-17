# Evidence gaps before manuscript submission

The manuscript is a software-methods draft for v0.5.0-preview, not a submitted paper or a claim of biological validation. The contribution under evaluation is the packaged, inspectable workflow using established calculations. The records support scoped numerical and package checks; they do not yet establish novelty, adoption, usability improvement or biological decision value.

| Gap | Existing evidence | Next evidence needed | Claims affected |
| --- | --- | --- | --- |
| Independent researcher reproduction | Developer-run fixtures and four native CI jobs | A researcher outside the development process follows REPRODUCE.md, reports versions and expected/observed outputs | Independent validation and ease of reproduction |
| Practical usefulness | Released application and traceable outputs | Researchers analyze a real compatible study and identify a useful question, failure or decision supported by the workflow | Research utility and target-prioritization value |
| Comparative contribution | Qualitative positioning against official tool documentation | Prespecified comparison of a defined task with appropriate established tools; matched data, graph definitions and outputs | Better, faster, easier or unique claims |
| Runtime and memory | Execution success and explicit graph limits | Repeated measurements on documented hardware across representative input sizes; include failures and extraction/setup costs | Scalability and performance |
| Biological participant analysis | Synthetic paired/Welch fixtures | Adequately annotated, independently replicated biological study with reviewed normalization and design | Valid condition effects and generalization |
| Ovary reproduction | Exact raw import and independently matched specified arithmetic | Resolve intended AOI membership and author processing recipe; preserve original failed centroid comparison | Full published-study reproduction |
| Endometriosis QC | Scoped intake and metadata audit | Obtain or document a defensible study-specific solution for missing area/nuclei annotations | Full raw-data QC reproduction |
| External calibration | Developer-calculated agreement tolerances | Independent critique of graph/contrast assumptions, limits, confounding and multiplicity | Statistical appropriateness beyond fixtures |
| Software archival and citation | GitHub release, tag, hashes and pinned revision | Consider a durable versioned archive/DOI and software citation metadata after authors confirm ownership and citation | Long-term accessibility and formal citation |
| Authorship and declarations | Project ownership context only | Confirm authors, affiliations, contributions, funding, competing interests and required AI-assistance disclosure | Submission readiness |

## Submission decision

Do not select a venue solely because the repository is public. First assess whether the contribution and evidence fit a software/application paper. A new algorithm is not claimed. Numerical agreement with established calculations cannot substitute for usefulness, independent evaluation or a clear comparison with existing workflows.

Prepare a reproducibility package containing the manuscript revision, software version, pinned data, expected results, scripts and complete pass/fail scope. Review the target venue's current scope and disclosure requirements only when a submission decision is being considered. No submission, preprint posting, author outreach or new independent validation is authorized or performed by drafting these documents.

## Corrections that must survive revision

- The initial lung negative-control difference was caused by our omitted documented probe-outlier step; all 24 differences resolved when that step was included. It is not an established author error.
- Ovary correspondence to published centroids remains unresolved; independent arithmetic agreement is not a full reproduction pass.
- Synthetic participant data are software fixtures, not an experimental result.
- All-platform package tests are execution checks, not clinical or biological validation.
- Private BRE integration is not implemented and public download grants no engine access.
- The manuscript describes the released preview. Adding a documentation checker does not retroactively place it inside v0.5.0 binary bundles.
