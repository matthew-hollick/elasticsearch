"""Main entry point for the SNMP-Bridge application."""

import logging
import sys

from snmp_bridge.config.bootstrap import load_bootstrap_config


def setup_logging():
    """Set up logging configuration."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )


def main():
    """Run the SNMP-Bridge application."""
    setup_logging()
    logger = logging.getLogger("snmp_bridge")

    try:
        logger.info("Loading bootstrap configuration...")
        bootstrap_config = load_bootstrap_config()
        logger.info(
            f"Successfully loaded bootstrap configuration. "
            f"Using Elasticsearch at {bootstrap_config.elasticsearch_url} "
            f"and config index {bootstrap_config.config_index_name}"
        )

        # TODO: Initialize Elasticsearch connection
        # TODO: Load runtime configuration
        # TODO: Start supervisor process

    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        sys.exit(1)
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
