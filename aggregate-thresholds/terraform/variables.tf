variable "elasticsearch_endpoint" {
  description = "Elasticsearch endpoint URL"
  type        = string
  default     = "http://localhost:9200"
}

variable "elasticsearch_username" {
  description = "Elasticsearch username"
  type        = string
  default     = "hedgehog_admin"
}

variable "elasticsearch_password" {
  description = "Elasticsearch password"
  type        = string
  sensitive   = true
}

variable "elasticsearch_insecure" {
  description = "Allow insecure SSL connections"
  type        = bool
  default     = false
}
