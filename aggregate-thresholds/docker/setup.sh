#!/bin/bash

# Component versions
export ELASTIC_VERSION="8.17.2"  # Latest stable version

# Default passwords - change these in production
export ELASTIC_PASSWORD=${ELASTIC_PASSWORD:-changeme}
export KIBANA_PASSWORD=${KIBANA_PASSWORD:-changeme}

# Clean up any old certificates
rm -rf certs/*

# Start the setup container to generate certificates
docker-compose up setup

# Start Elasticsearch and wait for it to be ready
docker-compose up -d elasticsearch
echo "Waiting for Elasticsearch..."
until curl -k --cacert certs/ca/ca.crt -u elastic:"${ELASTIC_PASSWORD}" https://localhost:9200 >/dev/null 2>&1; do
  sleep 5
done

# Enable trial license
echo "Enabling trial license..."
curl -k --cacert certs/ca/ca.crt -X POST -u elastic:"${ELASTIC_PASSWORD}" \
  "https://localhost:9200/_license/start_trial?acknowledge=true" \
  -H "Content-Type: application/json"

# Set kibana_system user password
echo "Setting kibana_system user password..."
curl -k --cacert certs/ca/ca.crt -X POST -u elastic:"${ELASTIC_PASSWORD}" \
  "https://localhost:9200/_security/user/kibana_system/_password" \
  -H "Content-Type: application/json" \
  -d "{\"password\":\"${KIBANA_PASSWORD}\"}"

# Create service token for Kibana
echo "Creating service token for Kibana..."
TOKEN_RESPONSE=$(curl -k --cacert certs/ca/ca.crt -X POST -u elastic:"${ELASTIC_PASSWORD}" \
  "https://localhost:9200/_security/service/elastic/kibana/credential/token/kibana" \
  -H "Content-Type: application/json")


KIBANA_SERVICE_TOKEN=$(echo "$TOKEN_RESPONSE" | grep -o '"token":{"value":"[^"]*"' | cut -d'"' -f6)
export KIBANA_SERVICE_TOKEN

echo "KIBANA_SERVICE_TOKEN=$KIBANA_SERVICE_TOKEN"

# Save tokens to .env file
echo "Saving environment variables..."
cat > .env << EOL
# Password for the 'elastic' user (at least 6 characters)
ELASTIC_PASSWORD=${ELASTIC_PASSWORD}

# Password for the 'kibana_system' user (at least 6 characters)
KIBANA_PASSWORD=${KIBANA_PASSWORD}

# Kibana service token
KIBANA_SERVICE_TOKEN=${KIBANA_SERVICE_TOKEN}

# Version of Elastic products
ELASTIC_VERSION=${ELASTIC_VERSION}
EOL

# Start Kibana
echo "Starting Kibana..."
docker-compose up -d kibana

echo "Waiting for Kibana to be ready..."
until curl -s --cacert certs/ca/ca.crt https://localhost:5601/api/status | grep -q '"status":{"overall":{"level":"available"'; do
  sleep 5
done

echo "Setup complete! Your environment is now running with:"
echo "- Elasticsearch at https://elasticsearch.hedgehog.internal:9200"
echo "- Kibana at https://kibana.elasticsearch.hedgehog.internal:5601"
echo
echo "Default credentials:"
echo "Username: elastic"
echo "Password: ${ELASTIC_PASSWORD}"
echo
echo "CA Certificate is at: ./certs/ca/ca.crt"
echo
echo "Add the following to your /etc/hosts file:"
echo "127.0.0.1 elasticsearch.hedgehog.internal kibana.elasticsearch.hedgehog.internal"
