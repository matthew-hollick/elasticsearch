# Elasticsearch Setup for SNMP Bridge

This directory contains scripts to set up Elasticsearch for use with the SNMP Bridge application.

## Prerequisites

- Elasticsearch 8.x running and accessible
- `curl` command-line tool installed
- Proper permissions to create users, roles, and indices in Elasticsearch

## Configuration

The scripts are configured to connect to Elasticsearch at `https://127.0.0.1:9200` with the following credentials:
- Username: `elastic`
- Password: `changeme`

If your Elasticsearch instance uses different connection details, please update the variables at the top of each script:
- `ES_HOST`
- `ES_USER`
- `ES_PASS`

## Setup Scripts

The following scripts are available:

1. `cleanup_indices.sh` - Cleans up existing indices and templates before setup
2. `create_user.sh` - Creates a dedicated user and role for the SNMP Bridge application
3. `create_bootstrap_user.sh` - Creates a bootstrap user with read-only access to configuration
4. `create_index_template.sh` - Sets up the index template, component templates, and ILM policy for SNMP metrics
5. `create_config_index.sh` - Creates the configuration index where runtime configurations are stored
6. `upload_example_config.sh` - Uploads the example runtime configuration to Elasticsearch
7. `setup_all.sh` - Master script that runs all the above scripts in sequence

## Running the Setup

To set up everything at once, run:

```bash
chmod +x setup_all.sh
./setup_all.sh
```

Or, to run individual scripts:

```bash
chmod +x create_user.sh
./create_user.sh
```

## What Gets Created

The setup scripts create the following resources in Elasticsearch:

1. **Users and Roles**:
   - Metrics User: `hedgehog_snmp_bridge`
   - Metrics Role: `snmp_bridge_role` with the following permissions:
     - Cluster: `monitor`
     - Indices:
       - `snmp-metrics-*`, `hedgehog-snmp-*`: `write`, `read`, `view_index_metadata`
       - `.snmp-bridge-config`: `read`, `view_index_metadata` (read-only access)
   - Bootstrap User: `hedgehog_snmp_bootstrap`
   - Bootstrap Role: `snmp_bridge_bootstrap_role` with the following permissions:
     - Cluster: `monitor`
     - Indices:
       - `.snmp-bridge-config`: `read`, `view_index_metadata` (read-only access)

2. **Indices and Templates**:
   - Configuration index: `.snmp-bridge-config`
   - Metrics index template: `snmp-metrics-template` (applies to `snmp-metrics-*` and `hedgehog-snmp-*`)
   - Initial metrics index: `snmp-metrics-000001` (for ILM-managed data)
   - Regular metrics index: `hedgehog-snmp-metrics` (for direct writing)
   - Metrics alias: `snmp-metrics`

3. **ILM Policy**:
   - Policy name: `snmp-metrics-policy`
   - Phases: hot (7 days), warm (30 days), cold (60 days), delete (90 days)

## Credential Structure

The SNMP Bridge application uses a two-tier credential structure for enhanced security:

1. **Bootstrap Credentials**:
   - Provided in the bootstrap configuration file
   - Used only to access the configuration index (`.snmp-bridge-config`)
   - Requires only read access to the configuration index
   - Example: `hedgehog_snmp_bootstrap` user with limited permissions

2. **Runtime Credentials**:
   - Stored within the runtime configuration in Elasticsearch
   - Used to write metrics data to the metrics indices
   - Requires write access to metrics indices
   - Example: `hedgehog_snmp_bridge` user with write permissions to `snmp-metrics-*` and `hedgehog-snmp-*`

This separation of credentials follows the principle of least privilege, ensuring that each component has only the permissions it needs to function.

## Security Considerations

- The default password for the SNMP Bridge user is set to `snmp_secure_password`. This should be changed in production.
- The default password for the Bootstrap user is set to `bootstrap_secure_password`. This should be changed in production.
- In a production environment, you should use proper TLS certificates instead of the `-k` flag which skips certificate validation.
- The SNMP Bridge user has minimal permissions - it can only:
  - Write and read metrics data
  - Read configuration data
  - Monitor cluster health
- All index and template creation is done using the `elastic` user.

## Index Naming Conventions

The SNMP Bridge supports two index naming patterns:

1. **ILM-managed indices**: `snmp-metrics-*` (e.g., `snmp-metrics-000001`)
   - Managed by the Index Lifecycle Management (ILM) policy
   - Automatically rolled over based on age or size
   - Suitable for high-volume production environments

2. **Direct-write indices**: `hedgehog-snmp-*` (e.g., `hedgehog-snmp-metrics`)
   - Simple indices without ILM management
   - Suitable for testing or low-volume environments
   - Default in the runtime configuration

You can specify which index to use in the runtime configuration by setting the `index` field in the target configuration.
