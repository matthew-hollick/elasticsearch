"""Tests for the bootstrap configuration module."""

import os
import tempfile
from unittest.mock import patch

import pytest
import yaml
from snmp_bridge.config.bootstrap import BootstrapConfig
from snmp_bridge.config.bootstrap import ConfigLoader


def test_bootstrap_config_validation():
    """Test that BootstrapConfig validation works correctly."""
    # Valid config
    valid_config = BootstrapConfig(
        elasticsearch_url="https://elasticsearch.hedgehog.internal:9200",
        elasticsearch_username="hedgehog_admin",
        elasticsearch_password="password",
        config_index_name="snmp-bridge-config",
    )
    assert valid_config.validate() is True

    # Invalid config (missing URL)
    invalid_config = BootstrapConfig(
        elasticsearch_url="",
        elasticsearch_username="hedgehog_admin",
        elasticsearch_password="password",
        config_index_name="snmp-bridge-config",
    )
    assert invalid_config.validate() is False


def test_load_from_file():
    """Test loading configuration from a file."""
    config_loader = ConfigLoader()

    # Create a temporary config file
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".yaml", delete=False
    ) as temp_file:
        config_data = {
            "elasticsearch_url": "https://elasticsearch.hedgehog.internal:9200",
            "elasticsearch_username": "hedgehog_admin",
            "elasticsearch_password": "file_password",
            "config_index_name": "file-config-index",
        }
        yaml.dump(config_data, temp_file)

    try:
        # Load the config from the file
        config_loader.load_from_file(temp_file.name)

        # Check that the config was loaded correctly
        assert (
            config_loader._config["elasticsearch_url"]
            == "https://elasticsearch.hedgehog.internal:9200"
        )
        assert config_loader._config["elasticsearch_username"] == "hedgehog_admin"
        assert config_loader._config["elasticsearch_password"] == "file_password"
        assert config_loader._config["config_index_name"] == "file-config-index"
    finally:
        # Clean up the temporary file
        os.unlink(temp_file.name)


def test_load_from_env():
    """Test loading configuration from environment variables."""
    config_loader = ConfigLoader()

    # Set environment variables
    with patch.dict(
        os.environ,
        {
            "ELASTICSEARCH_URL": "https://env-elasticsearch.hedgehog.internal:9200",
            "ELASTICSEARCH_USERNAME": "env_hedgehog_admin",
            "ELASTICSEARCH_PASSWORD": "env_password",
            "CONFIG_INDEX_NAME": "env-config-index",
        },
    ):
        config_loader.load_from_env()

    # Check that the config was loaded correctly
    assert (
        config_loader._config["elasticsearch_url"]
        == "https://env-elasticsearch.hedgehog.internal:9200"
    )
    assert config_loader._config["elasticsearch_username"] == "env_hedgehog_admin"
    assert config_loader._config["elasticsearch_password"] == "env_password"
    assert config_loader._config["config_index_name"] == "env-config-index"


def test_load_from_args():
    """Test loading configuration from command line arguments."""
    config_loader = ConfigLoader()

    # Mock command line arguments
    test_args = [
        "--elasticsearch-url",
        "https://arg-elasticsearch.hedgehog.internal:9200",
        "--elasticsearch-username",
        "arg_hedgehog_admin",
        "--elasticsearch-password",
        "arg_password",
        "--config-index-name",
        "arg-config-index",
    ]

    with patch("sys.argv", ["program"] + test_args):
        config_loader.load_from_args()

    # Check that the config was loaded correctly
    assert (
        config_loader._config["elasticsearch_url"]
        == "https://arg-elasticsearch.hedgehog.internal:9200"
    )
    assert config_loader._config["elasticsearch_username"] == "arg_hedgehog_admin"
    assert config_loader._config["elasticsearch_password"] == "arg_password"
    assert config_loader._config["config_index_name"] == "arg-config-index"


def test_precedence():
    """Test that configuration sources have the correct precedence."""
    # Create a temporary config file
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".yaml", delete=False
    ) as temp_file:
        config_data = {
            "elasticsearch_url": "https://file-elasticsearch.hedgehog.internal:9200",
            "elasticsearch_username": "file_hedgehog_admin",
            "elasticsearch_password": "file_password",
            "config_index_name": "file-config-index",
        }
        yaml.dump(config_data, temp_file)

    try:
        # Set up environment variables and command line arguments
        env_vars = {
            "ELASTICSEARCH_URL": "https://env-elasticsearch.hedgehog.internal:9200",
            "ELASTICSEARCH_USERNAME": "env_hedgehog_admin",
            "ELASTICSEARCH_PASSWORD": "env_password",
            # No config_index_name in env to test fallback
        }

        test_args = [
            "--elasticsearch-url",
            "https://arg-elasticsearch.hedgehog.internal:9200",
            # No elasticsearch_username in args to test fallback
            "--elasticsearch-password",
            "arg_password",
            # No config_index_name in args to test fallback
        ]

        with patch.dict(os.environ, env_vars):
            with patch("sys.argv", ["program", "--config", temp_file.name] + test_args):
                config_loader = ConfigLoader()
                config_loader.load()

                # Check precedence:
                # 1. Command line args (highest)
                assert (
                    config_loader._config["elasticsearch_url"]
                    == "https://arg-elasticsearch.hedgehog.internal:9200"
                )
                assert config_loader._config["elasticsearch_password"] == "arg_password"

                # 2. Environment variables (middle)
                assert (
                    config_loader._config["elasticsearch_username"]
                    == "env_hedgehog_admin"
                )

                # 3. Config file (lowest)
                assert config_loader._config["config_index_name"] == "file-config-index"
    finally:
        # Clean up the temporary file
        os.unlink(temp_file.name)


def test_missing_required_fields():
    """Test that an error is raised when required fields are missing."""
    config_loader = ConfigLoader()

    # Set up partial configuration
    config_loader._config = {
        "elasticsearch_url": "https://elasticsearch.hedgehog.internal:9200",
        # Missing elasticsearch_username
        "elasticsearch_password": "password",
        # Missing config_index_name
    }

    # Check that validation fails
    with pytest.raises(ValueError) as excinfo:
        config_loader.load()

    # Check that the error message includes the missing fields
    assert "elasticsearch_username" in str(excinfo.value)
    assert "config_index_name" in str(excinfo.value)
