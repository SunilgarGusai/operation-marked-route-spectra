# Reproduce the mathematical results

The exact mathematical verification requires **no benchmark files, GPU, or neural-network retraining**.

```bash
python -m venv .venv
# Linux/macOS: source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install -r requirements-proofs.txt
python run_proofs.py
python tests/check_reported_statistics.py
```

On Windows, `RUN_PROOFS_WINDOWS.cmd` runs the same mathematical suites with a locally available Python installation.

Expected outcomes: four independent exact verification scripts pass; the separate numerical-summary check passes. Results of the latter are *arithmetic consistency checks*, **not** a re-execution of 288 ML fits.

A single command is also provided for the public-artifact metadata, versioning and repository-layout preflight:

```bash
python scripts/validate_public_artifact.py
```

See `docs/FROZEN_RESULTS.md` for paper-aligned numbers, `docs/METHOD_PROTOCOL.md` for the mathematical/benchmark distinction, and `docs/CLAIM_BOUNDARIES.md` for limitations and prohibited claims.
