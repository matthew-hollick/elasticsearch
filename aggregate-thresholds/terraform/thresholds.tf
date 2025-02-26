# Kafka broker thresholds
locals {
  kafka_production_thresholds = {
    "_enrich_key" : "kafka-production",
    "service" : {
      "type" : "kafka",
      "name" : "kafka",
      "environment" : "production"
    },
    "thresholds" : {
      "kafka" : {
        "broker" : {
          "request" : {
            "queue" : {
              "warning" : 20,
              "critical" : 40
            },
            "time" : {
              "avg" : {
                "ms" : {
                  "warning" : 100,
                  "critical" : 200
                }
              }
            }
          },
          "network" : {
            "io" : {
              "rate" : {
                "warning" : 4000,
                "critical" : 4800
              }
            }
          },
          "messages" : {
            "in" : {
              "rate" : {
                "warning" : 1500,
                "critical" : 1800
              }
            }
          },
          "offline_partition" : {
            "count" : {
              "warning" : 1,
              "critical" : 3
            }
          },
          "under_replicated_partition" : {
            "count" : {
              "warning" : 1,
              "critical" : 3
            }
          }
        }
      },
      "system" : {
        "cpu" : {
          "total" : {
            "pct" : {
              "warning" : 0.7,
              "critical" : 0.9
            }
          },
          "iowait" : {
            "pct" : {
              "warning" : 0.15,
              "critical" : 0.25
            }
          }
        },
        "load" : {
          "1" : {
            "warning" : 3.5,
            "critical" : 7
          },
          "5" : {
            "warning" : 3,
            "critical" : 6
          },
          "15" : {
            "warning" : 2.5,
            "critical" : 5
          }
        },
        "memory" : {
          "used" : {
            "pct" : {
              "warning" : 0.8,
              "critical" : 0.95
            }
          },
          "swap" : {
            "used" : {
              "pct" : {
                "warning" : 0.5,
                "critical" : 0.8
              }
            }
          }
        }
      }
    }
  }
}

resource "null_resource" "kafka_production_thresholds" {
  triggers = {
    document_hash = sha256(jsonencode(local.kafka_production_thresholds))
  }

  provisioner "local-exec" {
    command = <<-EOT
      curl -X PUT "${var.elasticsearch_endpoint}/${elasticstack_elasticsearch_index.service_thresholds.name}/_doc/kafka-production" \
        -H "Content-Type: application/json" \
        -u "${var.elasticsearch_username}:${var.elasticsearch_password}" \
        -d '${jsonencode(local.kafka_production_thresholds)}'
    EOT
  }

  depends_on = [elasticstack_elasticsearch_index.service_thresholds]
}

# MySQL thresholds
locals {
  mysql_production_thresholds = {
    "_enrich_key" : "mysql-production",
    "service" : {
      "type" : "mysql",
      "name" : "mysql",
      "environment" : "production"
    },
    "thresholds" : {
      "mysql" : {
        "connections" : {
          "usage_pct" : {
            "warning" : 70,
            "critical" : 90
          }
        },
        "status" : {
          "threads" : {
            "connected" : {
              "warning" : 80,
              "critical" : 150
            },
            "running" : {
              "warning" : 20,
              "critical" : 40
            }
          },
          "slow_queries" : {
            "warning" : 10,
            "critical" : 25
          },
          "aborted" : {
            "clients" : {
              "warning" : 5,
              "critical" : 15
            },
            "connects" : {
              "warning" : 5,
              "critical" : 15
            }
          }
        }
      },
      "system" : {
        "cpu" : {
          "total" : {
            "pct" : {
              "warning" : 0.7,
              "critical" : 0.9
            }
          },
          "iowait" : {
            "pct" : {
              "warning" : 0.15,
              "critical" : 0.25
            }
          }
        },
        "load" : {
          "1" : {
            "warning" : 3.5,
            "critical" : 7
          },
          "5" : {
            "warning" : 3,
            "critical" : 6
          },
          "15" : {
            "warning" : 2.5,
            "critical" : 5
          }
        },
        "memory" : {
          "used" : {
            "pct" : {
              "warning" : 0.8,
              "critical" : 0.95
            }
          },
          "swap" : {
            "used" : {
              "pct" : {
                "warning" : 0.5,
                "critical" : 0.8
              }
            }
          }
        }
      }
    }
  }
}

resource "null_resource" "mysql_production_thresholds" {
  triggers = {
    document_hash = sha256(jsonencode(local.mysql_production_thresholds))
  }

  provisioner "local-exec" {
    command = <<-EOT
      curl -X PUT "${var.elasticsearch_endpoint}/${elasticstack_elasticsearch_index.service_thresholds.name}/_doc/mysql-production" \
        -H "Content-Type: application/json" \
        -u "${var.elasticsearch_username}:${var.elasticsearch_password}" \
        -d '${jsonencode(local.mysql_production_thresholds)}'
    EOT
  }

  depends_on = [elasticstack_elasticsearch_index.service_thresholds]
}

# System-specific thresholds
locals {
  system_production_thresholds = {
    "_enrich_key" : "system-production",
    "service" : {
      "type" : "system",
      "name" : "system",
      "environment" : "production"
    },
    "thresholds" : {
      "system" : {
        "cpu" : {
          "usage" : {
            "pct" : {
              "warning" : 0.7,
              "critical" : 0.9
            }
          },
          "iowait" : {
            "pct" : {
              "warning" : 0.15,
              "critical" : 0.25
            }
          }
        },
        "load" : {
          "1" : {
            "warning" : 3.5,
            "critical" : 7
          },
          "5" : {
            "warning" : 3,
            "critical" : 6
          },
          "15" : {
            "warning" : 2.5,
            "critical" : 5
          }
        },
        "memory" : {
          "used" : {
            "pct" : {
              "warning" : 0.8,
              "critical" : 0.95
            }
          },
          "swap" : {
            "used" : {
              "pct" : {
                "warning" : 0.5,
                "critical" : 0.8
              }
            }
          }
        }
      }
    }
  }
}

resource "null_resource" "system_production_thresholds" {
  triggers = {
    document_hash = sha256(jsonencode(local.system_production_thresholds))
  }

  provisioner "local-exec" {
    command = <<-EOT
      curl -X PUT "${var.elasticsearch_endpoint}/${elasticstack_elasticsearch_index.service_thresholds.name}/_doc/system-production" \
        -H "Content-Type: application/json" \
        -u "${var.elasticsearch_username}:${var.elasticsearch_password}" \
        -d '${jsonencode(local.system_production_thresholds)}'
    EOT
  }

  depends_on = [elasticstack_elasticsearch_index.service_thresholds]
}
