#!/usr/bin/env python3
"""
Utility script to validate runtime configuration.

This script loads a runtime configuration file and validates it against the schema.
"""

import argparse
import json
import logging
import sys
import os
import yaml
from pathlib import Path
from typing import Dict, Any

from runtime_schema import RuntimeConfig
from pydantic import ValidationError


def setup_logging(verbose: bool) -> None:
    """Configure logging based on verbosity level."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )


def load_config_file(file_path: str) -> Dict[str, Any]:
    """
    Load configuration from a YAML or JSON file.

    Args:
        file_path: Path to the configuration file

    Returns:
        Dict containing the configuration

    Raises:
        ValueError: If the file cannot be loaded or parsed
    """
    path = Path(file_path)
    if not path.exists():
        raise ValueError(f"Configuration file not found: {file_path}")

    with open(path, "r") as f:
        if path.suffix.lower() in [".yaml", ".yml"]:
            return yaml.safe_load(f)
        elif path.suffix.lower() == ".json":
            return json.load(f)
        else:
            raise ValueError(f"Unsupported file format: {path.suffix}")


def main(
    config_file: str, verbose: bool = False, show_bad_example: bool = False
) -> int:
    """
    Main function to validate runtime configuration.

    Args:
        config_file: Path to configuration file
        verbose: Enable verbose logging
        show_bad_example: Show validation errors for a bad example

    Returns:
        Exit code (0 for success, non-zero for failure)
    """
    setup_logging(verbose)
    logger = logging.getLogger(__name__)

    try:
        # Load configuration from file
        logger.info(f"Loading configuration from {config_file}")
        config_data = load_config_file(config_file)

        # Validate configuration against schema
        logger.info("Validating configuration against schema")
        config = RuntimeConfig(**config_data)

        # Display the loaded configuration
        print("Runtime configuration loaded successfully!")
        print("\nConfiguration details:")
        print(f"Version: {config.version}")
        print(f"Number of exporters: {len(config.exporters)}")
        print(f"Number of targets: {len(config.targets)}")

        # Show exporters
        print("\nExporters:")
        for name, exporter in config.exporters.items():
            print(f"  - {name}: {exporter.type} ({exporter.url})")

        # Show targets
        print("\nTargets:")
        for name, target in config.targets.items():
            print(f"  - {name}: using {target.exporter}, interval {target.interval}s")
            print(f"    Metrics: {len(target.metrics)}")
            print(f"    Index: {target.index}")

        # Show global settings
        if config.global_:
            print("\nGlobal settings:")
            print(f"  Timeout: {config.global_.timeout}s")
            print(f"  Retries: {config.global_.retries}")
            print(f"  Concurrency: {config.global_.concurrency}")

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

    except ValidationError as e:
        if show_bad_example:
            print(
                "Configuration validation error (expected for bad example):",
                file=sys.stderr,
            )
        else:
            print("Configuration validation error:", file=sys.stderr)

        for error in e.errors():
            location = " -> ".join(str(loc) for loc in error["loc"])
            print(f"  - {location}: {error['msg']}", file=sys.stderr)

        return 0 if show_bad_example else 1

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        if verbose:
            import traceback

            traceback.print_exc()
        return 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Validate runtime configuration")
    parser.add_argument("--config", help="Path to configuration file")
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Enable verbose output"
    )
    parser.add_argument(
        "-e",
        "--example",
        action="store_true",
        help="Use example configuration from examples directory",
    )
    parser.add_argument(
        "-b",
        "--bad-example",
        action="store_true",
        help="Use bad example configuration to show validation errors",
    )

    args = parser.parse_args()

    if args.config:
        config_path = args.config
    elif args.bad_example:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(
            script_dir, "examples", "bad_runtime_config_example.json"
        )
        print(f"Using bad example configuration: {config_path}")
    elif args.example:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(
            script_dir, "examples", "runtime_config_example.json"
        )
        print(f"Using example configuration: {config_path}")
    else:
        parser.print_help()
        sys.exit(1)

    sys.exit(main(config_path, args.verbose, args.bad_example))
