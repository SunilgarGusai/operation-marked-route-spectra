# Substantive AI assistance and provenance

## Scope and accountability

OpenAI ChatGPT assisted in the project's research planning, discovery and testing of operation-marked spectral constructions, symbolic Python verifiers, experiment code and audits, literature checks, and multiple manuscript drafts. This was **not** limited to proofreading. The human authors remain responsible for proofs, references, experimental interpretations, licensing and the submitted version.

## Source-supported stages

| Stage | AI-assisted work | Traceable evidence in this release |
| --- | --- | --- |
| Mathematical development | Proposed and scrutinized two seed families, infinite-width formulas, pencil identities and balanced edge transfer | `verification/` and `results/V0*_CERTIFICATE.json` |
| Experimental design | Generated/checked architecture feature encoders, grouped-validation protocols, placebo controls, development-only evaluation | `benchmarks/`, `docs/HISTORICAL_COMPUTATIONAL_PROTOCOL.md` |
| Validation | Drafted exact symbolic checks and numerical summaries, inspected failures, documented limits | `run_proofs.py`, `tests/check_reported_statistics.py`, `docs/CLAIM_BOUNDARIES.md` |
| Manuscript | Created and revised proofs, exposition, TikZ figures, tables, bibliography, ELA formatting | Corresponding manuscript source retained by authors; this public repository does not include its pending-submission draft |
| Literature | Assisted prior-art screening, not a certification that no equivalent formulation exists | `docs/CLAIM_BOUNDARIES.md` and paper citations |

ChatGPT GPT-6 was used during October 2026. Do not retrospectively assert a model/version for earlier sessions when not preserved in the historical record.

## Exact historical prompts

The public repository does **not** contain a complete chronological prompt/output archive. Research conversations and local execution artifacts are the primary potential sources for such a reconstruction. This file is a stage-level audit and **must not be represented as every exact prompt, model version, or generated passage**.

ELA requests the available AI tool/version details, methods or prompts, affected material and reproduction code where possible. The associated article must carry a sufficiently specific disclosure, and a more detailed confidential editorial supplement should be retained from verifiable conversation exports. User-provided clearance does not fill missing historical evidence.

## Reproducibility boundaries

Exact symbolic tests can be run from this checkout. Reproducing the full exploratory NAS experiment needs separately obtained official benchmark data, private frozen preprocessing caches and full model-evaluation checkpoints; those materials are not contained in the public release.

Reference: https://journals.uwyo.edu/index.php/ela/announcement/view/45
