#!/usr/bin/env python3
"""
Elasticsearch writer module for the SNMP Bridge.
This module provides functionality to write metrics to Elasticsearch.
"""

import logging
from typing import Dict, Any, List, Optional

from elasticsearch import Elasticsearch
from elasticsearch.exceptions import ApiError

from runtime_schema import RuntimeConfig, ECSFieldType

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def create_elasticsearch_client(config: RuntimeConfig) -> Optional[Elasticsearch]:
    """
    Create an Elasticsearch client using the configuration.
    Returns None if Elasticsearch is not configured.
    """
    if not config.global_ or not config.global_.elasticsearch:
        logger.warning("Elasticsearch not configured in runtime configuration")
        return None

    es_config = config.global_.elasticsearch

    # Set up authentication
    auth_config = es_config.auth

    # Set up TLS verification
    verify_certs = True
    ca_certs = None

    if es_config.tls:
        verify_certs = es_config.tls.verify
        if not verify_certs:
            logger.warning("TLS certificate verification is disabled for Elasticsearch")

        if es_config.tls.ca_cert:
            ca_certs = es_config.tls.ca_cert

    # Get hosts from config or use default
    hosts = getattr(es_config, "hosts", ["https://127.0.0.1:9200"])

    # Create client options based on authentication type
    if hasattr(auth_config, "username") and hasattr(auth_config, "password"):
        # Username/password authentication
        logger.info("Using username/password authentication for Elasticsearch")
        client = Elasticsearch(
            hosts=hosts,
            basic_auth=(auth_config.username, auth_config.password),
            verify_certs=verify_certs,
            ca_certs=ca_certs,
            ssl_show_warn=False,
        )
    elif hasattr(auth_config, "api_key"):
        # API key authentication
        logger.info("Using API key authentication for Elasticsearch")
        client = Elasticsearch(
            hosts=hosts,
            api_key=auth_config.api_key,
            verify_certs=verify_certs,
            ca_certs=ca_certs,
            ssl_show_warn=False,
        )
    else:
        logger.error("Unsupported authentication type for Elasticsearch")
        return None

    # Test the connection
    try:
        info = client.info()
        logger.info(f"Connected to Elasticsearch cluster: {info['cluster_name']}")
        return client
    except ApiError as e:
        logger.error(f"Failed to connect to Elasticsearch: {e}")
        return None


def get_ecs_value(metric_data: Dict[str, Any], ecs_mapping: Dict[str, Any]) -> Any:
    """
    Extract the appropriate value for ECS mapping based on the metric type.
    For string-like fields, use the label value if available.
    For numeric fields, use the metric value.
    """
    # Handle both dictionary and object access for type
    if isinstance(ecs_mapping, dict):
        field_type = ecs_mapping.get("type", "auto")
    else:
        field_type = getattr(ecs_mapping, "type", "auto")

    # For auto type, try to determine the appropriate type based on the value
    if field_type == "auto":
        # Check if the value is a string
        if isinstance(metric_data["value"], str):
            return metric_data["value"]

        # Check if the value is a boolean
        if isinstance(metric_data["value"], bool):
            return metric_data["value"]

        # Check if the value is an integer
        if isinstance(metric_data["value"], int):
            return metric_data["value"]

        # Default to float for numeric values
        return float(metric_data["value"])

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


def get_ecs_field_from_metric_name(metric_name: str) -> str:
    """
    Convert a metric name with underscores to dot notation for ECS mapping.
    Example: node_memory_MemFree_bytes -> node.memory.MemFree.bytes
    """
    return metric_name.replace("_", ".")


def set_nested_field(doc: Dict[str, Any], field_name: str, value: Any) -> None:
    """
    Set a nested field in the document.
    """
    field_parts = field_name.split(".")
    current = doc
    for i, part in enumerate(field_parts):
        if i == len(field_parts) - 1:
            current[part] = value
        else:
            if part not in current:
                current[part] = {}
            current = current[part]


