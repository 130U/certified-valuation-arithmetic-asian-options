# Start here

1. Read `SCOPE.md` to identify the applicable parameter domain and result.
2. Check the Windows/Python requirements in `ENVIRONMENT.md` and install `requirements.txt` into a local virtual environment.
3. Run `python code/run.py verify` and `python code/run.py environment` from the repository root.
4. Run `python code/run.py run --module asian --independent` for the arithmetic Asian certificate, or `--module all --independent` for the complete set.
5. Read the new run's `run-receipt.json`, `mathematical-check.json`, and job logs. The accepted outcome is `COMPLETE` together with `PASS_EXACT_MATHEMATICAL_PAYLOAD`.

Use the installed virtual environment's Python. The public entry point does not retrieve data or invoke external services. Inputs and reference results remain unchanged. The accompanying paper supplies the mathematical argument; the code verifies its finite numerical conditions.
