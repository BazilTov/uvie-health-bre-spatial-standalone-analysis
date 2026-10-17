# Walkthrough verification record

The [main walkthrough](../../REPRODUCE.md) consolidates existing v0.5.0-preview inputs, instructions, expected results and historical release records. It adds an optional Python standard-library checker and a manuscript draft; it does not change released application code or rebuild the binary ZIPs.

## Checks executed October 17, 2026

- The local `app.R`, `processed_input.R`, `spatial_input.R` and `research_analysis.R` were compared byte for byte with tested application revision `35b98a834c6d251cd3a7e62baf84fd23e25e0fdc`; all matched.
- `tests/check_research_analysis.R` passed again using the bundled R runtime.
- Fresh local browser runs passed the synthetic participant workflow and the public tissue-map/neighborhood workflow, including downloads, input rejection and stale-state clearing. See [participant browser checks](participant-browser-checks.json) and [public browser checks](public-browser-checks.json).
- [Complete-run export checks](export-checks.json) passed inclusion of current analyses, unchanged inputs and stale-file removal.
- The [new checker](../../scripts/check_walkthrough.py) reproduced the public graph and synthetic paired result from the fresh browser downloads. See [fresh results](fresh-browser-results.json).
- The [download/integrity check](walkthrough-verification.json) checked the four recognized assets present locally: both previously downloaded example ZIPs, PACKAGE-VERIFICATION.json and SHA256SUMS.txt. Its `not_checked` list is explicit. The four large native ZIPs were **not downloaded or executed anew in this documentation task**; their historical release verification is linked from the walkthrough.
- [Rejection checks](checker-rejection-checks.json) confirmed that changed gene identity, participant count, inference confirmation, p-value and example checksum do not silently pass the new checker.
- Thirty relative links across the updated entry point, walkthrough, input guides and manuscript/gap documents resolved locally. The manuscript DOCX was rendered and all seven pages inspected after final layout changes.

These are developer-run software checks. They are not independent researcher adoption, a biological study, a new cross-platform release run, or validation of arbitrary uploaded data. The optional checker is source tooling and is not retroactively included in v0.5.0 full packages. The manuscript's [evidence gaps](../manuscript/EVIDENCE-GAPS.md) remain open.
