#!/usr/bin/env python3
"""
Script to compare metrics exposed by the Prometheus exporter with metrics written to Elasticsearch.
This helps verify that all metrics are being properly collected and stored.
"""

import argparse
import json
import logging
import os
import sys
from datetime import datetime, timedelta
from typing import Any, Set

import requests
from elasticsearch import Elasticsearch
from prometheus_client.parser import text_string_to_metric_families

from test_snmp_fetch import build_exporter_url
from runtime_schema import RuntimeConfig

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def get_metrics_from_exporter(config: Any, target_name: str) -> Set[str]:
    """
    Get the set of all metric names exposed by the exporter for a specific target.
    """
    target_config = config.targets[target_name]
    exporter_name = target_config.exporter
    exporter_config = config.exporters[exporter_name]

    # Use target-specific exporter_url if available, otherwise use the exporter's default URL
    if hasattr(target_config, "exporter_url") and target_config.exporter_url:
        exporter_url = str(target_config.exporter_url).rstrip("/")
    else:
        exporter_url = str(exporter_config.url).rstrip("/")

    url = build_exporter_url(exporter_url, target_config)
    logger.info(f"Fetching metrics from {url}")

    # Prepare request parameters
    headers = exporter_config.headers or {}
    timeout = target_config.timeout or exporter_config.timeout or config.global_.timeout

    # Set up authentication if configured
    auth = None
    if exporter_config.auth:
        auth_config = exporter_config.auth
        if hasattr(auth_config, "username") and hasattr(auth_config, "password"):
            # Basic authentication
            auth = (auth_config.username, auth_config.password)

    try:
        response = requests.get(
            url, headers=headers, timeout=timeout, auth=auth, verify=True
        )
        response.raise_for_status()

        # Parse metrics using the Prometheus parser
        metric_names = set()
        for family in text_string_to_metric_families(response.text):
            metric_names.add(family.name)

        return metric_names
    except requests.RequestException as e:
        logger.error(f"Error fetching metrics: {e}")
        return set()


def get_metrics_from_elasticsearch(
    es_client: Elasticsearch, index_name: str, target_name: str, time_range: int
) -> Set[str]:
    """
    Get the set of all metric names written to Elasticsearch for a specific target.
    """
    now = datetime.now()
    time_from = now - timedelta(minutes=time_range)

    # First check if the index exists
    try:
        index_exists = es_client.indices.exists(index=index_name)
        if not index_exists:
            logger.warning(f"Index {index_name} does not exist")
            return set()
    except Exception as e:
        logger.error(f"Error checking if index exists: {e}")
        return set()

    # Use a simple search to get all documents
    query = {
        "size": 100,  # Get up to 100 documents
        "query": {
            "bool": {
                "must": [
                    {
                        "range": {
                            "@timestamp": {
                                "gte": time_from.isoformat(),
                                "lte": now.isoformat(),
                            }
                        }
                    }
                ]
            }
        },
    }

    # Add target filter if provided
    if target_name:
        query["query"]["bool"]["must"].append({"term": {"labels.target": target_name}})

    try:
        response = es_client.search(index=index_name, body=query)
        logger.info(f"Got {len(response['hits']['hits'])} hits from Elasticsearch")

        if len(response["hits"]["hits"]) == 0:
            logger.warning(
                "No documents found in Elasticsearch. Check your time range and target filter."
            )
            return set()

        # Log the first document for debugging
        if response["hits"]["hits"]:
            logger.info(
                f"First document: {json.dumps(response['hits']['hits'][0]['_source'], indent=2)}"
            )

        metric_names = set()

        # Extract metric names from the hits
        for hit in response.get("hits", {}).get("hits", []):
            source = hit.get("_source", {})

            logger.info(f"Processing document with keys: {list(source.keys())}")

            if "metrics" in source:
                logger.info(f"Metrics keys: {list(source['metrics'].keys())}")

                # Extract metric names from the metrics object
                # We need to recursively traverse the metrics object to find all metrics
                def extract_metric_names(obj, prefix=""):
                    if not isinstance(obj, dict):
                        logger.debug(f"Not a dict: {obj}")
                        return

                    logger.debug(
                        f"Processing object with prefix '{prefix}': {list(obj.keys())}"
                    )

                    for key, value in obj.items():
                        if isinstance(value, dict):
                            # Recurse into nested objects
                            logger.debug(
                                f"Recursing into {key} with prefix {prefix}{key}_"
                            )
                            extract_metric_names(value, f"{prefix}{key}_")
                        else:
                            # This is a leaf node, so it's a metric
                            if prefix:
                                # This is a nested metric, reconstruct the original name
                                # e.g., "snmp_scrape_duration_seconds"
                                metric_name = f"{prefix}{key}"
                            else:
                                # This is a top-level metric
                                metric_name = key

                            logger.debug(f"Found metric: {metric_name} = {value}")
                            metric_names.add(metric_name)

                # First handle top-level metrics
                for key in source["metrics"]:
                    if not isinstance(source["metrics"][key], dict):
                        logger.info(f"Found top-level metric: {key}")
                        metric_names.add(key)

                # Then handle nested metrics like snmp.scrape.duration.seconds
                for key, value in source["metrics"].items():
                    if isinstance(value, dict):
                        logger.info(f"Processing nested metric: {key}")
                        extract_metric_names(value, f"{key}_")

        logger.info(f"Found metrics in Elasticsearch: {sorted(metric_names)}")
        return metric_names
    except Exception as e:
        logger.error(f"Error querying Elasticsearch: {e}")
        import traceback

        logger.error(traceback.format_exc())
        return set()


