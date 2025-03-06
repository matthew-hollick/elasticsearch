# Elasticsearch SNMP Bridge Architecture

This document provides an overview of the Elasticsearch SNMP Bridge architecture, focusing on the data flow and credential management.

## Architecture Diagram

```
┌───────────────────┐     ┌───────────────────┐     ┌───────────────────┐
│                   │     │                   │     │                   │
│  SNMP Exporters   │     │  SNMP Bridge      │     │  Elasticsearch    │
│  ---------------  │     │  ---------------  │     │  ---------------  │
│                   │     │                   │     │                   │
│  ┌─────────────┐  │     │  ┌─────────────┐  │     │  ┌─────────────┐  │
│  │ SNMP        │  │     │  │ Bootstrap   │  │     │  │ Config      │  │
│  │ Exporter 1  │◄─┼─────┼──┤ Config      │  │     │  │ Index       │  │
│  └─────────────┘  │     │  │             │  │     │  │             │  │
│                   │     │  │ (Bootstrap  │◄─┼─────┼──┤ (Read with  │  │
│  ┌─────────────┐  │     │  │  Creds)     │  │     │  │  Bootstrap  │  │
│  │ SNMP        │  │     │  └─────────────┘  │     │  │  Creds)     │  │
│  │ Exporter 2  │◄─┼─────┼───────┐           │     │  └─────────────┘  │
│  └─────────────┘  │     │       │           │     │                   │
│                   │     │       ▼           │     │                   │
│  ┌─────────────┐  │     │  ┌─────────────┐  │     │  ┌─────────────┐  │
│  │ SNMP        │  │     │  │ Runtime     │  │     │  │ Metrics     │  │
│  │ Exporter 3  │◄─┼─────┼──┤ Config      │  │     │  │ Indices     │  │
│  └─────────────┘  │     │  │             │  │     │  │             │  │
│                   │     │  │ (Runtime    │──┼─────┼─►│ (Write with │  │
│                   │     │  │  Creds)     │  │     │  │  Runtime    │  │
│                   │     │  └─────────────┘  │     │  │  Creds)     │  │
│                   │     │                   │     │  └─────────────┘  │
└───────────────────┘     └───────────────────┘     └───────────────────┘
```

## Component Description

### SNMP Exporters

- **Purpose**: Convert SNMP data to Prometheus metrics format
- **Examples**:
  - Prometheus SNMP Exporter
  - Custom SNMP exporters
- **Interface**: HTTP endpoints that return Prometheus-formatted metrics

### SNMP Bridge

- **Bootstrap Configuration**:
  - Stored locally as a file or in environment variables
  - Contains credentials to access the configuration index in Elasticsearch
  - Used only at startup to retrieve the runtime configuration

- **Runtime Configuration**:
  - Retrieved from Elasticsearch using bootstrap credentials
  - Contains:
    - Exporter definitions
    - Target definitions
    - Metrics mappings
    - Elasticsearch credentials for writing metrics

### Elasticsearch

- **Configuration Index**:
  - Name: `.snmp-bridge-config`
  - Contains runtime configurations
  - Accessed using bootstrap credentials (read-only)

- **Metrics Indices**:
  - Pattern: `snmp-metrics-*`
  - Store the collected metrics data
  - Written to using runtime credentials

## Authentication Flow

1. **Bootstrap Authentication**:
   - SNMP Bridge starts with bootstrap configuration
   - Connects to Elasticsearch using bootstrap credentials
   - Retrieves runtime configuration from configuration index

2. **Runtime Authentication**:
   - Extracts Elasticsearch credentials from runtime configuration
   - Uses these credentials for all metrics writing operations
   - These credentials have write access to metrics indices

## Security Considerations

- **Principle of Least Privilege**:
  - Bootstrap user: Read-only access to configuration
  - Runtime user: Write access to metrics indices

- **Credential Isolation**:
  - Bootstrap credentials stored locally
  - Runtime credentials stored in Elasticsearch
  - Compromise of one doesn't automatically compromise the other

- **Auditability**:
  - Different users for different operations
  - Clear audit trail in Elasticsearch logs

## Data Flow

1. SNMP Bridge retrieves runtime configuration from Elasticsearch
2. For each target in the configuration:
   - Connects to the specified SNMP exporter
   - Retrieves metrics in Prometheus format
   - Parses metrics using the prometheus_client library
   - Maps metrics to ECS fields according to configuration
   - Writes metrics to Elasticsearch using runtime credentials

## Scaling Considerations

- The SNMP Bridge can be deployed as multiple instances
- Each instance can handle a subset of targets
- Configuration can be shared across instances via Elasticsearch
