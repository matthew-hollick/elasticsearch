#!/usr/bin/env python3
"""
Test script for Elasticsearch writer functionality.
"""

import argparse
import json
import logging
import sys


from elasticsearch_writer import (
    create_elasticsearch_client,
    write_metrics_to_elasticsearch,
)
from test_snmp_fetch import fetch_metrics, load_config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)

logger = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Test Elasticsearch writer")
    parser.add_argument(
        "--config",
        default="examples/runtime_config_example.json",
        help="Path to runtime configuration file",
    )
    parser.add_argument(
        "--target", default="network_devices", help="Target name to fetch metrics from"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Fetch metrics but do not write to Elasticsearch",
    )
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")

    return parser.parse_args()


def main() -> None:
    """Main function."""
    args = parse_args()

    # Set log level based on verbosity
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Load configuration
    config = load_config(args.config)

    # Fetch metrics
    logger.info(f"Fetching metrics from target: {args.target}")
    metrics = fetch_metrics(config, args.target)

    # Print fetched metrics
    logger.info(f"Fetched metrics: {json.dumps(metrics, indent=2)}")

    # Check if dry run
    if args.dry_run:
        logger.info("Dry run mode enabled, not writing to Elasticsearch")
        return

    # Create Elasticsearch client
    client = create_elasticsearch_client(config)
    if not client:
        logger.error("Failed to create Elasticsearch client")
        sys.exit(1)

    # Write metrics to Elasticsearch
    result = write_metrics_to_elasticsearch(client, metrics, config, args.target)

    # Print result
    if result.get("failed", 0) > 0:
        logger.error(f"Failed to write {result['failed']} metrics to Elasticsearch")
        if "errors" in result and result["errors"]:
            logger.error(f"Errors: {json.dumps(result['errors'], indent=2)}")
        sys.exit(1)
    else:
        logger.info(f"Successfully wrote {result['success']} metrics to Elasticsearch")


if __name__ == "__main__":
    main()
