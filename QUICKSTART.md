# Quick start — exact mathematics first

The four proof-verification suites are fully self-contained except for their open Python dependencies. **No GPU, NAS-Bench dataset, neural-network retraining or institutional cluster is required.**

![Route-to-spectrum workflow](docs/assets/spectral-mechanism.svg)

## 1. Install

Python 3.11 or a compatible version:

```bash
python -m venv .venv
# Linux/macOS: source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install -r requirements-proofs.txt
```

## 2. Verify the mathematics

```bash
python run_proofs.py
```

Expected result: **four exact SymPy verification suites pass**. For the underlying witness arc lists and theorems, see [theorem map](docs/THEOREM_MAP.md) and [seed definitions](figures/seed_arc_lists.json).

Windows users may alternatively double-click `RUN_PROOFS_WINDOWS.cmd`.

## 3. Check the published numerical summaries

```bash
python tests/check_reported_statistics.py
```

This validates the saved table arithmetic only. It **does not** refit the 288 exploratory NAS-Bench models. See [frozen results](docs/FROZEN_RESULTS.md) and [benchmark reproducibility](docs/BENCHMARK_REPRODUCIBILITY.md).

## 4. Validate the public artifact

```bash
python scripts/validate_public_artifact.py
```

This checks required files, archive manifest coverage, SVG validity, absence of disallowed raw benchmark inputs, and the MIT license.

## 5. Start reading

1. [Research question and main claims](README.md)
2. [Mathematical result map](docs/THEOREM_MAP.md)
3. [Method definitions and protocol](docs/METHOD_PROTOCOL.md)
4. [Frozen numerical results](docs/FROZEN_RESULTS.md)
5. [What is **not** claimed](docs/CLAIM_BOUNDARIES.md)

The public GitHub Actions workflow runs the same proof and artifact tests on each push.
