# Router Health Evaluation Pipeline
resource "elasticstack_elasticsearch_ingest_pipeline" "router_health_evaluation" {
  name        = "router_health_evaluation"
  description = "Router pipeline that handles common operations and routes to specialized pipelines"

  processors = [
    jsonencode({
      "set" : {
        "field" : "health_evaluation_timestamp",
        "value" : "{{_ingest.timestamp}}"
      }
    }),
    jsonencode({
      "set" : {
        "field" : "_enrich_key",
        "value" : "{{service.name}}-{{service.environment}}"
      }
    }),
    jsonencode({
      "enrich" : {
        "field" : "_enrich_key",
        "policy_name" : "service_threshold_policy",
        "target_field" : "thresholds",
        "ignore_missing" : true
      }
    }),
    jsonencode({
      "script" : {
        "description" : "Route document to appropriate pipeline",
        "lang" : "painless",
        "source" : "// Determine which pipeline to route to based on service type\nif (ctx.service?.type == \"kafka\") {\n  ctx.pipeline = \"kafka_health_evaluation\";\n} else if (ctx.service?.type == \"mysql\") {\n  ctx.pipeline = \"mysql_health_evaluation\";\n} else {\n  ctx.pipeline = \"system_health_evaluation\";\n}\n// Always evaluate system metrics\nctx._temp_pipelines = new ArrayList();\nctx._temp_pipelines.add(\"system_health_evaluation\");\n// Always evaluate SLO\nctx._temp_pipelines.add(\"slo_health_evaluation\");"
      }
    }),
    jsonencode({
      "pipeline" : {
        "if" : "ctx.service?.type == 'kafka'",
        "name" : "kafka_health_evaluation"
      }
    }),
    jsonencode({
      "pipeline" : {
        "if" : "ctx.service?.type == 'mysql'",
        "name" : "mysql_health_evaluation"
      }
    }),
    jsonencode({
      "pipeline" : {
        "name" : "system_health_evaluation"
      }
    }),
    jsonencode({
      "pipeline" : {
        "name" : "slo_health_evaluation"
      }
    })
  ]

  depends_on = [
    elasticstack_elasticsearch_enrich_policy.service_threshold_policy,
    null_resource.execute_enrich_policy
  ]
}

# Kafka Health Evaluation Pipeline
resource "elasticstack_elasticsearch_ingest_pipeline" "kafka_health_evaluation" {
  name        = "kafka_health_evaluation"
  description = "Evaluates health of Kafka services based on broker metrics"

  processors = [
    jsonencode({
      "script" : {
        "description" : "Evaluate Kafka broker health",
        "lang" : "painless",
        "source" : file("${path.module}/pipelines/kafka_health_script.painless")
      }
    })
  ]

  depends_on = [elasticstack_elasticsearch_index.service_health]
}

# MySQL Health Evaluation Pipeline
resource "elasticstack_elasticsearch_ingest_pipeline" "mysql_health_evaluation" {
  name        = "mysql_health_evaluation"
  description = "Evaluates health of MySQL services based on database metrics"

  processors = [
    jsonencode({
      "script" : {
        "description" : "Evaluate MySQL health",
        "lang" : "painless",
        "source" : file("${path.module}/pipelines/mysql_health_script.painless")
      }
    })
  ]

  depends_on = [elasticstack_elasticsearch_index.service_health]
}

# System Health Evaluation Pipeline
resource "elasticstack_elasticsearch_ingest_pipeline" "system_health_evaluation" {
  name        = "system_health_evaluation"
  description = "Evaluates basic system health metrics across all service types"

  processors = [
    jsonencode({
      "script" : {
        "description" : "Evaluate system metrics health",
        "lang" : "painless",
        "source" : file("${path.module}/pipelines/system_health_script.painless")
      }
    })
  ]

  depends_on = [elasticstack_elasticsearch_index.service_health]
}

# SLO Health Evaluation Pipeline
resource "elasticstack_elasticsearch_ingest_pipeline" "slo_health_evaluation" {
  name        = "slo_health_evaluation"
  description = "Evaluates service level objectives across services"

  processors = [
    jsonencode({
      "script" : {
        "description" : "Evaluate SLO health",
        "lang" : "painless",
        "source" : file("${path.module}/pipelines/slo_health_script.painless")
      }
    })
  ]

  depends_on = [elasticstack_elasticsearch_index.service_health]
}
