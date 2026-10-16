# Exploratory architecture benchmark reproducibility

The two architecture-benchmark experiments reused development labels from prior exploratory analyses and are not prospective or confirmatory tests.

| Benchmark | Development records | Grouped method | Held-out labels |
| --- | ---: | --- | ---: |
| NAS-Bench-101 | 3,359 | five-fold GroupKFold (1,529 topology groups), 2 seeds | 617 reserved |
| NAS-Bench-201 | 12,544 | leave-one-topology-out (31 groups), 2 seeds | 2,496 reserved |

The complete campaign used four feature configurations, two seeds, and 5 + 31 folds, totaling 288 ExtraTrees fits. The model had 96 trees, `min_samples_leaf=3`, `max_features=0.9`, `n_jobs=2`, with seeds 11 and 23. Performance values are validation-accuracy mean absolute errors in percentage points. The matched placebo is deterministic hash-derived synthetic features of the same dimension as the added weighted features; it was not generated from target accuracy values.

**Published numerical evidence:** `results/VELE09_Integrated_CV_Metrics.csv` and `results/VELE09_Integrated_Paired_Topology_Comparisons.csv`. Bootstrap intervals are exploratory cluster-level intervals, and both primary intervals include zero. Neither official GRAF end-to-end training nor the original NASGraph or DAG-S pipeline was faithfully reproduced.

**Missing inputs to full refit:** this public candidate does not include the 3,976 architecture record file and frozen development labels of the original NB101 local study, the official 15,040-row NB201 feature cache, the original NB201 labels, or all 288 model checkpoint prediction arrays. Redistribution rights for the original benchmark sources and derived labels require review before publication. This is why this repository presently supports complete mathematical verification and summary-level numerical verification, **not** end-to-end reproduction of the published CV from a fresh checkout.

**Source fingerprints:** `docs/SOURCE_SHA256.json` contains hashes against which locally recovered sources can be verified. The original Phase 9C cache SHA-256 begins `7323dec8`; a synthetic cache must never be substituted. The original benchmark providers and upstream GRAF methods must be cited when those data/features are used.

**Data sources:** NAS-Bench-101 (Ying et al., ICML 2019), NAS-Bench-201 (Dong and Yang, ICLR 2020). The research scripts preserve the development-only split semantics. Do not call the reserved holdout scores, and do not claim that unused holdout testing has occurred.
