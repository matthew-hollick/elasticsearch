# SNMP-Bridge for Elasticsearch

A bridge between SNMP data (via Prometheus exporters) and Elasticsearch.

## Overview

This project collects metrics from Prometheus exporters (which gather SNMP data), transforms them into Elasticsearch Common Schema (ECS) format, and sends them to Elasticsearch for storage and analysis.

## Features

- Two-tier configuration system (bootstrap and runtime)
- Worker-based architecture for scalability
- Automatic configuration updates
- Time and size-based batching
- Resilient connection handling

## Getting Started

### Prerequisites

- Python 3.8+
- Access to Elasticsearch
- Access to Prometheus exporters with SNMP data

### Installation

```bash
pip install -r requirements.txt
```

### Configuration

The application uses a two-tier configuration system:

1. **Bootstrap Configuration**: Minimal settings to start the application
   - Can be provided via command line arguments, environment variables, or configuration files
   - Must include Elasticsearch connection details and configuration index name

2. **Runtime Configuration**: Stored in Elasticsearch and periodically checked for updates
   - Contains details for Prometheus exporters, data transformation, and output settings

## Usage

```bash
python -m snmp_bridge --config config.yaml
```

## Development

Please refer to `Rules.md` for development guidelines.
