# Create and configure the transform
resource "elasticstack_elasticsearch_transform" "service_health_transform" {
  name        = "service_health_transform"
  description = "Aggregates service metrics for health evaluation"

  source {
    indices = [elasticstack_elasticsearch_index.metrics_test.name]
    query = jsonencode({
      "range" : {
        "@timestamp" : {
          "gte" : "now-1h"
        }
      }
    })
  }

  destination {
    index    = elasticstack_elasticsearch_index.service_health.name
    pipeline = elasticstack_elasticsearch_ingest_pipeline.router_health_evaluation.name
  }

  frequency = "1m"

  sync {
    time {
      field = "@timestamp"
      delay = "30s"
    }
  }

  # Using pivot transformation
  pivot = jsonencode({
    "group_by" : {
      "service.name" : {
        "terms" : {
          "field" : "service.name"
        }
      },
      "service.environment" : {
        "terms" : {
          "field" : "service.environment"
        }
      },
      "service.type" : {
        "terms" : {
          "field" : "service.type"
        }
      },
      "host.name" : {
        "terms" : {
          "field" : "host.name"
        }
      },
      "timestamp_bucket" : {
        "date_histogram" : {
          "field" : "@timestamp",
          "fixed_interval" : "1m"
        }
      }
    },
    "aggregations" : {
      // Kafka metrics
      "kafka.broker.request.queue" : {
        "avg" : {
          "field" : "kafka.broker.request.queue"
        }
      },
      "kafka.broker.request.time.avg.ms" : {
        "avg" : {
          "field" : "kafka.broker.request.time.avg.ms"
        }
      },
      "kafka.broker.topics.count" : {
        "avg" : {
          "field" : "kafka.broker.topics.count"
        }
      },
      "kafka.broker.partitions.count" : {
        "avg" : {
          "field" : "kafka.broker.partitions.count"
        }
      },
      "kafka.broker.partitions.under_replicated" : {
        "avg" : {
          "field" : "kafka.broker.partitions.under_replicated"
        }
      },
      "kafka.broker.partitions.offline" : {
        "avg" : {
          "field" : "kafka.broker.partitions.offline"
        }
      },

      // MySQL metrics
      "mysql.status.threads.connected" : {
        "avg" : {
          "field" : "mysql.status.threads.connected"
        }
      },
      "mysql.status.threads.running" : {
        "avg" : {
          "field" : "mysql.status.threads.running"
        }
      },
      "mysql.status.slow_queries" : {
        "avg" : {
          "field" : "mysql.status.slow_queries"
        }
      },
      "mysql.status.queries" : {
        "avg" : {
          "field" : "mysql.status.queries"
        }
      },
      "mysql.status.handlers.read_first" : {
        "avg" : {
          "field" : "mysql.status.handlers.read_first"
        }
      },
      "mysql.status.handlers.read_key" : {
        "avg" : {
          "field" : "mysql.status.handlers.read_key"
        }
      },
      "mysql.status.handlers.read_next" : {
        "avg" : {
          "field" : "mysql.status.handlers.read_next"
        }
      },
      "mysql.status.handlers.read_rnd" : {
        "avg" : {
          "field" : "mysql.status.handlers.read_rnd"
        }
      },
      "mysql.status.handlers.read_rnd_next" : {
        "avg" : {
          "field" : "mysql.status.handlers.read_rnd_next"
        }
      },

      // System metrics
      "system.cpu.usage.pct" : {
        "avg" : {
          "field" : "system.cpu.usage.pct"
        }
      },
      "system.memory.used.pct" : {
        "avg" : {
          "field" : "system.memory.used.pct"
        }
      },
      "system.filesystem.used.pct" : {
        "avg" : {
          "field" : "system.filesystem.used.pct"
        }
      },
      "system.network.in.bytes" : {
        "avg" : {
          "field" : "system.network.in.bytes"
        }
      },
      "system.network.out.bytes" : {
        "avg" : {
          "field" : "system.network.out.bytes"
        }
      },
      "system.network.in.packets" : {
        "avg" : {
          "field" : "system.network.in.packets"
        }
      },
      "system.network.out.packets" : {
        "avg" : {
          "field" : "system.network.out.packets"
        }
      },

      // Metadata
      "@timestamp" : {
        "max" : {
          "field" : "@timestamp"
        }
      },
      "metadata.slo_relevant" : {
        "max" : {
          "field" : "metadata.slo_relevant"
        }
      }
    }
  })

  retention_policy {
    time {
      field   = "@timestamp"
      max_age = "30d"
    }
  }

  # Set additional transform settings
  docs_per_second      = 1000
  max_page_search_size = 500

  depends_on = [
    elasticstack_elasticsearch_index.metrics_test,
    elasticstack_elasticsearch_index.service_health,
    elasticstack_elasticsearch_ingest_pipeline.router_health_evaluation
  ]
}

# Start the transform after creation
resource "null_resource" "start_transform" {
  provisioner "local-exec" {
    command = "curl -X POST '${var.elasticsearch_endpoint}/_transform/service_health_transform/_start' -u ${var.elasticsearch_username}:${var.elasticsearch_password}"
  }

  depends_on = [elasticstack_elasticsearch_transform.service_health_transform]
}
