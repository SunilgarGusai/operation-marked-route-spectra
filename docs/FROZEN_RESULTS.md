# Frozen exploratory results

The quantities are accuracy-prediction mean absolute errors in **percentage points (pp)**; lower is better.

| Dataset | GRAF + structural controls | With weighted-route features | Mean improvement |
|---|---:|---:|---:|
| NAS-Bench-101 | 1.2272 | 1.2232 | +0.0040 pp |
| NAS-Bench-201 | 0.8842 | 0.8692 | +0.0150 pp |

Equal-topology paired improvement: NAS-Bench-101 +0.00215 pp (exploratory 95% interval −0.02359 to +0.02669); NAS-Bench-201 +0.00656 pp (−0.00634 to +0.01952). Both intervals cross zero.

These are exploratory development-only grouped-cross-validation results, not an independent confirmatory evaluation. All 288 fits were completed in the original research run; **the current public repository cannot reproduce the 288 refits from a fresh checkout** without separately acquired original benchmark inputs and frozen feature caches. Summary arithmetic can be checked, but that is not an end-to-end replication.
