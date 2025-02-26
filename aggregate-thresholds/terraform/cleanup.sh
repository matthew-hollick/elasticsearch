#!/bin/bash
if [ -f terraform.tfvars ]; then
  ES_ENDPOINT=$(grep elasticsearch_endpoint terraform.tfvars | cut -d '=' -f2 | tr -d ' "')
  ES_USERNAME=$(grep elasticsearch_username terraform.tfvars | cut -d '=' -f2 | tr -d ' "')
  ES_PASSWORD=$(grep elasticsearch_password terraform.tfvars | cut -d '=' -f2 | tr -d ' "')
else
  echo "terraform.tfvars not found. Please enter the Elasticsearch details manually."
  read -r -p "Elasticsearch endpoint (e.g., http://elasticsearch.hedgehog.internal:9200): " ES_ENDPOINT
  read -r -p "Username: " ES_USERNAME
  read -r -p "Password: " ES_PASSWORD
fi

# I like this, hadent really thought about doing this before, stolen from somewhere.
es_call() {
  local method=$1
  local path=$2

  curl -X "$method" "$ES_ENDPOINT$path" -u "$ES_USERNAME:$ES_PASSWORD" -H "Content-Type: application/json"
  echo
}

echo "Starting cleanup of Elasticsearch resources..."
echo "Stopping transform..."
es_call POST "/_transform/service_health_transform/_stop?force=true"
echo "Deleting transform..."
es_call DELETE "/_transform/service_health_transform"
echo "Deleting ingest pipelines..."
es_call DELETE "/_ingest/pipeline/router_health_evaluation"
es_call DELETE "/_ingest/pipeline/kafka_health_evaluation"
es_call DELETE "/_ingest/pipeline/mysql_health_evaluation"
es_call DELETE "/_ingest/pipeline/system_health_evaluation"
es_call DELETE "/_ingest/pipeline/slo_health_evaluation"
echo "Deleting enrichment policy..."
es_call DELETE "/_enrich/policy/service_threshold_policy"
echo "Deleting indices..."
es_call DELETE "/metrics-test"
es_call DELETE "/service_thresholds"
es_call DELETE "/service-health"
echo "Deleting enrichment indices..."
es_call DELETE "/.enrich-*"
echo "Cleanup completed."
