# Working with this code

Read `SCOPE.md`, `ENVIRONMENT.md` and `configuration.json` before running calculations. Use `run.py`; it creates isolated outputs and checks every numerical payload against its reference. Keep mathematical scope separate across modules.

Require exact numerical agreement with the established references. Retain original output artifacts for traceable verification. Preserve mathematical assertions, use unoptimized Python, retain the declared parameter domains, and include every tail, projection and rounding fee. Changes to numerical formulas require proof and independent validation; output-path and presentation changes must preserve mathematical payloads.

Run numerical kernels through `run.py`, which copies inputs from `core/` into `runs/run-<uuid>/work/` before creating outputs beside the copied source. Preserve completed runs in their original directories. Keep large generated runs and local virtual environments outside version control.

For a change limited to documentation, verify the package after updating its manifest. For numerical or orchestration changes, run all affected modules with `--independent` and compare against the established references. Describe an execution as certified only when every required job completes and all numerical payloads agree with the references.
