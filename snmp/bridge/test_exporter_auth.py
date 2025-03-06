#!/usr/bin/env python3
"""
Test script for verifying exporter authentication in the SNMP Bridge.
This script tests various authentication methods and error handling.
"""

import unittest
import requests
import json
import os
from unittest.mock import patch

# Import the fetch_metrics function from test_snmp_fetch.py
from test_snmp_fetch import fetch_metrics, RuntimeConfig


class MockResponse:
    """Mock response object for testing."""

    def __init__(
        self, text: str = "", status_code: int = 200, raise_error: bool = False
    ):
        self.text = text
        self.status_code = status_code
        self.raise_error = raise_error

    def raise_for_status(self):
        if self.raise_error:
            raise requests.exceptions.HTTPError(f"HTTP Error: {self.status_code}")


class TestExporterAuthentication(unittest.TestCase):
    """Test cases for exporter authentication."""

    def setUp(self):
        """Set up test fixtures."""
        # Load example runtime configuration
        example_config_path = os.path.join(
            os.path.dirname(__file__), "examples", "runtime_config_example.json"
        )
        with open(example_config_path, "r") as f:
            self.config_data = json.load(f)

        # Create a RuntimeConfig instance
        self.config = RuntimeConfig.model_validate(self.config_data)

        # Patch sys.exit to prevent tests from exiting
        self.exit_patcher = patch("sys.exit")
        self.mock_exit = self.exit_patcher.start()

    def tearDown(self):
        """Clean up after tests."""
        self.exit_patcher.stop()

    @patch("test_snmp_fetch.requests.get")
    def test_basic_auth(self, mock_get):
        """Test basic authentication."""
        # Set up mock response
        mock_response = MockResponse(
            text="# HELP test_metric Test metric\n# TYPE test_metric gauge\ntest_metric 1.0\n"
        )
        mock_get.return_value = mock_response

        # Call fetch_metrics
        fetch_metrics(self.config, "network_devices")

        # Check that requests.get was called with the correct auth
        args, kwargs = mock_get.call_args
        self.assertIn("auth", kwargs)
        self.assertEqual(kwargs["auth"], ("hedgehog_exporter_user", "password"))

    @patch("test_snmp_fetch.requests.get")
    def test_bearer_token_auth(self, mock_get):
        """Test bearer token authentication."""
        # Set up mock response
        mock_response = MockResponse(
            text="# HELP test_metric Test metric\n# TYPE test_metric gauge\ntest_metric 1.0\n"
        )
        mock_get.return_value = mock_response

        # Create a new auth config with bearer token
        self.config_data["exporters"]["snmp_exporter"]["auth"] = {
            "bearer_token": "test_token"
        }
        self.config = RuntimeConfig.model_validate(self.config_data)

        # Call fetch_metrics
        fetch_metrics(self.config, "network_devices")

        # Check that requests.get was called with the correct headers
        args, kwargs = mock_get.call_args
        self.assertIn("headers", kwargs)
        self.assertIn("Authorization", kwargs["headers"])
        self.assertEqual(kwargs["headers"]["Authorization"], "Bearer test_token")

    @patch("test_snmp_fetch.requests.get")
    def test_api_key_auth(self, mock_get):
        """Test API key authentication."""
        # Set up mock response
        mock_response = MockResponse(
            text="# HELP test_metric Test metric\n# TYPE test_metric gauge\ntest_metric 1.0\n"
        )
        mock_get.return_value = mock_response

        # Create a new auth config with API key
        self.config_data["exporters"]["snmp_exporter"]["auth"] = {
            "api_key": "test_api_key"
        }
        self.config = RuntimeConfig.model_validate(self.config_data)

        # Call fetch_metrics
        fetch_metrics(self.config, "network_devices")

        # Check that requests.get was called with the correct headers
        args, kwargs = mock_get.call_args
        self.assertIn("headers", kwargs)
        self.assertIn("Authorization", kwargs["headers"])
        self.assertEqual(kwargs["headers"]["Authorization"], "ApiKey test_api_key")

    @patch("test_snmp_fetch.requests.get")
    def test_auth_failure(self, mock_get):
        """Test handling of authentication failures."""
        # Set up mock response for auth failure
        mock_get.side_effect = requests.exceptions.HTTPError("HTTP Error: 401")

        # Call fetch_metrics and expect sys.exit to be called
        fetch_metrics(self.config, "network_devices")

        # Check that sys.exit was called with the correct code
        self.mock_exit.assert_called_once_with(1)

    @patch("test_snmp_fetch.requests.get")
    def test_tls_verification(self, mock_get):
        """Test TLS verification settings."""
        # Set up mock response
        mock_response = MockResponse(
            text="# HELP test_metric Test metric\n# TYPE test_metric gauge\ntest_metric 1.0\n"
        )
        mock_get.return_value = mock_response

        # Call fetch_metrics
        fetch_metrics(self.config, "network_devices")

        # Check that requests.get was called with verify=True and the CA cert path
        args, kwargs = mock_get.call_args
        self.assertIn("verify", kwargs)
        self.assertEqual(kwargs["verify"], "/etc/ssl/certs/ca-certificates.crt")

        # Create a new TLS config with verify=False
        self.config_data["exporters"]["snmp_exporter"]["tls"] = {"verify": False}
        self.config = RuntimeConfig.model_validate(self.config_data)

        # Call fetch_metrics again
        fetch_metrics(self.config, "network_devices")

        # Check that requests.get was called with verify=False
        args, kwargs = mock_get.call_args
        self.assertIn("verify", kwargs)
        self.assertEqual(kwargs["verify"], False)


if __name__ == "__main__":
    unittest.main()
