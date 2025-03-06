# Credential Flow in SNMP Bridge

This document explains the credential flow in the Elasticsearch SNMP Bridge application.

## Overview

The SNMP Bridge uses a two-tier credential structure for enhanced security:

1. **Bootstrap Credentials**: Used to access the configuration index
2. **Runtime Credentials**: Used to write metrics data to indices

## Flow Diagram

```
┌─────────────────────┐                  ┌─────────────────────┐
│                     │                  │                     │
│  Bootstrap Config   │                  │  Elasticsearch      │
│  ----------------   │                  │  ----------------   │
│  - ES URL           │                  │                     │
│  - ES Auth          │◄─── Read ────────┤  .snmp-bridge-config│
│    (hedgehog_admin) │    Config        │  (Configuration     │
│                     │                  │   Index)            │
└─────────────────────┘                  │                     │
         │                               └─────────────────────┘
         │                                         ▲
         │                                         │
         │                                         │
         │                                  Write  │
         ▼                                  Metrics│
┌─────────────────────┐                           │
│                     │                  ┌─────────────────────┐
│  Runtime Config     │                  │                     │
│  ----------------   │                  │  Elasticsearch      │
│  - Exporters        │                  │  ----------------   │
│  - Targets          │                  │                     │
│  - ES Auth          │────── Write ────►│  snmp-metrics-*     │
│    (snmp_bridge)    │      Metrics     │  (Metrics Indices)  │
│                     │                  │                     │
└─────────────────────┘                  └─────────────────────┘
```

## Credential Details

### Bootstrap Credentials

- **Purpose**: Access the configuration index to retrieve runtime configuration
- **Location**: Stored in the bootstrap configuration file or environment variables
- **Permissions**: Read-only access to `.snmp-bridge-config` index
- **Example**:
  ```json
  {
    "elasticsearch": {
      "url": "https://elasticsearch.hedgehog.internal:9200",
      "auth": {
        "username": "hedgehog_admin",
        "password": "secure_password_here"
      }
    },
    "config_index": ".snmp-bridge-config"
  }
  ```

### Runtime Credentials

- **Purpose**: Write metrics data to Elasticsearch indices
- **Location**: Stored within the runtime configuration in Elasticsearch
- **Permissions**: Write access to `snmp-metrics-*` indices
- **Example**:
  ```json
  {
    "global": {
      "elasticsearch": {
        "auth": {
          "username": "hedgehog_snmp_bridge",
          "password": "snmp_secure_password"
        }
      }
    }
  }
  ```

## Security Benefits

1. **Principle of Least Privilege**: Each set of credentials has only the permissions needed for its specific task
2. **Separation of Concerns**: Configuration access is separate from metrics writing
3. **Reduced Attack Surface**: Compromise of one set of credentials doesn't automatically grant access to all functionality
4. **Auditability**: Different users for different operations makes audit trails clearer

## Implementation Notes

- The bootstrap credentials are used only at application startup to retrieve the runtime configuration
- The runtime credentials are extracted from the runtime configuration and used for all metrics writing operations
- Both sets of credentials should be securely managed and rotated according to your organization's security policies
