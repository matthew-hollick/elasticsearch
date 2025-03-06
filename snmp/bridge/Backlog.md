# Backlog

## High Priority
- Implement Elasticsearch client for retrieving runtime configuration
  - Implement Elasticsearch client with proper authentication and TLS support
  - Handle connection errors and retries
  - Add proper logging
- Implement metrics collection from exporters
  - Create a component to scrape metrics from Prometheus exporters
  - Support different authentication methods
  - Implement retry logic and error handling
- Implement metrics storage in Elasticsearch
  - Write collected metrics to Elasticsearch
  - Support bulk operations for better performance
  - Implement error handling and retries

## Medium Priority
- Add support for TLS client authentication in Elasticsearch client
- Implement health check endpoint
- Add support for Prometheus metrics for self-monitoring
- Add support for Docker deployment
  - Create Dockerfile
  - Set up appropriate entrypoint
  - Configure environment variables

## Low Priority
- Add support for custom index templates
- Implement automatic index lifecycle management
- Add support for alerting on collection failures
- Implement dashboard templates for Kibana
- Write comprehensive documentation
  - Document bootstrap configuration
  - Document runtime configuration
  - Add examples and usage instructions

## Completed
- ✅ Define bootstrap configuration schema
- ✅ Implement bootstrap configuration loader
- ✅ Add support for loading configuration from environment variables
- ✅ Create validation utilities for bootstrap configuration
- ✅ Add example bootstrap configuration
- ✅ Define runtime configuration schema using Pydantic
- ✅ Create JSON schema for runtime configuration
- ✅ Create example runtime configuration file
- ✅ Create utility script for validating runtime configuration
- ✅ Add support for multiple exporters and targets
- ✅ Add support for ECS mappings
- ✅ Move example configuration files to examples directory
- ✅ Update scripts to look for example files in the examples directory
- ✅ Update main.py to support using example configuration
- ✅ Remove transformation functionality from the runtime schema
- ✅ Update validation scripts to use model_dump instead of dict for Pydantic v2 compatibility
- ✅ Remove index management configuration from the runtime schema
- ✅ Create test script for fetching metrics from SNMP exporter
- ✅ Test configuration against real SNMP exporter
