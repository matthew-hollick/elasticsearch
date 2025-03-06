#!/usr/bin/env python3
"""
Utility script to validate bootstrap configuration.

This script loads the bootstrap configuration using the BootstrapLoader
and displays the loaded configuration if valid.
"""

import argparse
import logging
import json
import sys
import os
from typing import Optional

from bootstrap_loader import load_bootstrap_config, ConfigurationError


def setup_logging(verbose: bool) -> None:
    """Configure logging based on verbosity level."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )


def main(config_file: Optional[str] = None, verbose: bool = False) -> int:
    """
    Main function to validate bootstrap configuration.

    Args:
        config_file: Optional path to configuration file
        verbose: Enable verbose logging

    Returns:
        Exit code (0 for success, non-zero for failure)
    """
    setup_logging(verbose)

    # Set environment variable if config_file is provided
    if config_file:
        import os

        os.environ["BRIDGE_CONFIG_FILE"] = config_file

    try:
        config = load_bootstrap_config()

        # Display the loaded configuration
        print("Bootstrap configuration loaded successfully!")
        print("\nConfiguration details:")
        print(f"Elasticsearch URL: {config.elasticsearch.url}")

        # Show authentication method
        if config.elasticsearch.auth:
            if hasattr(config.elasticsearch.auth, "username"):
                print(
                    f"Authentication: Username/Password ({config.elasticsearch.auth.username})"
                )
            elif hasattr(config.elasticsearch.auth, "api_key"):
                print("Authentication: API Key")
        else:
            print("Authentication: None")

        # Show TLS configuration
        if config.elasticsearch.tls:
            print(
                f"TLS Verification: {'Enabled' if config.elasticsearch.tls.verify else 'Disabled'}"
            )
            if config.elasticsearch.tls.ca_cert:
                print(f"CA Certificate: {config.elasticsearch.tls.ca_cert}")
            if config.elasticsearch.tls.client_cert:
                print(f"Client Certificate: {config.elasticsearch.tls.client_cert}")

        print(f"Config Index: {config.config_index}")

        # Show logging configuration
        if config.logging:
            print(f"Logging Level: {config.logging.level}")
            if config.logging.file:
                print(f"Log File: {config.logging.file}")
            else:
                print("Logging to: stdout")

        # Print the full configuration as JSON if verbose
        if verbose:
            print("\nFull configuration (JSON):")
            # Use model_dump instead of dict for Pydantic v2 compatibility
            config_dict = (
                config.model_dump() if hasattr(config, "model_dump") else config.dict()
            )

            # Convert any non-serializable objects to strings
            def json_serializable(obj):
                try:
                    json.dumps(obj)
                    return obj
                except (TypeError, OverflowError):
                    return str(obj)

            def make_serializable(d):
                if isinstance(d, dict):
                    return {k: make_serializable(v) for k, v in d.items()}
                elif isinstance(d, list):
                    return [make_serializable(i) for i in d]
                else:
                    return json_serializable(d)

            serializable_config = make_serializable(config_dict)
            print(json.dumps(serializable_config, indent=2))

        return 0

    except ConfigurationError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Validate bootstrap configuration")
    parser.add_argument("-c", "--config", help="Path to configuration file")
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Enable verbose output"
    )
    parser.add_argument(
        "-e",
        "--example",
        action="store_true",
        help="Use example configuration from examples directory",
    )

    args = parser.parse_args()

    config_path = args.config
    if args.example and not args.config:
        # Use example configuration if requested and no specific config provided
        script_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(
            script_dir, "examples", "bootstrap_config_example.yaml"
        )
        print(f"Using example configuration: {config_path}")

    sys.exit(main(config_path, args.verbose))
