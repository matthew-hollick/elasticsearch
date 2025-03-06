#!/usr/bin/env python3
"""
Upload runtime configuration to Elasticsearch
This script uploads the runtime configuration to Elasticsearch
"""

import argparse
import json
import logging
import sys
import os
from datetime import datetime

from elasticsearch import Elasticsearch
from runtime_schema import RuntimeConfig

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)

logger = logging.getLogger(__name__)


def upload_config_to_elasticsearch(
    config_path, es_client, index_name=".hedgehog-snmp-runtime-config"
):
    """
    Upload the runtime configuration to Elasticsearch.

    Args:
        config_path: Path to the configuration file
        es_client: Elasticsearch client
        index_name: Index name for the runtime configuration

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Load and validate configuration
        with open(config_path, "r") as f:
            config_data = json.load(f)

        # Validate using Pydantic
        config = RuntimeConfig.parse_obj(config_data)
        logger.info(f"Loaded and validated configuration from {config_path}")

        # Create the index if it doesn't exist
        if not es_client.indices.exists(index=index_name):
            logger.info(f"Creating runtime configuration index {index_name}")
            es_client.indices.create(
                index=index_name,
                body={
                    "mappings": {
                        "properties": {
                            "@timestamp": {"type": "date"},
                            "config": {"type": "object", "enabled": True},
                            "version": {"type": "keyword"},
                            "description": {"type": "text"},
                        }
                    }
                },
            )

        # Prepare the document
        doc = {
            "@timestamp": datetime.now().isoformat(),
            "config": config_data,
            "version": config.version,
            "description": f"Runtime configuration uploaded at {datetime.now().isoformat()}",
        }

        # Index the document
        response = es_client.index(index=index_name, document=doc, refresh=True)

        logger.info(
            f"Successfully uploaded configuration to {index_name}, document ID: {response['_id']}"
        )
        return True

    except Exception as e:
        logger.error(f"Error uploading configuration to Elasticsearch: {e}")
        import traceback

        logger.error(traceback.format_exc())
        return False


def main():
    """Main function to upload the runtime configuration to Elasticsearch"""
    parser = argparse.ArgumentParser(
        description="Upload runtime configuration to Elasticsearch"
    )
    parser.add_argument(
        "-c", "--config", required=True, help="Path to the configuration file"
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
    parser.add_argument(
        "--index",
        default=".hedgehog-snmp-runtime-config",
        help="Index name for the runtime configuration",
    )

    args = parser.parse_args()

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

    # Upload configuration
    success = upload_config_to_elasticsearch(args.config, es_client, args.index)

    if success:
        logger.info("Configuration upload completed successfully")
        sys.exit(0)
    else:
        logger.error("Configuration upload failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
