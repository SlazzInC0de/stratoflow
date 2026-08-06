variable "resource_group_name" {
  default = "stratoflow-rg"
}

variable "location" {
  default = "eastasia"
}

variable "storage_account_name" {
  default = "stratoflowdata"
}

variable "synapse_workspace_name" {
  default = "stratoflow-ws"
}

variable "sql_admin_login" {
  default = "sqladmin"
}

variable "sql_admin_password" {
  sensitive = true
}