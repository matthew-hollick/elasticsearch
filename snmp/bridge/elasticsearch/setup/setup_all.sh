#!/bin/bash
# Master script to run all Elasticsearch setup scripts
# This script should be run with appropriate permissions

# Set the directory to the location of this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR"

# Make all scripts executable
chmod +x *.sh

# Configuration
ES_HOST="https://127.0.0.1:9200"
ES_USER="elastic"
ES_PASS="changeme"

# Check if Elasticsearch is available
echo "Checking Elasticsearch connection..."
if ! curl -k -s -u "$ES_USER:$ES_PASS" "$ES_HOST" > /dev/null; then
  echo "Error: Could not connect to Elasticsearch at $ES_HOST"
  echo "Please ensure Elasticsearch is running and the credentials are correct."
  exit 1
fi

echo "Elasticsearch is available. Starting setup..."

# Run each setup script in sequence
echo "Step 1: Cleaning up existing indices and templates..."
./cleanup_indices.sh

echo "Step 2: Creating metrics user..."
./create_user.sh

echo "Step 3: Creating bootstrap user..."
./create_bootstrap_user.sh

echo "Step 4: Creating index template..."
./create_index_template.sh

echo "Step 5: Creating configuration index..."
./create_config_index.sh

echo "Step 6: Uploading example configuration..."
./upload_example_config.sh

echo "Setup complete!"
echo "The Elasticsearch SNMP Bridge is now ready to use with the following details:"
echo "- Metrics User: hedgehog_snmp_bridge (for writing metrics)"
echo "- Bootstrap User: hedgehog_snmp_bootstrap (for reading configuration)"
echo "- Configuration index: .snmp-bridge-config"
echo "- Metrics index template: snmp-metrics-template"
echo "- Metrics index: hedgehog-snmp-metrics"
echo ""
echo "See the docs/credential_flow.md file for details on how these credentials are used."
