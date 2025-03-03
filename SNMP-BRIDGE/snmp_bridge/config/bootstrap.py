"""Bootstrap configuration module.

This module handles loading the minimal configuration needed to start the application
from multiple sources: command line arguments, environment variables, and config files.
"""

import argparse
import os
from dataclasses import dataclass
from typing import Any
from typing import Dict

import yaml
from dotenv import load_dotenv


@dataclass
class BootstrapConfig:
    """Represents the minimal configuration needed to bootstrap the application."""

    elasticsearch_url: str
    elasticsearch_username: str
    elasticsearch_password: str
    config_index_name: str

    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> "BootstrapConfig":
        """Create a BootstrapConfig instance from a dictionary."""
        return cls(
            elasticsearch_url=config_dict["elasticsearch_url"],
            elasticsearch_username=config_dict["elasticsearch_username"],
            elasticsearch_password=config_dict["elasticsearch_password"],
            config_index_name=config_dict["config_index_name"],
        )

    def validate(self) -> bool:
        """Validate that all required fields are present and valid."""
        return all(
            [
                self.elasticsearch_url,
                self.elasticsearch_username,
                self.elasticsearch_password,
                self.config_index_name,
            ]
        )


class ConfigLoader:
    """Loads configuration from multiple sources with precedence."""

    def __init__(self):
        """Initialize the ConfigLoader."""
        self._config: Dict[str, Any] = {}

    def load_from_file(self, file_path: str) -> None:
        """Load configuration from a YAML file."""
        if not os.path.exists(file_path):
            return

        with open(file_path, "r") as file:
            file_config = yaml.safe_load(file)
            if file_config and isinstance(file_config, dict):
                self._config.update(file_config)

    def load_from_env(self) -> None:
        """Load configuration from environment variables."""
        # Load from .env file if it exists
        load_dotenv()

        # Map environment variables to config keys
        env_mapping = {
            "ELASTICSEARCH_URL": "elasticsearch_url",
            "ELASTICSEARCH_USERNAME": "elasticsearch_username",
            "ELASTICSEARCH_PASSWORD": "elasticsearch_password",
            "CONFIG_INDEX_NAME": "config_index_name",
        }

        for env_var, config_key in env_mapping.items():
            if env_var in os.environ:
                self._config[config_key] = os.environ[env_var]

    def load_from_args(self) -> None:
        """Load configuration from command line arguments."""
        parser = argparse.ArgumentParser(description="SNMP-Bridge for Elasticsearch")

        parser.add_argument("--config", help="Path to configuration file")
        parser.add_argument("--elasticsearch-url", help="Elasticsearch server URL")
        parser.add_argument("--elasticsearch-username", help="Elasticsearch username")
        parser.add_argument("--elasticsearch-password", help="Elasticsearch password")
        parser.add_argument(
            "--config-index-name",
            help="Name of the Elasticsearch index containing runtime configuration",
        )

        args = parser.parse_args()

        # First, if a config file is specified, load it
        if args.config:
            self.load_from_file(args.config)

        # Then update with any command line arguments (highest precedence)
        arg_dict = vars(args)
        for key, value in arg_dict.items():
            if value is not None and key != "config":
                # Convert hyphenated args to underscored keys
                config_key = key.replace("-", "_")
                self._config[config_key] = value

    def load(self) -> BootstrapConfig:
        """Load configuration from all sources with precedence.

        Precedence order (highest to lowest):
        1. Command line arguments
        2. Environment variables
        3. Configuration file
        """
        # Load from lowest to highest precedence
        self.load_from_file("config.yaml")  # Default config file
        self.load_from_env()
        self.load_from_args()

        # Create and validate the bootstrap config
        bootstrap_config = BootstrapConfig.from_dict(self._config)

        if not bootstrap_config.validate():
            missing_fields = []
            if not bootstrap_config.elasticsearch_url:
                missing_fields.append("elasticsearch_url")
            if not bootstrap_config.elasticsearch_username:
                missing_fields.append("elasticsearch_username")
            if not bootstrap_config.elasticsearch_password:
                missing_fields.append("elasticsearch_password")
            if not bootstrap_config.config_index_name:
                missing_fields.append("config_index_name")

            raise ValueError(
                f"Missing required bootstrap configuration fields: {', '.join(missing_fields)}"
            )

        return bootstrap_config


def load_bootstrap_config() -> BootstrapConfig:
    """Load bootstrap configuration from all available sources."""
    config_loader = ConfigLoader()
    return config_loader.load()
