resource "azurerm_resource_group" "main" {
  name     = var.resource_group_name
  location = "eastus" # matches your existing group's region
}

resource "azurerm_storage_account" "main" {
  name                             = var.storage_account_name
  resource_group_name              = azurerm_resource_group.main.name
  location                         = var.location
  account_tier                     = "Standard"
  account_replication_type         = "LRS"
  allow_nested_items_to_be_public  = true
  cross_tenant_replication_enabled = true
  min_tls_version                  = "TLS1_2"
}

resource "azurerm_storage_container" "raw_uploads" {
  name                  = "raw-uploads"
  storage_account_name  = azurerm_storage_account.main.name
  container_access_type = "private"
}

resource "azurerm_storage_container" "processed_output" {
  name                  = "processed-output"
  storage_account_name  = azurerm_storage_account.main.name
  container_access_type = "private"
}