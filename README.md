\## CI/CD



GitHub Actions runs on every push/PR:

\- \*\*Test \& Lint\*\*: Pytest suite + flake8 on the data validation logic

\- \*\*Terraform Validate \& Format\*\*: Confirms the Terraform configuration is syntactically valid and correctly formatted, without requiring cloud credentials



\*\*Note on deployment\*\*: `terraform plan`/`apply` are run manually rather than in CI. The Azure tenant used for this project (an institutional subscription) restricts service principal / app registration creation, which is required for GitHub Actions to authenticate with Azure. In an unrestricted environment, this would be automated via OIDC federated credentials. This is a real, common constraint in enterprise/institutional cloud environments — not a limitation of the pipeline design itself.

