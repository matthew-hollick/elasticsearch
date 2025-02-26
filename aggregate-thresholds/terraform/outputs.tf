output "metrics_index_name" {
  description = "Name of the metrics index"
  value       = elasticstack_elasticsearch_index.metrics_test.name
}

output "service_thresholds_index_name" {
  description = "Name of the service thresholds index"
  value       = elasticstack_elasticsearch_index.service_thresholds.name
}

output "service_health_index_name" {
  description = "Name of the service health index"
  value       = elasticstack_elasticsearch_index.service_health.name
}

output "router_pipeline_name" {
  description = "Name of the router pipeline"
  value       = elasticstack_elasticsearch_ingest_pipeline.router_health_evaluation.name
}

output "transform_name" {
  description = "Name of the service health transform"
  value       = elasticstack_elasticsearch_transform.service_health_transform.name
}
