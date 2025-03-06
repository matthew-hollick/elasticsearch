#!/usr/bin/env python3
"""
Test script to fetch metrics from an SNMP exporter using our runtime configuration.
This script demonstrates how the bridge will connect to exporters and collect metrics.
"""

import argparse
import json
import logging
import sys
import urllib.parse
from datetime import datetime, UTC
from typing import Dict, Any, List

import requests
from pydantic import ValidationError
from prometheus_client.parser import text_string_to_metric_families

from runtime_schema import RuntimeConfig, TargetConfig, ECSFieldType

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def load_config(config_file: str) -> RuntimeConfig:
    """Load and validate the runtime configuration."""
    logger.info(f"Loading configuration from {config_file}")
    with open(config_file, "r") as f:
        config_data = json.load(f)

    try:
        config = RuntimeConfig(**config_data)
        logger.info("Configuration validated successfully")
        return config
    except ValidationError as e:
        logger.error(f"Configuration validation error: {e}")
        sys.exit(1)


def build_exporter_url(exporter_url: str, target_config: TargetConfig) -> str:
    """Build the URL for the exporter with parameters."""
    # Check if we have the new format with module, target and auth directly in the target config
    params = {}

    # Add module if specified
    if hasattr(target_config, "module"):
        params["module"] = target_config.module

    # Add target if specified
    if hasattr(target_config, "target"):
        params["target"] = target_config.target

    # Add auth if specified
    if hasattr(target_config, "auth"):
        params["auth"] = target_config.auth

    # Fall back to the old format with params dictionary if no direct attributes
    if not params and hasattr(target_config, "params"):
        params = target_config.params or {}

    # Build the URL with parameters
    query_params = urllib.parse.urlencode(params)
    return f"{exporter_url}/snmp?{query_params}"


def fetch_metrics(config: RuntimeConfig, target_name: str) -> Dict[str, Any]:
    """Fetch metrics from the specified target."""
    if target_name not in config.targets:
        logger.error(f"Target '{target_name}' not found in configuration")
        sys.exit(1)

    target_config = config.targets[target_name]
    exporter_name = target_config.exporter

    if exporter_name not in config.exporters:
        logger.error(f"Exporter '{exporter_name}' not found in configuration")
        sys.exit(1)

    exporter_config = config.exporters[exporter_name]

    # Use target-specific exporter_url if available, otherwise use the exporter's default URL
    if hasattr(target_config, "exporter_url") and target_config.exporter_url:
        exporter_url = str(target_config.exporter_url).rstrip("/")
        logger.info(f"Using target-specific exporter URL: {exporter_url}")
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
            logger.info(f"Using basic authentication for exporter {exporter_name}")
        elif hasattr(auth_config, "bearer_token"):
            # Bearer token authentication
            headers["Authorization"] = f"Bearer {auth_config.bearer_token}"
            logger.info(
                f"Using bearer token authentication for exporter {exporter_name}"
            )
        elif hasattr(auth_config, "api_key"):
            # API key authentication
            headers["Authorization"] = f"ApiKey {auth_config.api_key}"
            logger.info(f"Using API key authentication for exporter {exporter_name}")

    # Set up TLS/SSL verification if configured
    verify = True
    cert = None
    if exporter_config.tls:
        verify = exporter_config.tls.verify
        if not verify:
            logger.warning(
                f"TLS certificate verification is disabled for exporter {exporter_name}"
            )

        if exporter_config.tls.ca_cert:
            verify = exporter_config.tls.ca_cert

        if exporter_config.tls.client_cert and exporter_config.tls.client_key:
            cert = (exporter_config.tls.client_cert, exporter_config.tls.client_key)

    try:
        response = requests.get(
            url, headers=headers, timeout=timeout, auth=auth, verify=verify, cert=cert
        )
        response.raise_for_status()

        # Process the response using the official Prometheus parser
        metrics = parse_prometheus_metrics(response.text, target_config.metrics)
        return metrics
    except requests.RequestException as e:
        logger.error(f"Error fetching metrics: {e}")
        sys.exit(1)


def parse_prometheus_metrics(content: str, metric_configs: List) -> Dict[str, Any]:
    """
    Parse Prometheus metrics from the response content using the official parser.

    This uses the prometheus_client.parser module which is the official way to parse
    Prometheus exposition format as recommended by Brian Brazil.

    Collects all metrics from the exporter, not just those defined in the configuration.
    """
    metrics = {}
    # Create a set of configured metric names for quick lookup
    configured_metrics = {m.name for m in metric_configs} if metric_configs else set()
    timestamp = datetime.now(UTC).isoformat()

    try:
        # Use the official Prometheus parser
        for family in text_string_to_metric_families(content):
            # Process all metrics, not just those in our configuration
            if family.name not in metrics:
                metrics[family.name] = []

            for sample in family.samples:
                # The sample object has name, labels, value, and timestamp attributes
                # Access them directly instead of unpacking
                metrics[family.name].append(
                    {
                        "name": sample.name,
                        "labels": sample.labels,
                        "value": sample.value,
                        "timestamp": timestamp,
                        # Flag if this metric is explicitly configured
                        "is_configured": family.name in configured_metrics,
                    }
                )

        return metrics
    except Exception as e:
        logger.error(f"Error parsing Prometheus metrics: {e}")
        return {}