def create_ecs_document(
    metric_data: Dict[str, Any],
    metric_config: Any,
    global_metadata: Dict[str, Any],
    target_metadata: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Create an ECS-compliant document from metric data.

    If the metric has an explicit ECS mapping in the configuration, use that.
    Otherwise, automatically convert the metric name to a field name using dots
    instead of underscores and detect the appropriate data type.
    """
    # Start with base document structure
    doc = {
        "@timestamp": metric_data["timestamp"],
        "event": {"dataset": "snmp", "module": "snmp", "kind": "metric"},
        "metricset": {
            "name": metric_config.name,
            "period": 60,  # Default period in seconds
        },
        "service": {"type": "snmp"},
        "labels": metric_data.get("labels", {}),
    }

    # Add global metadata
    if global_metadata:
        for key, value in global_metadata.items():
            doc[key] = value

    # Add target metadata
    if target_metadata:
        for key, value in target_metadata.items():
            doc[key] = value

    # Add metric value with ECS mapping if available
    if hasattr(metric_config, "ecs_mapping") and metric_config.ecs_mapping:
        # Use explicit mapping from configuration
        field_name = metric_config.ecs_mapping.field
        field_type = metric_config.ecs_mapping.type

        # Get the appropriate value based on the field type
        value = get_ecs_value(metric_data, metric_config.ecs_mapping)

        # Set the field in the document
        set_nested_field(doc, field_name, value)
    else:
        # Use automatic mapping - convert underscores to dots
        field_name = get_ecs_field_from_metric_name(metric_config.name)

        # Automatically detect the type and convert the value
        value = metric_data["value"]

        # Detect the type and convert if necessary
        if isinstance(value, bool):
            # Boolean value
            pass
        elif isinstance(value, int):
            # Integer value
            pass
        elif isinstance(value, float):
            # Float value
            pass
        elif isinstance(value, str):
            # Try to convert string to appropriate type
            if value.lower() in ["true", "false"]:
                value = value.lower() == "true"
            else:
                try:
                    # Try to convert to int or float
                    if "." in value:
                        value = float(value)
                    else:
                        value = int(value)
                except ValueError:
                    # Keep as string if conversion fails
                    pass

        # Set the field in the document
        set_nested_field(doc, field_name, value)

    return doc


def write_metrics_to_elasticsearch(
    es_client,
    metrics: Dict[str, List[Dict[str, Any]]],
    target_config: Any,
    global_metadata: Dict[str, Any],
) -> int:
    """
    Write metrics to Elasticsearch.

    This function will group all metrics by collection time and target,
    creating a single document with multiple metrics inside it.

    Returns the number of documents successfully indexed.
    """
    if not metrics:
        logger.warning("No metrics to write to Elasticsearch")
        return 0

    # Get target metadata
    target_metadata = target_config.metadata or {}

    # Get index name from target config or use default
    index_name = target_config.index or "hedgehog-snmp-metrics"

    # Create a mapping of configured metrics for quick lookup
    metric_configs_map = (
        {m.name: m for m in target_config.metrics} if target_config.metrics else {}
    )

    # Group metrics by timestamp (they should all have the same timestamp in a single scrape)
    # but we'll group just in case
    metrics_by_timestamp = {}

    # Process all metrics
    for metric_name, metric_data_list in metrics.items():
        for metric_data in metric_data_list:
            timestamp = metric_data["timestamp"]
            if timestamp not in metrics_by_timestamp:
                metrics_by_timestamp[timestamp] = []

            # Check if this metric is explicitly configured
            if metric_name in metric_configs_map:
                metric_config = metric_configs_map[metric_name]
                field_name = (
                    metric_config.ecs_mapping.field
                    if hasattr(metric_config, "ecs_mapping")
                    and metric_config.ecs_mapping
                    else get_ecs_field_from_metric_name(metric_name)
                )
            else:
                # Use automatic mapping for metrics not in the configuration
                field_name = get_ecs_field_from_metric_name(metric_name)

            # Get the value and convert if necessary
            value = metric_data["value"]

            # Detect the type and convert if necessary
            if isinstance(value, str):
                # Try to convert string to appropriate type
                if value.lower() in ["true", "false"]:
                    value = value.lower() == "true"
                else:
                    try:
                        # Try to convert to int or float
                        if "." in value:
                            value = float(value)
                        else:
                            value = int(value)
                    except ValueError:
                        # Keep as string if conversion fails
                        pass

            # Add to the metrics for this timestamp
            metrics_by_timestamp[timestamp].append(
                {
                    "name": metric_name,
                    "field": field_name,
                    "value": value,
                    "labels": metric_data.get("labels", {}),
                }
            )

    # Prepare documents for bulk indexing
    bulk_data = []
    doc_count = 0

    # Create one document per timestamp
    for timestamp, metrics_list in metrics_by_timestamp.items():
        # Create the base document
        doc = {
            "@timestamp": timestamp,
            "event": {"dataset": "snmp", "module": "snmp", "kind": "metric"},
            "service": {"type": "snmp"},
            "metrics": {},  # Will contain all metrics
            "labels": {},  # Will contain all labels
        }

        # Add global metadata
        if global_metadata:
            for key, value in global_metadata.items():
                doc[key] = value

        # Add target metadata
        if target_metadata:
            for key, value in target_metadata.items():
                doc[key] = value

        # Add all metrics to the document
        for metric in metrics_list:
            field_name = metric["field"]
            value = metric["value"]

            # Split the field path and create nested structure
            field_parts = field_name.split(".")
            current = doc["metrics"]
            for i, part in enumerate(field_parts):
                if i == len(field_parts) - 1:
                    current[part] = value
                else:
                    if part not in current:
                        current[part] = {}
                    current = current[part]

            # Add labels to the labels object instead of directly to the document
            for label_key, label_value in metric["labels"].items():
                if label_key not in doc["labels"]:
                    doc["labels"][label_key] = label_value

        # Add to bulk data
        bulk_data.append({"index": {"_index": index_name}})
        bulk_data.append(doc)
        doc_count += 1

    if not bulk_data:
        logger.warning("No documents to index")
        return 0

    try:
        # Perform bulk indexing
        response = es_client.bulk(operations=bulk_data, refresh=True)

        # Check for errors
        if response["errors"]:
            error_count = sum(
                1 for item in response["items"] if "error" in item["index"]
            )
            logger.error(
                f"Errors occurred during bulk indexing: {error_count} documents failed"
            )

            # Log the first few errors
            for i, item in enumerate(response["items"]):
                if "error" in item["index"] and i < 5:  # Only log the first 5 errors
                    logger.error(f"Error for document {i}: {item['index']['error']}")

            # Return the number of successful documents
            return doc_count - error_count
        else:
            logger.info(f"Successfully indexed {doc_count} documents")
            return doc_count
    except Exception as e:
        logger.error(f"Error writing to Elasticsearch: {e}")
        return 0
