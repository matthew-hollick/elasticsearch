# Create the enrichment policy
resource "elasticstack_elasticsearch_enrich_policy" "service_threshold_policy" {
  name        = "service_threshold_policy"
  policy_type = "match"

  indices       = [elasticstack_elasticsearch_index.service_thresholds.name]
  match_field   = "_enrich_key"
  enrich_fields = ["service", "thresholds"]

  depends_on = [
    elasticstack_elasticsearch_index.service_thresholds,
    null_resource.kafka_production_thresholds,
    null_resource.mysql_production_thresholds,
    null_resource.system_production_thresholds
  ]
}

# Execute the policy to build the enrichment index
resource "null_resource" "execute_enrich_policy" {
  provisioner "local-exec" {
    command = "curl -X POST '${var.elasticsearch_endpoint}/_enrich/policy/service_threshold_policy/_execute' -u ${var.elasticsearch_username}:${var.elasticsearch_password}"
  }

  depends_on = [elasticstack_elasticsearch_enrich_policy.service_threshold_policy]
}
