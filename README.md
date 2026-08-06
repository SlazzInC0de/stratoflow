\## CI/CD Notes



This project uses GitHub Actions for automated testing (Pytest, linting) on every push/PR. 



Terraform deployment (`terraform apply`) is run manually rather than via CI, because the Azure tenant used for this project (an institutional/student subscription) restricts service principal creation, which is normally required for GitHub Actions to authenticate with Azure. In a production environment with an unrestricted subscription, this would be automated via OIDC federated credentials or a service principal stored in GitHub Secrets.



The `terraform-plan` job in the workflow demonstrates the intended automation and will run once appropriate credentials are available.

