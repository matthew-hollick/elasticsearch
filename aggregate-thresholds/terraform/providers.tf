provider "elasticstack" {
  elasticsearch {
    endpoints = [var.elasticsearch_endpoint]
    username  = var.elasticsearch_username
    password  = var.elasticsearch_password
    insecure  = var.elasticsearch_insecure
  }
}
