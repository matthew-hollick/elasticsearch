# Elasticsearch Writing in SNMP Bridge

This document describes how the SNMP Bridge writes metrics to Elasticsearch, including configuration, data mapping, and troubleshooting.

## Overview

The SNMP Bridge collects metrics from Prometheus exporters and writes them to Elasticsearch in an ECS-compliant format. This allows for seamless integration with Kibana for visualization and analysis.

## Configuration

### Runtime Configuration

Elasticsearch connection details are configured in the `global.elasticsearch` section of the runtime configuration:

```json
"global": {
  "elasticsearch": {
    "auth": {
      "username": "hedgehog_snmp_bridge",
      "password": "snmp_secure_password"
    },
    "tls": {
      "verify": true,
      "ca_cert": "/path/to/ca.crt"
    }
  }
}
```

### Target Configuration

Each target can specify its own Elasticsearch index using the `index` field:

```json
"targets": {
  "network_devices": {
    "exporter": "snmp_exporter",
    "interval": 60,
    "index": "metrics-network-daily",
    "metrics": [
      // metric configurations
    ]
  }
}
```

If no index is specified, the default `metrics-snmp-daily` will be used.

## Data Mapping

### ECS Mapping

Metrics are mapped to Elasticsearch Common Schema (ECS) fields using the `ecs_mapping` configuration in each metric:

```json
"metrics": [
  {
    "name": "ifHCInOctets",
    "path": "ifHCInOctets",
    "labels": ["ifName", "ifDescr", "ifAlias"],
    "ecs_mapping": {
      "field": "network.bytes_in",
      "type": "long"
    }
  }
]
```

### Document Structure

Each metric data point is transformed into an ECS-compliant document with the following structure:

```json
{
  "@timestamp": "2025-03-05T10:45:00.000Z",
  "event": {
    "dataset": "snmp.network_devices",
    "module": "snmp",
    "kind": "metric"
  },
  "metric": {
    "name": "ifHCInOctets"
  },
  "labels": {
    "ifName": "eth0",
    "ifDescr": "Ethernet Interface",
    "ifAlias": "External"
  },
  "network": {
    "bytes_in": 1234567
  },
  "target": {
    "device_type": "network",
    "collection_method": "snmp"
  },
  "environment": "production",
  "datacenter": "london",
  "collector": "prometheus-bridge"
}
```

## Bulk Writing

The SNMP Bridge uses Elasticsearch's bulk API to efficiently write multiple metrics in a single request. This improves performance and reduces the load on the Elasticsearch cluster.

## Error Handling

The SNMP Bridge includes robust error handling for Elasticsearch writing:

1. **Connection Errors**: If the connection to Elasticsearch fails, the error is logged and the metrics are not written.
2. **Authentication Errors**: If authentication fails, the error is logged and the metrics are not written.
3. **Bulk Write Errors**: If some documents fail to be indexed, the bridge reports the number of successful and failed documents.

## Troubleshooting

### Common Issues

1. **Connection Refused**: Ensure that Elasticsearch is running and accessible from the SNMP Bridge.
2. **Authentication Failed**: Verify that the username and password are correct.
3. **Index Not Found**: Check that the index exists or that Elasticsearch is configured to create indices automatically.
4. **Mapping Errors**: Ensure that the ECS field types match the actual data types of the metrics.

### Logging

The SNMP Bridge logs all Elasticsearch operations at the INFO level, with errors at the ERROR level. To enable more detailed logging, use the `--verbose` flag when running the bridge.

## Testing

You can test the Elasticsearch writing functionality using the `test_elasticsearch_writer.py` script:

```bash
uv run test_elasticsearch_writer.py --config examples/runtime_config_example.json --target network_devices
```

To perform a dry run without actually writing to Elasticsearch, use the `--dry-run` flag:

```bash
uv run test_elasticsearch_writer.py --config examples/runtime_config_example.json --target network_devices --dry-run
```

## Kibana Integration

Once metrics are written to Elasticsearch, you can create Kibana dashboards to visualize them. The ECS-compliant document structure makes it easy to create visualizations based on fields like `network.bytes_in` or `system.cpu.total.pct`.

## Security Considerations

1. **Credentials**: Store Elasticsearch credentials securely and use a dedicated user with minimal permissions.
2. **TLS**: Enable TLS for all connections to Elasticsearch to encrypt data in transit.
3. **Index Permissions**: Ensure that the Elasticsearch user has only the necessary permissions to write to the specified indices.
