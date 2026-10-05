# Reproducible numerical certificates

This directory contains deterministic, outward-rounded calculations for the accompanying paper. It includes six principal implementations, six independent implementations, and a compatibility implementation used to cross-check the posterior calculation. No simulated paths or downloaded market data are needed.

## Install and run

The resource controls currently require **Windows x86-64 and CPython 3.12**. In PowerShell, from the repository root:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r code/requirements.txt
.\.venv\Scripts\python.exe code/run.py verify
.\.venv\Scripts\python.exe code/run.py environment
.\.venv\Scripts\python.exe code/run.py run --module all --independent
```

The installation requires access to a package index or a separately supplied compatible wheel. No wheel is bundled. After installation, calculations and verification run offline. Do not use `python -O`, `python -OO`, or `PYTHONOPTIMIZE`: assertions enforce certificate conditions.

Each run creates a new `code/runs/run-<uuid>/` directory. Source inputs and reference results are never overwritten. A complete run executes 14 jobs; the Asian pilot and full calculation have separate log files. The run stops on a failed guard, insufficient memory, timeout, process failure, missing output, source mismatch, or reference mismatch.

## Select a calculation

```powershell
.\.venv\Scripts\python.exe code/run.py list
.\.venv\Scripts\python.exe code/run.py run --module asian --independent
.\.venv\Scripts\python.exe code/run.py run --module tt --independent
.\.venv\Scripts\python.exe code/run.py run --module small-xi --independent
.\.venv\Scripts\python.exe code/run.py run --module posterior --independent
.\.venv\Scripts\python.exe code/run.py check --run code/runs/run-<uuid>
```

Replace the final placeholder with the actual run directory. `posterior-zero` is also available separately. The posterior module automatically computes its zero-volatility reference. The independent posterior check also evaluates a compatibility implementation, then verifies equality to the principal implementation after one explicitly documented field-name normalization.

## Contents

| Path | Purpose |
| --- | --- |
| `core/` | Numerical implementations and resource helper |
| `configuration.json` | Module selection, fixed parameter domains, resource contracts |
| `reference/` | Numerical payloads established before the public-package rerun |
| `data/synthetic_quotes.json` | Exact binary64 synthetic observations |
| `SCOPE.md` | Mathematical scope and interpretation |
| `ENVIRONMENT.md` | Dependency and execution requirements |
| `DATA.md` | Observation values and provenance |
| `verification/` | Portability identities and executed validation receipt |
| `MANIFEST.json` | SHA-256 integrity manifest for packaged files |

All mathematical JSON fields, including rational endpoints, arrays, booleans and fee components, must match the reference exactly. Only hash identities and six explicitly listed timing fields are excluded. A match is a reproducibility check, not a substitute for the mathematical proof or the interval-arithmetic assumptions; see the paper and `SCOPE.md`.
