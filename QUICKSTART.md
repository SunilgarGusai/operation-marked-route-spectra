# Quick start

The principal mathematical results are checked with exact SymPy arithmetic; GPU access and NAS datasets are not required.

```bash
python -m venv .venv
# Activate the environment on your platform
python -m pip install -r requirements-proofs.txt
python run_proofs.py
python tests/check_reported_statistics.py
python scripts/validate_public_artifact.py
```

Expected: four exact verification suites pass, then the numerical-summary and public-artifact consistency checks pass. The latter **do not** refit the 288 neural architecture models.

Read [frozen results](docs/FROZEN_RESULTS.md), [claim boundaries](docs/CLAIM_BOUNDARIES.md), and [data provenance](docs/DATA_PROVENANCE.md) before using this code.
