#!/bin/bash
# Script to create a dedicated bootstrap user for the Elasticsearch SNMP Bridge
# This user will only have read access to the configuration index
# This script should be run with appropriate permissions

# Configuration
ES_HOST="https://127.0.0.1:9200"
ES_USER="elastic"
ES_PASS="changeme"
BOOTSTRAP_USER="hedgehog_snmp_bootstrap"
BOOTSTRAP_PASS="bootstrap_secure_password"  # Should be changed in production

# Create the role for the Bootstrap user
echo "Creating role for SNMP Bridge Bootstrap user..."
curl -k -X PUT "$ES_HOST/_security/role/snmp_bridge_bootstrap_role" \
  -H "Content-Type: application/json" \
  -u "$ES_USER:$ES_PASS" \
  -d '{
  "cluster": ["monitor"],
  "indices": [
    {
      "names": [".snmp-bridge-config"],
      "privileges": ["read", "view_index_metadata"]
    }
  ]
}'

# Create the Bootstrap user
echo "Creating Bootstrap user for SNMP Bridge..."
curl -k -X PUT "$ES_HOST/_security/user/$BOOTSTRAP_USER" \
  -H "Content-Type: application/json" \
  -u "$ES_USER:$ES_PASS" \
  -d '{
  "password": "'"$BOOTSTRAP_PASS"'",
  "roles": ["snmp_bridge_bootstrap_role"],
  "full_name": "SNMP Bridge Bootstrap User",
  "email": "snmp-bootstrap@hedgehog.internal",
  "metadata": {
    "description": "Bootstrap user for Elasticsearch SNMP Bridge with read-only access to configuration"
  }
}'

echo "Bootstrap user setup complete. Please store the credentials securely."
echo "Username: $BOOTSTRAP_USER"
echo "Password: $BOOTSTRAP_PASS"
echo ""
echo "This user has read-only access to the configuration index (.snmp-bridge-config)."
echo "Use these credentials in your bootstrap configuration file."
