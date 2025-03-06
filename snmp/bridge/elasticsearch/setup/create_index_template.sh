#!/bin/bash
# Script to create index template for SNMP metrics
# This script should be run with appropriate permissions

# Configuration
ES_HOST="https://127.0.0.1:9200"
ES_USER="elastic"
ES_PASS="changeme"

# Create the component template for SNMP metrics mappings
echo "Creating component template for SNMP metrics mappings..."
curl -k -X PUT "$ES_HOST/_component_template/snmp-metrics-mappings" \
  -H "Content-Type: application/json" \
  -u "$ES_USER:$ES_PASS" \
  -d '{
  "template": {
    "mappings": {
      "properties": {
        "@timestamp": { "type": "date" },
        "host": {
          "properties": {
            "name": { "type": "keyword" },
            "description": { "type": "keyword" },
            "location": { "type": "keyword" },
            "contact": { "type": "keyword" },
            "uptime": { "type": "long" },
            "ip": { "type": "ip" }
          }
        },
        "network": {
          "properties": {
            "interface": {
              "properties": {
                "name": { "type": "keyword" },
                "alias": { "type": "keyword" },
                "type": { "type": "keyword" },
                "speed": { "type": "long" },
                "up": { "type": "boolean" },
                "admin_status": { "type": "keyword" },
                "oper_status": { "type": "keyword" }
              }
            }
          }
        },
        "system": {
          "properties": {
            "cpu": {
              "properties": {
                "usage": { "type": "float" },
                "load": {
                  "properties": {
                    "1m": { "type": "float" },
                    "5m": { "type": "float" },
                    "15m": { "type": "float" }
                  }
                }
              }
            },
            "memory": {
              "properties": {
                "total": { "type": "long" },
                "used": { "type": "long" },
                "free": { "type": "long" },
                "usage": { "type": "float" }
              }
            },
            "filesystem": {
              "properties": {
                "name": { "type": "keyword" },
                "mount_point": { "type": "keyword" },
                "total": { "type": "long" },
                "used": { "type": "long" },
                "free": { "type": "long" },
                "usage": { "type": "float" }
              }
            }
          }
        },
        "labels": { "type": "object", "dynamic": true },
        "metric": {
          "properties": {
            "name": { "type": "keyword" }
          }
        }
      }
    }
  }
}'

# Create the component template for SNMP metrics settings
echo "Creating component template for SNMP metrics settings..."
curl -k -X PUT "$ES_HOST/_component_template/snmp-metrics-settings" \
  -H "Content-Type: application/json" \
  -u "$ES_USER:$ES_PASS" \
  -d '{
  "template": {
    "settings": {
      "number_of_shards": 1,
      "number_of_replicas": 1,
      "index.lifecycle.name": "snmp-metrics-policy",
      "index.lifecycle.rollover_alias": "snmp-metrics"
    }
  }
}'

# Create the index template for SNMP metrics
echo "Creating index template for SNMP metrics..."
curl -k -X PUT "$ES_HOST/_index_template/snmp-metrics-template" \
  -H "Content-Type: application/json" \
  -u "$ES_USER:$ES_PASS" \
  -d '{
  "index_patterns": ["snmp-metrics-*", "hedgehog-snmp-*"],
  "template": {
    "aliases": {
      "snmp-metrics": {}
    }
  },
  "composed_of": ["snmp-metrics-mappings", "snmp-metrics-settings"],
  "priority": 500,
  "_meta": {
    "description": "Template for SNMP metrics collected by Elasticsearch SNMP Bridge"
  }
}'

# Create the ILM policy for SNMP metrics
echo "Creating ILM policy for SNMP metrics..."
curl -k -X PUT "$ES_HOST/_ilm/policy/snmp-metrics-policy" \
  -H "Content-Type: application/json" \
  -u "$ES_USER:$ES_PASS" \
  -d '{
  "policy": {
    "phases": {
      "hot": {
        "min_age": "0ms",
        "actions": {
          "rollover": {
            "max_age": "7d",
            "max_size": "50gb"
          },
          "set_priority": {
            "priority": 100
          }
        }
      },
      "warm": {
        "min_age": "30d",
        "actions": {
          "shrink": {
            "number_of_shards": 1
          },
          "forcemerge": {
            "max_num_segments": 1
          },
          "set_priority": {
            "priority": 50
          }
        }
      },
      "cold": {
        "min_age": "60d",
        "actions": {
          "set_priority": {
            "priority": 0
          }
        }
      },
      "delete": {
        "min_age": "90d",
        "actions": {
          "delete": {}
        }
      }
    }
  }
}'

# Create initial index for SNMP metrics
echo "Creating initial index for SNMP metrics..."
curl -k -X PUT "$ES_HOST/snmp-metrics-000001" \
  -H "Content-Type: application/json" \
  -u "$ES_USER:$ES_PASS" \
  -d '{
  "aliases": {
    "snmp-metrics": {
      "is_write_index": true
    }
  }
}'

echo "Index setup complete."
