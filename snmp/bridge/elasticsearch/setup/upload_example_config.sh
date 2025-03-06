#!/bin/bash
# Script to upload example runtime configuration to Elasticsearch
# This script should be run with appropriate permissions

# Configuration
ES_HOST="https://127.0.0.1:9200"
ES_USER="elastic"
ES_PASS="changeme"
CONFIG_FILE="../../examples/runtime_config_example.json"
CONFIG_ID="default"

# Check if the configuration file exists
if [ ! -f "$CONFIG_FILE" ]; then
  echo "Error: Configuration file $CONFIG_FILE not found."
  exit 1
fi

# Read the configuration file
CONFIG_CONTENT=$(cat "$CONFIG_FILE")

# Create a temporary file for the document
TMP_FILE=$(mktemp)
cat > "$TMP_FILE" << EOF
{
  "config_id": "$CONFIG_ID",
  "name": "Default SNMP Bridge Configuration",
  "description": "Example configuration for the Elasticsearch SNMP Bridge",
  "created_at": "$(date -u +"%Y-%m-%dT%H:%M:%S.%3NZ")",
  "updated_at": "$(date -u +"%Y-%m-%dT%H:%M:%S.%3NZ")",
  "version": "1.0.0",
  "active": true,
  "config": $CONFIG_CONTENT
}
EOF

# Upload the configuration to Elasticsearch
echo "Uploading example configuration to Elasticsearch..."
curl -k -X POST "$ES_HOST/.snmp-bridge-config/_doc/$CONFIG_ID" \
  -H "Content-Type: application/json" \
  -u "$ES_USER:$ES_PASS" \
  -d @"$TMP_FILE"

# Clean up
rm "$TMP_FILE"

echo "Example configuration uploaded successfully."
