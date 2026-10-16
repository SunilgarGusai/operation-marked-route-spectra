# Mathematical definitions and computational protocol

The paper studies directed acyclic operation-labelled architecture graphs. For route-count DAG matrix `U`, the all-positive-length route operator is the finite nilpotent-series resolvent `(I-U)^(-1)-I`. Operation-marked routes induce symmetric route matrices. With undirected-support eccentricity diagonal `D`, the corresponding weighted route matrix is `D C + C D`.

The mathematical suites independently verify exact polynomial identities for two distinct seven-vertex seed pairs and their uniform clone families; see `figures/seed_arc_lists.json` and scripts in `verification/`.

Benchmark controls use structural/operation features and source-aligned GRAF descriptors on NAS-Bench-101 and NAS-Bench-201; these are *not* treated as faithful end-to-end reproductions of GRAF, NASGraph or DAG-S.

The exploratory design uses 5 grouped folds and 2 seeds for NB101, plus 31 leave-one-topology-out folds and 2 seeds for NB201 across 4 feature configurations, totaling **288 ExtraTrees fits**. Frozen earlier development records informed the model-design choices. The reserved holdout datasets are excluded. See `docs/BENCHMARK_REPRODUCIBILITY.md` and `docs/HISTORICAL_COMPUTATIONAL_PROTOCOL.md` for implementation details and missing input data.
