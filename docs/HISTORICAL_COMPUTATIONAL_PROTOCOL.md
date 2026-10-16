# Integrated campaign — frozen computational protocol

**Research classification:** exploratory confirmatory-design work; NOT final independent confirmation. The development outcomes have already informed earlier choices, so evaluating new models on them again does not erase that history.

## Outcome protection

- NAS-Bench-101: the exact Phase 8/9B frozen 3,976 architecture records, 2,742 originally training, 617 originally development, **617 reserved holdout**. The package includes the frozen features but labels only for 3,359 originally training/development records. No holdout labels enter this archive.
- NAS-Bench-201: reuse the actual original Phase 9C **15,040-record** frozen cache from the user's laptop, containing 7,808 originally training, 4,736 originally development and **2,496 label-masked holdout** records. The script rejects every synthetic/mismatched/partial cache before running long experiments. The full original source dataset is neither bundled nor re-downloaded.
- Phase 9C's previous synthetic engineering package in the preparation container had only 1,349 processed rows; it is **not eligible** and is rejected.

## Group-wise resampling

The original NAS-Bench-201 split has just five development topology groups. Rather than optimize the same five groups further, this exploratory extension uses **all 31 previously labelled topology groups** and performs leave-one-topology-out cross-validation (one complete active topology withheld in each fold). The six original reserved topology groups remain untouched. This directly exposes the large topology imbalance; do not interpret its standard errors as a sample of new architectures.

NAS-Bench-101 performs deterministic `GroupKFold(5)` across the pooled 3,359 training/development records, with no shared bare connectivity-topology hashes between a fold's training and evaluation rows. The 617 previously locked holdout records remain masked. This is an **exploratory refit** of already-inspected development data, not a final test of a finalized method.

Both benchmarks use ExtraTrees (`n_estimators=96, min_samples_leaf=3, max_features=0.9, n_jobs=2, random_state=11/23`) under the same prespecified configurations:

1. `GRAF`: source-aligned operation-subset feature implementation, not an author-reproduced full official GRAF study.
2. `GRAF_S2`: GRAF + unweighted route and basic eccentricity controls.
3. `GRAF_S2_WEIGHTED`: previous combined features + eccentricity-weighted operation-path features.
4. `GRAF_S2_PLACEBO`: previous combined controls + equal-dimensional SHA-256 deterministic noise features (architecture ID only; no label information).

Report architecture-weighted MAE *and* equal-topology-group MAE (percentage points), seed-specific paired differences, topology-level paired differences and **exploratory 95% cluster bootstrap** intervals. They are not multiplicity-adjusted or independent confirmation, especially for the original five NAS-Bench-201 development topology groups.

## Execution and engineering controls

Python 3.11 environment isolated under `.venv`. A launcher runs dependency preflight, exact symbolic witness verification, randomized independent marked-path tests, end-to-end smoke model fitting, full cached model CV on both benchmarks, summary integrity checks, and one ZIP collector. File hashes + code digests form checkpoint signatures. Any signature mismatch aborts rather than mixing old results. `PAUSE_AFTER_MODEL.cmd` checkpoints safely. `RESUME.cmd` skips identical completed work.

The collector uses POSIX filenames inside ZIP and a single manifest, does not self-hash itself or include the full raw dataset. The ZIP is reopened after creation and every archived SHA-256 is recomputed. Model checkpoint JSONs remain on the local disk for reproducibility; the upload contains compact aggregate summaries and verified logs. Any failure produces a partial diagnostic ZIP rather than requiring another manual packaging repair.

**Power/GPU:** CPU laptop adequate for this stage, no Ollama or DGX required. The final one-time original holdout test remains pending a claim lock and external-baseline audit.
