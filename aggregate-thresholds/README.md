## Original Metric Message from Client


## FIXME

```json
{
  "@timestamp": "2025-02-26T10:15:23.456Z",
  "service": {
    "name": "payment-processing",
    "environment": "production",
    "version": "2.3.1",
    "node": {
      "name": "payment-prod-node-03"
    },
    "type": "api"
  },
  "host": {
    "name": "ip-10-2-47-129",
    "ip": "10.2.47.129",
    "os": {
      "platform": "linux",
      "name": "Ubuntu",
      "version": "22.04"
    }
  },
  "metrics": {
    "http": {
      "response_time": {
        "avg": 237,
        "max": 512,
        "p95": 320,
        "p99": 486
      },
      "error_rate": 1.83,
      "request_rate": 421.5,
      "status_codes": {
        "200": 2476,
        "400": 12,
        "401": 5,
        "500": 29
      }
    },
    "system": {
      "cpu": {
        "usage": 76.8,
        "user": 42.1,
        "system": 34.7,
        "iowait": 3.8
      },
      "memory": {
        "usage": 82.3,
        "total_bytes": 16846524416,
        "used_bytes": 13864529392
      },
      "disk": {
        "io_utilization": 12.6,
        "free_space_percent": 43.8
      }
    },
    "jvm": {
      "memory": {
        "heap_used_percent": 67.5,
        "gc": {
          "collection_count": 42,
          "collection_time_ms": 230
        }
      }
    }
  },
  "event": {
    "created": "2025-02-26T10:15:23.456Z",
    "dataset": "metrics",
    "kind": "metric",
    "module": "service"
  },
  "agent": {
    "type": "metricbeat",
    "version": "8.12.0",
    "ephemeral_id": "a762b33c-5dac-4b57-8406-4e547878c4e9"
  },
  "ecs": {
    "version": "8.2.0"
  },
  "metadata": {
    "slo_relevant": true,
    "metric_category": "customer_facing"
  }
}
```

## Message as the Transform Passes it to the Ingest Pipeline

```json
{
  "service": {
    "name": "payment-processing",
    "environment": "production"
  },
  "interval": "2025-02-26T10:15:00.000Z",
  "http.response_time.avg": 237.42,
  "http.error_rate.avg": 1.83,
  "system.cpu.usage.avg": 76.8,
  "system.memory.usage.avg": 82.3,
  "jvm.memory.heap_used_percent.avg": 67.5,
  "doc_count": 12,
  "metadata.slo_relevant": true,
  "metadata.metric_category": "customer_facing"
}
```

## Message After Enrichment and Processing by the Ingest Pipeline

```json
{
  "service": {
    "name": "payment-processing",
    "environment": "production"
  },
  "interval": "2025-02-26T10:15:00.000Z",
  "http.response_time.avg": 237.42,
  "http.error_rate.avg": 1.83,
  "system.cpu.usage.avg": 76.8,
  "system.memory.usage.avg": 82.3,
  "jvm.memory.heap_used_percent.avg": 67.5,
  "doc_count": 12,
  "metadata.slo_relevant": true,
  "metadata.metric_category": "customer_facing",
  "health_evaluation_timestamp": "2025-02-26T10:16:03.789Z",
  "thresholds": {
    "thresholds": {
      "http": {
        "response_time": {
          "avg": {
            "warning": 150,
            "critical": 250
          }
        },
        "error_rate": {
          "warning": 0.5,
          "critical": 2.0
        }
      },
      "system": {
        "cpu": {
          "usage": {
            "warning": 70,
            "critical": 90
          }
        },
        "memory": {
          "usage": {
            "warning": 80,
            "critical": 95
          }
        }
      },
      "jvm": {
        "memory": {
          "heap_used_percent": {
            "warning": 75,
            "critical": 90
          }
        }
      }
    },
    "_enrich_key": "payment-processing-production"
  },
  "health": {
    "status": "warning",
    "issues": [
      {
        "metric": "http.response_time.avg",
        "value": 237.42,
        "threshold": 150,
        "severity": "warning",
        "message": "http.response_time.avg is warning: 237.42 (threshold: 150)"
      },
      {
        "metric": "http.error_rate",
        "value": 1.83,
        "threshold": 0.5,
        "severity": "warning",
        "message": "http.error_rate is warning: 1.83 (threshold: 0.5)"
      },
      {
        "metric": "system.cpu.usage",
        "value": 76.8,
        "threshold": 70,
        "severity": "warning",
        "message": "system.cpu.usage is warning: 76.8 (threshold: 70)"
      },
      {
        "metric": "system.memory.usage",
        "value": 82.3,
        "threshold": 80,
        "severity": "warning",
        "message": "system.memory.usage is warning: 82.3 (threshold: 80)"
      }
    ]
  }
}
```
