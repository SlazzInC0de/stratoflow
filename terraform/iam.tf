resource "azurerm_role_assignment" "synapse_storage_reader" {
  scope                = azurerm_storage_account.main.id
  role_definition_name = "Storage Blob Data Reader"
  principal_id          = azurerm_synapse_workspace.main.identity[0].principal_id
}