<!-- BEGIN_TF_DOCS -->
# Terraform Configuration for Elasticsearch Aggregate Thresholds

This Terraform configuration manages Elasticsearch indices, ingest pipelines, and transforms for the aggregate thresholds system.

## Architecture

This example imagines monitoring of mysql and kafka.

## Requirements

The following requirements are needed by this module:

- <a name="requirement_terraform"></a> [terraform](#requirement\_terraform) (>= 1.10.5)

- <a name="requirement_elasticstack"></a> [elasticstack](#requirement\_elasticstack) (>= 0.11.13)

- <a name="requirement_null"></a> [null](#requirement\_null) (>= 3.2.3)

## Providers

The following providers are used by this module:

- <a name="provider_elasticstack"></a> [elasticstack](#provider\_elasticstack) (0.11.13)

- <a name="provider_null"></a> [null](#provider\_null) (3.2.3)

## Modules

No modules.

## Resources

The following resources are used by this module:

- [elasticstack_elasticsearch_enrich_policy.service_threshold_policy](https://registry.terraform.io/providers/elastic/elasticstack/latest/docs/resources/elasticsearch_enrich_policy) (resource)
- [elasticstack_elasticsearch_index.metrics_test](https://registry.terraform.io/providers/elastic/elasticstack/latest/docs/resources/elasticsearch_index) (resource)
- [elasticstack_elasticsearch_index.service_health](https://registry.terraform.io/providers/elastic/elasticstack/latest/docs/resources/elasticsearch_index) (resource)
- [elasticstack_elasticsearch_index.service_thresholds](https://registry.terraform.io/providers/elastic/elasticstack/latest/docs/resources/elasticsearch_index) (resource)
- [elasticstack_elasticsearch_index_document.kafka_production_thresholds](https://registry.terraform.io/providers/elastic/elasticstack/latest/docs/resources/elasticsearch_index_document) (resource)
- [elasticstack_elasticsearch_index_document.mysql_production_thresholds](https://registry.terraform.io/providers/elastic/elasticstack/latest/docs/resources/elasticsearch_index_document) (resource)
- [elasticstack_elasticsearch_index_document.system_production_thresholds](https://registry.terraform.io/providers/elastic/elasticstack/latest/docs/resources/elasticsearch_index_document) (resource)
- [elasticstack_elasticsearch_ingest_pipeline.kafka_health_evaluation](https://registry.terraform.io/providers/elastic/elasticstack/latest/docs/resources/elasticsearch_ingest_pipeline) (resource)
- [elasticstack_elasticsearch_ingest_pipeline.mysql_health_evaluation](https://registry.terraform.io/providers/elastic/elasticstack/latest/docs/resources/elasticsearch_ingest_pipeline) (resource)
- [elasticstack_elasticsearch_ingest_pipeline.router_health_evaluation](https://registry.terraform.io/providers/elastic/elasticstack/latest/docs/resources/elasticsearch_ingest_pipeline) (resource)
- [elasticstack_elasticsearch_ingest_pipeline.slo_health_evaluation](https://registry.terraform.io/providers/elastic/elasticstack/latest/docs/resources/elasticsearch_ingest_pipeline) (resource)
- [elasticstack_elasticsearch_ingest_pipeline.system_health_evaluation](https://registry.terraform.io/providers/elastic/elasticstack/latest/docs/resources/elasticsearch_ingest_pipeline) (resource)
- [elasticstack_elasticsearch_transform.service_health_transform](https://registry.terraform.io/providers/elastic/elasticstack/latest/docs/resources/elasticsearch_transform) (resource)
- [null_resource.execute_enrich_policy](https://registry.terraform.io/providers/hashicorp/null/latest/docs/resources/resource) (resource)
- [null_resource.start_transform](https://registry.terraform.io/providers/hashicorp/null/latest/docs/resources/resource) (resource)

## Required Inputs

The following input variables are required:

### <a name="input_elasticsearch_password"></a> [elasticsearch\_password](#input\_elasticsearch\_password)

Description: Elasticsearch password

Type: `string`

## Optional Inputs

The following input variables are optional (have default values):

### <a name="input_elasticsearch_endpoint"></a> [elasticsearch\_endpoint](#input\_elasticsearch\_endpoint)

Description: Elasticsearch endpoint URL

Type: `string`

Default: `"http://localhost:9200"`

### <a name="input_elasticsearch_insecure"></a> [elasticsearch\_insecure](#input\_elasticsearch\_insecure)

Description: Allow insecure SSL connections

Type: `bool`

Default: `false`

### <a name="input_elasticsearch_username"></a> [elasticsearch\_username](#input\_elasticsearch\_username)

Description: Elasticsearch username

Type: `string`

Default: `"hedgehog_admin"`

## Outputs

The following outputs are exported:

### <a name="output_metrics_index_name"></a> [metrics\_index\_name](#output\_metrics\_index\_name)

Description: Name of the metrics index

### <a name="output_router_pipeline_name"></a> [router\_pipeline\_name](#output\_router\_pipeline\_name)

Description: Name of the router pipeline

### <a name="output_service_health_index_name"></a> [service\_health\_index\_name](#output\_service\_health\_index\_name)

Description: Name of the service health index

### <a name="output_service_thresholds_index_name"></a> [service\_thresholds\_index\_name](#output\_service\_thresholds\_index\_name)

Description: Name of the service thresholds index

### <a name="output_transform_name"></a> [transform\_name](#output\_transform\_name)

Description: Name of the service health transform
<!-- END_TF_DOCS -->
