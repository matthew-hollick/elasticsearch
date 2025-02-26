<!-- BEGIN_TF_DOCS -->
# Terraform Configuration for Elasticsearch Aggregate Thresholds

This Terraform configuration manages Elasticsearch indices, ingest pipelines, and transforms for the aggregate thresholds system.

## Architecture

The system processes metrics from Kafka, MySQL, and system sources, enriches them with threshold values, and evaluates health status through specialized pipelines.

## Requirements

| Name | Version |
|------|---------|
| <a name="requirement_terraform"></a> [terraform](#requirement\_terraform) | >= 1.10.5 |
| <a name="requirement_elasticstack"></a> [elasticstack](#requirement\_elasticstack) | >= 0.11.13 |
| <a name="requirement_null"></a> [null](#requirement\_null) | >= 3.2.3 |

## Providers

| Name | Version |
|------|---------|
| <a name="provider_elasticstack"></a> [elasticstack](#provider\_elasticstack) | 0.11.13 |
| <a name="provider_null"></a> [null](#provider\_null) | 3.2.3 |

## Modules

No modules.

## Resources

| Name | Type |
|------|------|
| [elasticstack_elasticsearch_enrich_policy.service_threshold_policy](https://registry.terraform.io/providers/elastic/elasticstack/latest/docs/resources/elasticsearch_enrich_policy) | resource |
| [elasticstack_elasticsearch_index.metrics_test](https://registry.terraform.io/providers/elastic/elasticstack/latest/docs/resources/elasticsearch_index) | resource |
| [elasticstack_elasticsearch_index.service_health](https://registry.terraform.io/providers/elastic/elasticstack/latest/docs/resources/elasticsearch_index) | resource |
| [elasticstack_elasticsearch_index.service_thresholds](https://registry.terraform.io/providers/elastic/elasticstack/latest/docs/resources/elasticsearch_index) | resource |
| [elasticstack_elasticsearch_index_document.kafka_production_thresholds](https://registry.terraform.io/providers/elastic/elasticstack/latest/docs/resources/elasticsearch_index_document) | resource |
| [elasticstack_elasticsearch_index_document.mysql_production_thresholds](https://registry.terraform.io/providers/elastic/elasticstack/latest/docs/resources/elasticsearch_index_document) | resource |
| [elasticstack_elasticsearch_index_document.system_production_thresholds](https://registry.terraform.io/providers/elastic/elasticstack/latest/docs/resources/elasticsearch_index_document) | resource |
| [elasticstack_elasticsearch_ingest_pipeline.kafka_health_evaluation](https://registry.terraform.io/providers/elastic/elasticstack/latest/docs/resources/elasticsearch_ingest_pipeline) | resource |
| [elasticstack_elasticsearch_ingest_pipeline.mysql_health_evaluation](https://registry.terraform.io/providers/elastic/elasticstack/latest/docs/resources/elasticsearch_ingest_pipeline) | resource |
| [elasticstack_elasticsearch_ingest_pipeline.router_health_evaluation](https://registry.terraform.io/providers/elastic/elasticstack/latest/docs/resources/elasticsearch_ingest_pipeline) | resource |
| [elasticstack_elasticsearch_ingest_pipeline.slo_health_evaluation](https://registry.terraform.io/providers/elastic/elasticstack/latest/docs/resources/elasticsearch_ingest_pipeline) | resource |
| [elasticstack_elasticsearch_ingest_pipeline.system_health_evaluation](https://registry.terraform.io/providers/elastic/elasticstack/latest/docs/resources/elasticsearch_ingest_pipeline) | resource |
| [elasticstack_elasticsearch_transform.service_health_transform](https://registry.terraform.io/providers/elastic/elasticstack/latest/docs/resources/elasticsearch_transform) | resource |
| [null_resource.execute_enrich_policy](https://registry.terraform.io/providers/hashicorp/null/latest/docs/resources/resource) | resource |
| [null_resource.start_transform](https://registry.terraform.io/providers/hashicorp/null/latest/docs/resources/resource) | resource |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_elasticsearch_endpoint"></a> [elasticsearch\_endpoint](#input\_elasticsearch\_endpoint) | Elasticsearch endpoint URL | `string` | `"http://localhost:9200"` | no |
| <a name="input_elasticsearch_insecure"></a> [elasticsearch\_insecure](#input\_elasticsearch\_insecure) | Allow insecure SSL connections | `bool` | `false` | no |
| <a name="input_elasticsearch_password"></a> [elasticsearch\_password](#input\_elasticsearch\_password) | Elasticsearch password | `string` | n/a | yes |
| <a name="input_elasticsearch_username"></a> [elasticsearch\_username](#input\_elasticsearch\_username) | Elasticsearch username | `string` | `"hedgehog_admin"` | no |

## Outputs

| Name | Description |
|------|-------------|
| <a name="output_metrics_index_name"></a> [metrics\_index\_name](#output\_metrics\_index\_name) | Name of the metrics index |
| <a name="output_router_pipeline_name"></a> [router\_pipeline\_name](#output\_router\_pipeline\_name) | Name of the router pipeline |
| <a name="output_service_health_index_name"></a> [service\_health\_index\_name](#output\_service\_health\_index\_name) | Name of the service health index |
| <a name="output_service_thresholds_index_name"></a> [service\_thresholds\_index\_name](#output\_service\_thresholds\_index\_name) | Name of the service thresholds index |
| <a name="output_transform_name"></a> [transform\_name](#output\_transform\_name) | Name of the service health transform |
<!-- END_TF_DOCS -->
