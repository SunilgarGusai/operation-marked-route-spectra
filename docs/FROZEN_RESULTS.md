# Submission-aligned numerical evidence (exploratory)

These are mean absolute errors of validation-accuracy prediction in **percentage points (pp)**, not percentage error rates.

| Benchmark | GRAF + structural controls | + eccentricity-weighted routes | Architecture-weighted improvement |
| :-- | --: | --: | --: |
| NAS-Bench-101 | 1.2272 | 1.2232 | +0.0040 pp |
| NAS-Bench-201 | 0.8842 | 0.8692 | +0.0150 pp |

| Benchmark | Equal-topology improvement | Exploratory topology-bootstrap interval (95%) |
| :-- | --: | :-- |
| NAS-Bench-101 | +0.00215 pp | −0.02359 to +0.02669 pp |
| NAS-Bench-201 | +0.00656 pp | −0.00634 to +0.01952 pp |

Both intervals span zero. These numbers reproduce the *reported summary values* and do not justify a predictive superiority claim. Full-precision values and source columns are in `results/VELE09_Integrated_CV_Metrics.csv` and `results/VELE09_Integrated_Paired_Topology_Comparisons.csv`.

To verify reported internal arithmetic:

```bash
python tests/check_reported_statistics.py
```

This command **does not retrain** ExtraTrees on the original frozen architecture data.
