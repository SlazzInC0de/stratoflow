resource "azurerm_synapse_workspace" "main" {
  name                                  = var.synapse_workspace_name
  resource_group_name                   = azurerm_resource_group.main.name
  location                               = var.location
  storage_data_lake_gen2_filesystem_id = "https://stratoflowdata.dfs.core.windows.net/container1"
  sql_administrator_login               = var.sql_admin_login
  sql_administrator_login_password      = var.sql_admin_password

  identity {
    type = "SystemAssigned"
  }
}

resource "azurerm_synapse_firewall_rule" "allow_azure" {
  name                 = "AllowAllWindowsAzureIps"
  synapse_workspace_id = azurerm_synapse_workspace.main.id
  start_ip_address     = "0.0.0.0"
  end_ip_address       = "0.0.0.0"
}