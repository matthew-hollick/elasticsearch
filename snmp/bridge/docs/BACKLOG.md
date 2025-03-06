# SNMP Bridge Development Backlog

This document tracks pending features and improvements for the Elasticsearch SNMP Bridge.

## In Progress

## High Priority

## Medium Priority

1. **Credential Rotation Support**
   - Implement graceful handling of credential rotation
   - Add support for detecting credential changes in runtime configuration
   - Implement automatic reconnection with new credentials

2. **Metrics Writing Optimization**
   - Implement bulk writing of metrics to Elasticsearch
   - Add configurable batching parameters
   - Optimize the ECS document creation process

## Low Priority

1. **Dashboard Templates**
   - Create Kibana dashboard templates for visualizing SNMP metrics
   - Add setup script for importing dashboards

2. **Alerting Integration**
   - Add integration with Elasticsearch alerting
   - Create example alert configurations for common SNMP metrics

## Completed

1. ✅ **Implement Bootstrap Configuration**
   - Schema definition
   - Configuration loading
   - Validation utilities

2. ✅ **Implement Runtime Configuration**
   - Schema definition
   - Example configuration
   - Validation utilities

3. ✅ **Implement Elasticsearch Credentials**
   - Separate bootstrap and runtime credentials
   - Proper permission model
   - Documentation of credential flow

4. ✅ **Implement Prometheus Exporter Authentication**
   - ✅ Add authentication support for Prometheus exporters in the runtime configuration
   - ✅ Update the exporter schema to include optional authentication credentials
   - ✅ Modify the metrics collection logic to use these credentials when connecting to exporters
   - ✅ Add support for both basic authentication and API tokens
   - ✅ Create example web configuration for SNMP exporter
   - ✅ Update example configurations with exporter authentication examples
   - ✅ Add documentation for exporter authentication
   - ✅ Add tests to verify authentication works correctly

5. ✅ **Implement Elasticsearch Writing**
   - ✅ Create Elasticsearch client with authentication support
   - ✅ Implement ECS document creation from Prometheus metrics
   - ✅ Add bulk writing capability for efficient indexing
   - ✅ Update schema to include index configuration
   - ✅ Add comprehensive error handling
   - ✅ Create test script for Elasticsearch writing
   - ✅ Add documentation for Elasticsearch writing