def load_runtime_config_from_elasticsearch(
    es_client, index_name=".hedgehog-snmp-runtime-config"
):
    """
    Load the runtime configuration from Elasticsearch.

    Returns:
        RuntimeConfig: The runtime configuration
    """
    try:
        # Check if the index exists
        if not es_client.indices.exists(index=index_name):
            logger.error(f"Runtime configuration index {index_name} does not exist")
            return None

        # Get the latest configuration
        response = es_client.search(
            index=index_name,
            body={"size": 1, "sort": [{"@timestamp": {"order": "desc"}}]},
        )

        if not response["hits"]["hits"]:
            logger.error("No runtime configuration found in Elasticsearch")
            return None

        config_doc = response["hits"]["hits"][0]["_source"]

        if "config" not in config_doc:
            logger.error(
                "Invalid runtime configuration document: missing 'config' field"
            )
            return None

        # Parse the configuration
        config = RuntimeConfig.parse_obj(config_doc["config"])
        logger.info(
            f"Loaded runtime configuration version {config.version} from Elasticsearch"
        )
        return config

    except Exception as e:
        logger.error(f"Error loading runtime configuration from Elasticsearch: {e}")
        return None


def main():
    parser = argparse.ArgumentParser(
        description="Compare metrics from exporter and Elasticsearch"
    )
    parser.add_argument(
        "-t",
        "--target",
        required=True,
        help="Name of the target to compare metrics for",
    )
    parser.add_argument(
        "-m",
        "--minutes",
        type=int,
        default=60,
        help="Time range in minutes to search for metrics in Elasticsearch",
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Enable verbose logging"
    )
    parser.add_argument(
        "--host",
        default=os.environ.get("ELASTICSEARCH_HOST", "https://127.0.0.1:9200"),
        help="Elasticsearch host",
    )
    parser.add_argument(
        "--username",
        default=os.environ.get("ELASTICSEARCH_USERNAME", "hedgehog_snmp_bridge"),
        help="Elasticsearch username",
    )
    parser.add_argument(
        "--password",
        default=os.environ.get("ELASTICSEARCH_PASSWORD", "snmp_secure_password"),
        help="Elasticsearch password",
    )
    parser.add_argument(
        "--verify-certs", action="store_true", help="Verify TLS certificates"
    )

    args = parser.parse_args()

    if args.verbose:
        logger.setLevel(logging.DEBUG)

    # Create Elasticsearch client
    es_client = Elasticsearch(
        args.host,
        basic_auth=(args.username, args.password),
        verify_certs=args.verify_certs,
        ssl_show_warn=False,
    )

    # Test connection
    try:
        info = es_client.info()
        logger.info(f"Connected to Elasticsearch cluster: {info['cluster_name']}")
    except Exception as e:
        logger.error(f"Failed to connect to Elasticsearch: {str(e)}")
        sys.exit(1)

    # Load runtime configuration from Elasticsearch
    config = load_runtime_config_from_elasticsearch(es_client)
    if not config:
        logger.error("Failed to load runtime configuration from Elasticsearch")
        sys.exit(1)

    # Get target configuration
    if args.target not in config.targets:
        logger.error(f"Target '{args.target}' not found in configuration")
        sys.exit(1)

    target_config = config.targets[args.target]
    index_name = target_config.index or "hedgehog-snmp-metrics"

    # Get metrics from exporter
    exporter_metrics = get_metrics_from_exporter(config, args.target)
    logger.info(f"Found {len(exporter_metrics)} metrics from exporter")

    # Get metrics from Elasticsearch
    es_metrics = get_metrics_from_elasticsearch(
        es_client, index_name, args.target, args.minutes
    )
    logger.info(f"Found {len(es_metrics)} metrics in Elasticsearch")

    # Compare metrics
    missing_metrics = exporter_metrics - es_metrics
    extra_metrics = es_metrics - exporter_metrics

    print("\nMetrics Comparison:")
    print("===================")
    print(f"Exporter metrics: {len(exporter_metrics)}")
    print(f"Elasticsearch metrics: {len(es_metrics)}")
    print(
        f"Missing metrics (in exporter but not in Elasticsearch): {len(missing_metrics)}"
    )
    print(f"Extra metrics (in Elasticsearch but not in exporter): {len(extra_metrics)}")

    if missing_metrics:
        print("\nMissing Metrics:")
        for metric in sorted(missing_metrics):
            print(f"  - {metric}")

    if extra_metrics:
        print("\nExtra Metrics:")
        for metric in sorted(extra_metrics):
            print(f"  - {metric}")

    # Print configured metrics
    configured_metrics = (
        {m.name for m in target_config.metrics} if target_config.metrics else set()
    )
    print(f"\nConfigured metrics: {len(configured_metrics)}")
    if configured_metrics:
        for metric in sorted(configured_metrics):
            print(f"  - {metric}")

    # Summary
    if len(exporter_metrics) == len(es_metrics):
        print("\nSUCCESS: All exporter metrics are being written to Elasticsearch!")
    else:
        print("\nWARNING: Not all exporter metrics are being written to Elasticsearch.")
        print("Check the missing metrics list and verify your configuration.")


if __name__ == "__main__":
    main()
