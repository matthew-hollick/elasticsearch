#!/bin/bash
# Script to create the configuration index for the SNMP Bridge
# This script should be run with appropriate permissions

# Configuration
ES_HOST="https://127.0.0.1:9200"
ES_USER="elastic"
ES_PASS="changeme"

# Create the configuration index
echo "Creating configuration index for SNMP Bridge..."
curl -k -X PUT "$ES_HOST/.snmp-bridge-config" \
  -H "Content-Type: application/json" \
  -u "$ES_USER:$ES_PASS" \
  -d '{
  "settings": {
    "number_of_shards": 1,
    "number_of_replicas": 1
  },
  "mappings": {
    "properties": {
      "config_id": { "type": "keyword" },
      "name": { "type": "keyword" },
      "description": { "type": "text" },
      "created_at": { "type": "date" },
      "updated_at": { "type": "date" },
      "version": { "type": "keyword" },
      "active": { "type": "boolean" },
      "config": { "type": "object", "enabled": false }
    }
  }
}'

echo "Configuration index setup complete."
