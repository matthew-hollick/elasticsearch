"""
Bootstrap configuration loader.

This module provides functionality to load bootstrap configuration from various sources
and validate it against the defined schema.
"""

import os
import yaml
import json
from pathlib import Path
from typing import Dict, Any, Optional
import logging
from pydantic import ValidationError

from bootstrap_schema import BootstrapConfig

logger = logging.getLogger(__name__)


class ConfigurationError(Exception):
    """Exception raised for configuration errors."""

    pass


class BootstrapLoader:
    """
    Loads bootstrap configuration from various sources and validates it against the schema.

    The loader tries to load configuration in the following order:
    1. From a YAML/JSON file specified by the BRIDGE_CONFIG_FILE environment variable
    2. From a YAML/JSON file at a default location (/etc/prometheus-bridge/config.yaml)
    3. From environment variables prefixed with BRIDGE_
    """

    DEFAULT_CONFIG_PATHS = [
        "/etc/prometheus-bridge/config.yaml",
        "/etc/prometheus-bridge/config.json",
        "~/.prometheus-bridge/config.yaml",
        "~/.prometheus-bridge/config.json",
        "./config.yaml",
        "./config.json",
        "./examples/bootstrap_config_example.yaml",
        "./examples/bootstrap_config_example.json",
    ]

    ENV_PREFIX = "BRIDGE_"

    def __init__(self):
        self.raw_config: Dict[str, Any] = {}
        self.config: Optional[BootstrapConfig] = None

    def load(self) -> BootstrapConfig:
        """
        Load configuration from all available sources and validate it.

        Returns:
            BootstrapConfig: Validated bootstrap configuration

        Raises:
            ConfigurationError: If no valid configuration could be loaded or validation failed
        """
        # Try to load from environment variable pointing to a config file
        env_config_path = os.environ.get(f"{self.ENV_PREFIX}CONFIG_FILE")
        if env_config_path:
            try:
                self._load_from_file(env_config_path)
                logger.info(f"Loaded configuration from {env_config_path}")
            except Exception as e:
                raise ConfigurationError(
                    f"Failed to load configuration from {env_config_path}: {str(e)}"
                )

        # If no config loaded yet, try default paths
        if not self.raw_config:
            for path in self.DEFAULT_CONFIG_PATHS:
                expanded_path = os.path.expanduser(path)
                if os.path.exists(expanded_path):
                    try:
                        self._load_from_file(expanded_path)
                        logger.info(f"Loaded configuration from {expanded_path}")
                        break
                    except Exception as e:
                        logger.warning(
                            f"Failed to load configuration from {expanded_path}: {str(e)}"
                        )

        # Load from environment variables and merge with existing config
        env_config = self._load_from_env()
        if env_config:
            self._deep_merge(self.raw_config, env_config)
            logger.info("Merged configuration from environment variables")

        # Validate the configuration
        if not self.raw_config or "bootstrap" not in self.raw_config:
            raise ConfigurationError("No valid bootstrap configuration found")

        try:
            self.config = BootstrapConfig(**self.raw_config["bootstrap"])
            return self.config
        except ValidationError as e:
            raise ConfigurationError(f"Configuration validation failed: {str(e)}")

    def _load_from_file(self, file_path: str) -> None:
        """
        Load configuration from a YAML or JSON file.

        Args:
            file_path: Path to the configuration file

        Raises:
            ConfigurationError: If the file cannot be loaded or parsed
        """
        path = Path(file_path)
        if not path.exists():
            raise ConfigurationError(f"Configuration file not found: {file_path}")

        with open(path, "r") as f:
            if path.suffix.lower() in [".yaml", ".yml"]:
                self.raw_config = yaml.safe_load(f)
            elif path.suffix.lower() == ".json":
                self.raw_config = json.load(f)
            else:
                raise ConfigurationError(f"Unsupported file format: {path.suffix}")

    def _load_from_env(self) -> Dict[str, Any]:
        """
        Load configuration from environment variables.

        Environment variables should be prefixed with BRIDGE_ and use double underscores
        to indicate nesting. For example:

        BRIDGE_ELASTICSEARCH__URL=https://elasticsearch.hedgehog.internal:9200
        BRIDGE_ELASTICSEARCH__AUTH__USERNAME=hedgehog_admin
        BRIDGE_ELASTICSEARCH__AUTH__PASSWORD=secure_password
        BRIDGE_CONFIG_INDEX=prometheus-bridge-config

        Returns:
            Dict containing the configuration loaded from environment variables
        """
        config = {}

        for key, value in os.environ.items():
            if (
                key.startswith(self.ENV_PREFIX)
                and key != f"{self.ENV_PREFIX}CONFIG_FILE"
            ):
                # Remove prefix and split by double underscore
                key_parts = key[len(self.ENV_PREFIX) :].lower().split("__")

                # Start with bootstrap as the root
                if key_parts[0] != "bootstrap":
                    key_parts.insert(0, "bootstrap")

                # Build nested dictionary
                current = config
                for i, part in enumerate(key_parts):
                    if i == len(key_parts) - 1:
                        # Try to parse the value as JSON if it looks like a complex type
                        try:
                            if value.lower() in ["true", "false"]:
                                current[part] = value.lower() == "true"
                            elif value.isdigit():
                                current[part] = int(value)
                            elif value.replace(".", "", 1).isdigit():
                                current[part] = float(value)
                            else:
                                # Try to parse as JSON
                                try:
                                    current[part] = json.loads(value)
                                except json.JSONDecodeError:
                                    current[part] = value
                        except (ValueError, AttributeError):
                            current[part] = value
                    else:
                        if part not in current:
                            current[part] = {}
                        current = current[part]

        return config

    def _deep_merge(self, target: Dict[str, Any], source: Dict[str, Any]) -> None:
        """
        Deep merge two dictionaries, with source taking precedence over target.

        Args:
            target: Target dictionary to merge into
            source: Source dictionary to merge from
        """
        for key, value in source.items():
            if (
                key in target
                and isinstance(target[key], dict)
                and isinstance(value, dict)
            ):
                self._deep_merge(target[key], value)
            else:
                target[key] = value


def load_bootstrap_config() -> BootstrapConfig:
    """
    Load and validate bootstrap configuration.

    Returns:
        BootstrapConfig: Validated bootstrap configuration

    Raises:
        ConfigurationError: If no valid configuration could be loaded or validation failed
    """
    loader = BootstrapLoader()
    return loader.load()


if __name__ == "__main__":
    # Configure basic logging
    logging.basicConfig(level=logging.INFO)

    # Example usage
    try:
        config = load_bootstrap_config()
        print("Configuration loaded successfully:")
        print(f"Elasticsearch URL: {config.elasticsearch.url}")
        print(f"Config Index: {config.config_index}")
    except ConfigurationError as e:
        print(f"Error loading configuration: {e}")
