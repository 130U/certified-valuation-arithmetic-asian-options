# Execution environment

- Windows x86-64, CPython 3.12, `python-flint==0.8.0`.
- Standard library plus python-flint only. The installed python-flint wheel provides the native interval-arithmetic dependency. No global compiler, TeX, NumPy, simulation engine or external pricing service is required.
- One worker thread. Each numerical worker enforces a Windows Job Object memory limit of 256 MiB. Before execution the runner requires at least 512 MiB available physical memory and available commit memory.
- Explicit per-job timeouts are in `configuration.json`. A full run has 14 sequential jobs; no price bank or unbounded parameter search is launched. On a different machine the same calculation may stop at its resource limit. A stopped run is not a certificate.
- `PYTHONOPTIMIZE`, `-O` and `-OO` are prohibited. Resource and mathematical guards are assertions.
- Linux and macOS execution has not been certified by this package: the mathematical kernels use portable Python/flint operations, but the retained memory controls are Windows-specific. Do not remove those controls and present the result as an unchanged resource contract.

The first installation may access a package index. For an offline machine, obtain an authentic compatible python-flint wheel separately and install it using pip before running these commands. This repository contains no dependency binary. Numerical runs perform no network calls.

`run.py environment` reports the actual interpreter, python-flint version, platform and available memory. Run receipts record durations and source hashes. The checked-in validation receipt describes a completed run; it is not a promised runtime on other hardware.
