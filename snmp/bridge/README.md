# Prometheus Bridge for Elasticsearch

A flexible bridge for collecting metrics from Prometheus exporters and storing them in Elasticsearch.

## Overview

This application serves as a bridge between Prometheus exporters and Elasticsearch. It collects metrics from various Prometheus exporters, transforms them according to the Elasticsearch Common Schema (ECS), and stores them in Elasticsearch.

The bridge is designed to be flexible and can work with any Prometheus exporter, not just the SNMP exporter. It prioritises simplicity over complex worker architectures.

## Configuration

The application uses a two-level configuration approach:

1. **Bootstrap Configuration**: Minimal configuration needed to start the application and connect to Elasticsearch.
2. **Runtime Configuration**: Detailed configuration stored in Elasticsearch that defines what metrics to collect and how to transform them.

### Bootstrap Configuration

Bootstrap configuration can be provided in several ways:

1. YAML/JSON file specified by the `BRIDGE_CONFIG_FILE` environment variable
2. YAML/JSON file at default locations:
   - `/etc/prometheus-bridge/config.yaml`
   - `/etc/prometheus-bridge/config.json`
   - `~/.prometheus-bridge/config.yaml`
   - `~/.prometheus-bridge/config.json`
   - `./config.yaml`
   - `./config.json`
3. Environment variables prefixed with `BRIDGE_`

Example bootstrap configuration (see `examples/bootstrap_config_example.yaml`):

```yaml
bootstrap:
  elasticsearch:
    url: "https://elasticsearch.hedgehog.internal:9200"
    auth:
      username: "hedgehog_admin"
      password: "secure_password_here"
    tls:
      verify: true
  config_index: "prometheus-bridge-config"
  logging:
    level: "INFO"
```

Environment variable equivalent:

```
BRIDGE_ELASTICSEARCH__URL=https://elasticsearch.hedgehog.internal:9200
BRIDGE_ELASTICSEARCH__AUTH__USERNAME=hedgehog_admin
BRIDGE_ELASTICSEARCH__AUTH__PASSWORD=secure_password_here
BRIDGE_ELASTICSEARCH__TLS__VERIFY=true
BRIDGE_CONFIG_INDEX=prometheus-bridge-config
BRIDGE_LOGGING__LEVEL=INFO
```

### Runtime Configuration

Runtime configuration is stored in Elasticsearch and defines what metrics to collect and how to transform them. See `examples/runtime_config_example.json` for a complete example.

## Project Structure

```
.
├── bootstrap_loader.py        # Loads bootstrap configuration
├── bootstrap_schema.json      # JSON schema for bootstrap configuration
├── bootstrap_schema.py        # Pydantic models for bootstrap configuration
├── examples/                  # Example configuration files
│   ├── bootstrap_config_example.yaml
│   ├── bad_config_example.yaml
│   ├── runtime_config_example.json
│   └── bad_runtime_config_example.json
├── main.py                    # Main application entry point
├── runtime_schema.json        # JSON schema for runtime configuration
├── runtime_schema.py          # Pydantic models for runtime configuration
├── validate_config.py         # Utility to validate bootstrap configuration
└── validate_runtime_config.py # Utility to validate runtime configuration
```

## Usage

### Validating Configuration

You can validate your bootstrap configuration using the provided utility:

```bash
./validate_config.py -c path/to/config.yaml
```

Add the `-v` flag for verbose output:

```bash
./validate_config.py -c path/to/config.yaml -v
```

Use the `-e` flag to validate the example configuration:

```bash
./validate_config.py -e
```

Similarly, you can validate runtime configuration:

```bash
./validate_runtime_config.py --config path/to/config.json
```

Use the `-e` flag to validate the example runtime configuration:

```bash
./validate_runtime_config.py -e
```

Use the `-b` flag to see validation errors with the bad example:

```bash
./validate_runtime_config.py -b
```

### Running the Application

To start the application:

```bash
./main.py -c path/to/config.yaml
```

## Development

### Requirements

- Python 3.13+
- Dependencies listed in pyproject.toml

### Installing Dependencies

```bash
pip install -e .
```

## License

This project is proprietary to Hedgehog Analytics.
