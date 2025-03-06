#!/bin/bash
# Script to clean up existing indices and data streams before setup
# This script should be run with appropriate permissions

# Configuration
ES_HOST="https://127.0.0.1:9200"
ES_USER="elastic"
ES_PASS="changeme"

echo "Cleaning up existing indices and data streams..."

# Delete data streams if they exist
echo "Checking for existing data streams..."
curl -k -X GET "$ES_HOST/_data_stream" \
  -H "Content-Type: application/json" \
  -u "$ES_USER:$ES_PASS"

# Delete existing index if it exists
echo "Deleting hedgehog-snmp-metrics index if it exists..."
curl -k -X DELETE "$ES_HOST/hedgehog-snmp-metrics" \
  -H "Content-Type: application/json" \
  -u "$ES_USER:$ES_PASS"

# Delete index templates
echo "Deleting existing index templates..."
curl -k -X DELETE "$ES_HOST/_index_template/snmp-metrics-template" \
  -H "Content-Type: application/json" \
  -u "$ES_USER:$ES_PASS"

# Delete component templates
echo "Deleting existing component templates..."
curl -k -X DELETE "$ES_HOST/_component_template/snmp-metrics-mappings" \
  -H "Content-Type: application/json" \
  -u "$ES_USER:$ES_PASS"

curl -k -X DELETE "$ES_HOST/_component_template/snmp-metrics-settings" \
  -H "Content-Type: application/json" \
  -u "$ES_USER:$ES_PASS"

# Create a regular index for hedgehog-snmp-metrics
echo "Creating hedgehog-snmp-metrics index..."
curl -k -X PUT "$ES_HOST/hedgehog-snmp-metrics" \
  -H "Content-Type: application/json" \
  -u "$ES_USER:$ES_PASS" \
  -d '{
  "settings": {
    "number_of_shards": 1,
    "number_of_replicas": 1
  },
  "mappings": {
    "properties": {
      "@timestamp": { "type": "date" },
      "host": {
        "properties": {
          "name": { "type": "keyword" },
          "uptime": { "type": "long" }
        }
      },
      "network": {
        "properties": {
          "interface": {
            "properties": {
              "name": { "type": "keyword" }
            }
          },
          "bytes_in": { "type": "long" },
          "bytes_out": { "type": "long" }
        }
      },
      "event": {
        "properties": {
          "dataset": { "type": "keyword" },
          "module": { "type": "keyword" },
          "kind": { "type": "keyword" }
        }
      },
      "target": { "type": "object", "dynamic": true }
    }
  }
}'

echo "Cleanup complete."
