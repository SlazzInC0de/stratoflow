# Security Policy

## Supported versions

Only the latest commit on the `main` branch receives security fixes.

## Reporting a vulnerability

Please do not open a public issue for security problems.

Report it privately by either:

- using **Report a vulnerability** under this repository's **Security** tab, or
- emailing **vsuryansh080405@gmail.com** with the subject `[StratoFlow] Security report`.

Include:

- what the issue is and where it lives (Function, Terraform resource, workflow)
- steps or a sample CSV that reproduces it
- the impact you expect

## What to expect

- An acknowledgement within 7 days.
- A fix or a clear decision within 30 days for confirmed issues, depending on severity.
- Credit in the fix commit if you would like it.

## Scope

In scope:

- the Azure Function (`function_app.py`): crafted CSVs that crash it, exhaust memory, or inject formulas into the quarantine CSV
- Terraform (`terraform/`): over-broad RBAC roles, public storage containers, or overly open Synapse firewall rules
- the CI/CD workflow (`.github/workflows/deploy.yml`): secret exposure or untrusted code running with deploy credentials
- vulnerable dependencies

Out of scope: weaknesses in Azure itself, and reports from automated scanners without a working proof of concept.

## Notes for deploying

- Keep Azure credentials in GitHub Actions secrets or a managed identity. Never commit them or `local.settings.json`.
- Keep the storage containers private and restrict the Synapse firewall to the IP ranges you need.
- The bundled CSV and Parquet files in `data/` are synthetic sensor data, not real user data.
