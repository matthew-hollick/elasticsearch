#!/bin/bash
# Script to create a dedicated user for the Elasticsearch SNMP Bridge
# This script should be run with appropriate permissions

# Configuration
ES_HOST="https://127.0.0.1:9200"
ES_USER="elastic"
ES_PASS="changeme"
BRIDGE_USER="hedgehog_snmp_bridge"
BRIDGE_PASS="snmp_secure_password"  # Should be changed in production

# Create the role for the SNMP Bridge
echo "Creating role for SNMP Bridge..."
curl -k -X PUT "$ES_HOST/_security/role/snmp_bridge_role" \
  -H "Content-Type: application/json" \
  -u "$ES_USER:$ES_PASS" \
  -d '{
  "cluster": ["monitor"],
  "indices": [
    {
      "names": ["snmp-metrics-*", "hedgehog-snmp-*"],
      "privileges": ["write", "read", "view_index_metadata"]
    },
    {
      "names": [".snmp-bridge-config"],
      "privileges": ["read", "view_index_metadata"]
    }
  ]
}'

# Create the user for the SNMP Bridge
echo "Creating user for SNMP Bridge..."
curl -k -X PUT "$ES_HOST/_security/user/$BRIDGE_USER" \
  -H "Content-Type: application/json" \
  -u "$ES_USER:$ES_PASS" \
  -d '{
  "password": "'"$BRIDGE_PASS"'",
  "roles": ["snmp_bridge_role"],
  "full_name": "SNMP Bridge Service Account",
  "email": "snmp-bridge@hedgehog.internal",
  "metadata": {
    "description": "Service account for Elasticsearch SNMP Bridge"
  }
}'

echo "User setup complete. Please store the credentials securely."
echo "Username: $BRIDGE_USER"
echo "Password: $BRIDGE_PASS"
