#!/usr/bin/env python3
"""
Integration test script for testing authentication with a real SNMP exporter.
This script can be used to verify that the authentication works correctly
with a running SNMP exporter instance.
"""

import argparse
import requests
import sys
from typing import Dict, Optional
from urllib.parse import urljoin


def test_exporter_auth(
    url: str,
    username: Optional[str] = None,
    password: Optional[str] = None,
    bearer_token: Optional[str] = None,
    api_key: Optional[str] = None,
    api_key_header: str = "X-API-Key",
    verify_ssl: bool = True,
    endpoint: str = "/metrics",
    params: Optional[Dict[str, str]] = None,
) -> bool:
    """
    Test authentication with a Prometheus exporter.

    Args:
        url: Base URL of the exporter
        username: Username for basic auth
        password: Password for basic auth
        bearer_token: Bearer token for token-based auth
        api_key: API key for API key-based auth
        api_key_header: Header name for API key
        verify_ssl: Whether to verify SSL certificates
        endpoint: Endpoint to test (default: /metrics)
        params: Query parameters to include in the request

    Returns:
        True if authentication succeeded, False otherwise
    """
    headers = {}
    auth = None

    # Set up authentication
    if username and password:
        auth = (username, password)
        print(f"Using basic authentication with username: {username}")
    elif bearer_token:
        headers["Authorization"] = f"Bearer {bearer_token}"
        print("Using bearer token authentication")
    elif api_key:
        headers[api_key_header] = api_key
        print(f"Using API key authentication with header: {api_key_header}")
    else:
        print("No authentication provided, testing without auth")

    # Make the request
    try:
        full_url = urljoin(url, endpoint)
        print(f"Making request to: {full_url}")

        response = requests.get(
            full_url, auth=auth, headers=headers, params=params, verify=verify_ssl
        )

        # Check if request was successful
        response.raise_for_status()

        # Print response details
        print(f"Authentication successful! Status code: {response.status_code}")
        print(f"Response size: {len(response.text)} bytes")

        # Print first few lines of response
        lines = response.text.split("\n")[:10]
        print("\nFirst few lines of response:")
        for line in lines:
            print(f"  {line}")

        if len(lines) < 10:
            print("  ...")

        return True

    except requests.exceptions.HTTPError as e:
        print(f"Authentication failed with HTTP error: {e}")
        return False
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return False


def main():
    """Parse arguments and run the test."""
    parser = argparse.ArgumentParser(
        description="Test authentication with a Prometheus exporter"
    )

    parser.add_argument("--url", required=True, help="Base URL of the exporter")
    parser.add_argument("--username", help="Username for basic auth")
    parser.add_argument("--password", help="Password for basic auth")
    parser.add_argument("--bearer-token", help="Bearer token for token-based auth")
    parser.add_argument("--api-key", help="API key for API key-based auth")
    parser.add_argument(
        "--api-key-header", default="X-API-Key", help="Header name for API key"
    )
    parser.add_argument(
        "--no-verify-ssl",
        action="store_true",
        help="Disable SSL certificate verification",
    )
    parser.add_argument(
        "--endpoint", default="/metrics", help="Endpoint to test (default: /metrics)"
    )
    parser.add_argument(
        "--param",
        action="append",
        nargs=2,
        metavar=("KEY", "VALUE"),
        help="Add a query parameter (can be used multiple times)",
    )

    args = parser.parse_args()

    # Convert params list to dictionary
    params = {}
    if args.param:
        for key, value in args.param:
            params[key] = value

    # Run the test
    success = test_exporter_auth(
        url=args.url,
        username=args.username,
        password=args.password,
        bearer_token=args.bearer_token,
        api_key=args.api_key,
        api_key_header=args.api_key_header,
        verify_ssl=not args.no_verify_ssl,
        endpoint=args.endpoint,
        params=params if params else None,
    )

    # Exit with appropriate status code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
