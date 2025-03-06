#!/usr/bin/env python3
"""
Main entry point for the Prometheus Bridge application.

This application loads bootstrap configuration, connects to Elasticsearch,
retrieves runtime configuration, and starts the bridge service.
"""

import argparse
import logging
import sys
import os
from typing import Optional

from bootstrap_loader import load_bootstrap_config, ConfigurationError


def setup_logging(config) -> None:
    """
    Configure logging based on the bootstrap configuration.

    Args:
        config: Bootstrap configuration object
    """
    log_level = logging.INFO
    log_file = None

    if config.logging:
        log_level = getattr(logging, config.logging.level)
        log_file = config.logging.file

    logging_config = {
        "level": log_level,
        "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    }

    if log_file:
        logging_config["filename"] = log_file

    logging.basicConfig(**logging_config)


def main(config_file: Optional[str] = None) -> int:
    """
    Main function to start the Prometheus Bridge application.

    Args:
        config_file: Optional path to configuration file

    Returns:
        Exit code (0 for success, non-zero for failure)
    """
    # Set environment variable if config_file is provided
    if config_file:
        import os

        os.environ["BRIDGE_CONFIG_FILE"] = config_file

    try:
        # Load bootstrap configuration
        config = load_bootstrap_config()

        # Setup logging
        setup_logging(config)

        logger = logging.getLogger(__name__)
        logger.info("Starting Prometheus Bridge application")
        logger.info(f"Connecting to Elasticsearch at {config.elasticsearch.url}")

        # TODO: Connect to Elasticsearch
        # TODO: Load runtime configuration from config_index
        # TODO: Validate runtime configuration
        # TODO: Start the bridge service

        logger.info("Prometheus Bridge application started successfully")

        # TODO: Implement main application loop

        return 0

    except ConfigurationError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Start the Prometheus Bridge application"
    )
    parser.add_argument("-c", "--config", help="Path to configuration file")
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

    sys.exit(main(config_path))
