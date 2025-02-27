terraform {
  backend "local" {}

  required_version = ">= 1.10.4"

  required_providers {
    elasticstack = {
      source  = "elastic/elasticstack"
      version = ">= 0.11.13"
    }
    null = {
      source  = "hashicorp/null"
      version = ">= 3.2.3"
    }
    http = {
      source  = "hashicorp/http"
      version = ">= 3.4.2"
    }
  }
}
