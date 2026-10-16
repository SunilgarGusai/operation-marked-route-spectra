# Theorem and evidence map

This reviewer-facing document links the main mathematical claims to the exact verification scripts. It is not a replacement for human review of the article's proofs.

![How the route operator is built](assets/spectral-mechanism.svg)

## Main mathematical statements

| Mathematical item | Verified property | Reproduction entry point |
| :--- | :--- | :--- |
| Seven-vertex operation-labelled seed families | Explicit graph definitions, adjacency and route controls | [Seed arc lists](../figures/seed_arc_lists.json), `verification/verify_v03.py` |
| First family, combined-operation route pencil | Ordinary route spectra agree for all real operation coefficients | `verification/verify_joint_pencils_v04.py` |
| First family, weighted-route separation | Exact second-moment difference for nonnegative operation coefficients | `verification/verify_joint_pencils_v04.py` |
| Second family | Separate operation-control cospectrality; does **not** inherit full joint-pencil identity | `verification/verify_v03.py` |
| Balanced edge-transfer template | Exact template-specific determinant identity and criterion | `verification/verify_balanced_transfer_v05.py` |
| All-width construction | Symbolic identities in integer clone width | `verification/verify_extension_v02.py`, `verification/verify_v03.py` |

The first witness family satisfies the exact second-moment difference

```text
Δ(s,t) = 30 s³ [s + 2t(s+1) + t²(s+2)] > 0,
s ∈ positive integers, t ≥ 0.
```

The second family has **separate-channel**, rather than full joint-pencil, controls. For each marked operation its weighted-route second-moment difference is `−22s⁴`, which is nonzero at every positive replication width.

The algebraic template is specific to its prescribed seven-vertex matrix structure; it should not be presented as a wholly new form of graph switching.

## Reproduce exact identities

```bash
python -m pip install -r requirements-proofs.txt
python run_proofs.py
```

The four suites validate the article's central symbolic identities. They do **not** certify first-in-literature originality. See [claim boundaries](CLAIM_BOUNDARIES.md).

## Mathematical vs empirical evidence

![Three evidence layers](assets/evidence-layers.svg)

The [frozen empirical summaries](FROZEN_RESULTS.md) are development-only, exploratory benchmark evidence. Their arithmetic is checkable using `python tests/check_reported_statistics.py`, but the public checkout cannot refit all 288 models without the historical data and local feature caches. The incremental model improvement confidence intervals include zero; no robust predictive-superiority claim is made.