def format_metrics_for_display(metrics: Dict[str, Any]) -> str:
    """Format metrics for display."""
    output = []

    output.append("Collected Metrics:")
    output.append("=================")

    for metric_name, metric_data in metrics.items():
        output.append(f"\nMetric: {metric_name}")
        output.append("-" * (len(metric_name) + 8))

        for data_point in metric_data:
            labels_str = ", ".join(
                [f"{k}={v}" for k, v in data_point.get("labels", {}).items()]
            )
            if labels_str:
                output.append(f"  Labels: {labels_str}")
            output.append(f"  Value: {data_point['value']}")
            output.append(f"  Timestamp: {data_point['timestamp']}")
            output.append("")

    return "\n".join(output)


def get_ecs_value(metric_data: Dict[str, Any], ecs_mapping: Dict[str, Any]) -> Any:
    """
    Extract the appropriate value for ECS mapping based on the metric type.
    For string-like fields, use the label value if available.
    For numeric fields, use the metric value.
    """
    field_type = ecs_mapping.type

    # For string-like fields, prefer the label value if it exists
    if field_type in [ECSFieldType.KEYWORD, ECSFieldType.TEXT]:
        # Check if there's a label with the same name as the metric
        metric_name = metric_data["name"].split("_")[
            0
        ]  # Get base name without suffixes
        if metric_name in metric_data["labels"]:
            return metric_data["labels"][metric_name]

    # For all other cases, use the numeric value
    return metric_data["value"]


def get_elasticsearch_credentials(config: RuntimeConfig) -> Dict[str, Any]:
    """Extract Elasticsearch credentials from the runtime configuration."""
    if not config.global_ or not config.global_.elasticsearch:
        return {
            "status": "Not configured",
            "message": "No Elasticsearch credentials found in runtime configuration",
        }

    es_config = config.global_.elasticsearch
    auth_type = (
        "Username/Password" if hasattr(es_config.auth, "username") else "API Key"
    )

    # Don't expose the actual credentials in the output
    if auth_type == "Username/Password":
        return {
            "status": "Configured",
            "auth_type": auth_type,
            "username": es_config.auth.username,
            "tls_verify": es_config.tls.verify if es_config.tls else True,
        }
    else:
        return {
            "status": "Configured",
            "auth_type": auth_type,
            "tls_verify": es_config.tls.verify if es_config.tls else True,
        }


def main():
    parser = argparse.ArgumentParser(description="Test SNMP metrics collection")
    parser.add_argument(
        "-c",
        "--config",
        default="examples/test_snmp_config.json",
        help="Path to the runtime configuration file",
    )
    parser.add_argument(
        "-t",
        "--target",
        default="local_snmp_device",
        help="Name of the target to fetch metrics from",
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Enable verbose logging"
    )
    args = parser.parse_args()

    if args.verbose:
        logger.setLevel(logging.DEBUG)

    config = load_config(args.config)

    # Display Elasticsearch credentials information
    es_creds = get_elasticsearch_credentials(config)
    print("\nElasticsearch Credentials:")
    print("=========================")
    for key, value in es_creds.items():
        print(f"{key}: {value}")
    print()

    metrics = fetch_metrics(config, args.target)

    print(format_metrics_for_display(metrics))

    # Show how these metrics would be mapped to ECS fields
    print("\nECS Mapping:")
    print("===========")

    target_config = config.targets[args.target]
    for metric_config in target_config.metrics:
        if metric_config.name in metrics and metric_config.ecs_mapping:
            print(f"\nMetric: {metric_config.name}")
            print(f"ECS Field: {metric_config.ecs_mapping.field}")
            print(f"ECS Type: {metric_config.ecs_mapping.type}")

            # Show example of how data would be mapped
            if metrics[metric_config.name]:
                example = metrics[metric_config.name][0]
                ecs_value = get_ecs_value(example, metric_config.ecs_mapping)
                print(f"Example Value: {ecs_value}")
                print("Example ECS Document:")

                ecs_doc = {
                    "@timestamp": example["timestamp"],
                    metric_config.ecs_mapping.field: ecs_value,
                    "labels": example.get("labels", {}),
                    "metric": {"name": metric_config.name},
                }

                print(json.dumps(ecs_doc, indent=2))


if __name__ == "__main__":
    main()
