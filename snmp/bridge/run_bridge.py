#!/usr/bin/env python3
"""
Continuous runner for the SNMP Bridge
This script fetches metrics from SNMP exporters and writes them to Elasticsearch
"""

import time
import logging
import sys
import json
import os
from datetime import datetime

from test_snmp_fetch import fetch_metrics
from elasticsearch import Elasticsearch
from elasticsearch_writer import write_metrics_to_elasticsearch
from runtime_schema import RuntimeConfig

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)

logger = logging.getLogger(__name__)


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
    """Main function to run the SNMP Bridge continuously"""
    # Bootstrap with initial configuration
    logger.info("Starting SNMP Bridge")

    # Try to get configuration from environment variables
    bootstrap_es_host = os.environ.get("ELASTICSEARCH_HOST", "https://127.0.0.1:9200")
    bootstrap_es_user = os.environ.get("ELASTICSEARCH_USERNAME", "hedgehog_snmp_bridge")
    bootstrap_es_pass = os.environ.get("ELASTICSEARCH_PASSWORD", "snmp_secure_password")
    bootstrap_es_verify = (
        os.environ.get("ELASTICSEARCH_VERIFY_CERTS", "false").lower() == "true"
    )

    # Create bootstrap Elasticsearch client
    bootstrap_es_client = Elasticsearch(
        bootstrap_es_host,
        basic_auth=(bootstrap_es_user, bootstrap_es_pass),
        verify_certs=bootstrap_es_verify,
        ssl_show_warn=False,
    )

    # Test connection
    try:
        info = bootstrap_es_client.info()
        logger.info(f"Connected to Elasticsearch cluster: {info['cluster_name']}")
    except Exception as e:
        logger.error(f"Failed to connect to Elasticsearch: {str(e)}")
        sys.exit(1)

    # Load runtime configuration from Elasticsearch
    config = load_runtime_config_from_elasticsearch(bootstrap_es_client)

    # Fall back to local configuration if needed
    if config is None:
        logger.warning("Falling back to local configuration file")
        config_path = os.environ.get(
            "CONFIG_PATH", "examples/runtime_config_example.json"
        )

        try:
            with open(config_path, "r") as f:
                config_data = json.load(f)

            config = RuntimeConfig.parse_obj(config_data)
            logger.info(f"Loaded configuration from {config_path}")
        except Exception as e:
            logger.error(f"Failed to load local configuration: {str(e)}")
            sys.exit(1)

    # Create Elasticsearch client using the runtime configuration
    if config.global_ and config.global_.elasticsearch:
        es_client = Elasticsearch(
            bootstrap_es_host,  # Use the bootstrap host
            basic_auth=(
                config.global_.elasticsearch.auth.username,
                config.global_.elasticsearch.auth.password,
            ),
            verify_certs=config.global_.elasticsearch.tls.verify
            if hasattr(config.global_.elasticsearch, "tls")
            else False,
            ssl_show_warn=False,
        )
    else:
        # Use the bootstrap client if no configuration is available
        logger.warning(
            "No Elasticsearch configuration in runtime config, using bootstrap client"
        )
        es_client = bootstrap_es_client

    # Get global metadata
    global_metadata = (
        config.global_.metadata if hasattr(config.global_, "metadata") else {}
    )

    # Run continuously
    try:
        while True:
            start_time = time.time()
            logger.info(
                f"Starting metrics collection cycle at {datetime.now().isoformat()}"
            )

            # Process each target
            for target_name in config.targets:
                target_start = time.time()
                logger.info(f"Processing target: {target_name}")

                try:
                    # Fetch metrics
                    metrics = fetch_metrics(config, target_name)

                    # Write metrics to Elasticsearch
                    if metrics:
                        target_config = config.targets[target_name]
                        docs_indexed = write_metrics_to_elasticsearch(
                            es_client, metrics, target_config, global_metadata
                        )
                        logger.info(
                            f"Successfully wrote {docs_indexed} metrics for {target_name}"
                        )
                    else:
                        logger.warning(f"No metrics fetched for {target_name}")

                except Exception as e:
                    logger.error(f"Error processing target {target_name}: {str(e)}")

                target_duration = time.time() - target_start
                logger.info(
                    f"Completed processing target {target_name} in {target_duration:.2f} seconds"
                )

            # Calculate cycle duration and sleep if needed
            cycle_duration = time.time() - start_time
            logger.info(
                f"Completed metrics collection cycle in {cycle_duration:.2f} seconds"
            )

            # Sleep until next collection cycle (default 60 seconds)
            collection_interval = getattr(config, "collection_interval", 60)
            sleep_time = max(0, collection_interval - cycle_duration)

            if sleep_time > 0:
                logger.info(
                    f"Sleeping for {sleep_time:.2f} seconds until next collection cycle"
                )
                time.sleep(sleep_time)
            else:
                logger.warning(
                    f"Collection cycle took longer than the interval ({cycle_duration:.2f} > {collection_interval})"
                )

            # Reload configuration from Elasticsearch periodically
            try:
                new_config = load_runtime_config_from_elasticsearch(bootstrap_es_client)
                if new_config:
                    config = new_config
                    logger.info(
                        "Successfully reloaded runtime configuration from Elasticsearch"
                    )
            except Exception as e:
                logger.error(f"Failed to reload runtime configuration: {str(e)}")

    except KeyboardInterrupt:
        logger.info("SNMP Bridge stopped by user")
    except Exception as e:
        logger.error(f"SNMP Bridge stopped due to error: {str(e)}")


if __name__ == "__main__":
    main()
