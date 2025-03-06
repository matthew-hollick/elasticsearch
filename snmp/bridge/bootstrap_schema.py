"""
Bootstrap configuration schema definition using Pydantic.
This module provides classes for validating bootstrap configuration.
"""

from enum import Enum
from typing import Optional, Union
from pydantic import BaseModel, Field, HttpUrl


class LogLevel(str, Enum):
    """Valid logging levels."""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class LoggingConfig(BaseModel):
    """Configuration for application logging."""

    level: LogLevel = Field(default=LogLevel.INFO, description="Logging level")
    file: Optional[str] = Field(
        None, description="Path to log file (if not specified, logs to stdout)"
    )


class TLSConfig(BaseModel):
    """TLS/SSL configuration for Elasticsearch connections."""

    verify: bool = Field(default=True, description="Whether to verify TLS certificates")
    ca_cert: Optional[str] = Field(
        None, description="Path to CA certificate file for TLS verification"
    )
    client_cert: Optional[str] = Field(
        None,
        description="Path to client certificate file for TLS client authentication",
    )
    client_key: Optional[str] = Field(
        None, description="Path to client key file for TLS client authentication"
    )


class UsernamePasswordAuth(BaseModel):
    """Username and password authentication for Elasticsearch."""

    username: str = Field(..., description="Username for Elasticsearch authentication")
    password: str = Field(..., description="Password for Elasticsearch authentication")


class ApiKeyAuth(BaseModel):
    """API key authentication for Elasticsearch."""

    api_key: str = Field(..., description="API key for Elasticsearch authentication")


class ElasticsearchConfig(BaseModel):
    """Configuration for Elasticsearch connection."""

    url: HttpUrl = Field(..., description="URL of the Elasticsearch server")
    auth: Optional[Union[UsernamePasswordAuth, ApiKeyAuth]] = Field(
        None, description="Authentication credentials for Elasticsearch"
    )
    tls: Optional[TLSConfig] = Field(None, description="TLS/SSL configuration")


class BootstrapConfig(BaseModel):
    """
    Bootstrap configuration for the application.
    This is the minimal configuration needed to start the application.
    """

    elasticsearch: ElasticsearchConfig = Field(
        ..., description="Elasticsearch connection configuration"
    )
    config_index: str = Field(
        ...,
        description="Name of the Elasticsearch index containing runtime configuration",
    )
    logging: Optional[LoggingConfig] = Field(None, description="Logging configuration")


# Example usage:
#
# from bootstrap_schema import BootstrapConfig
# import yaml
#
# # Load configuration from YAML file
# with open("config.yaml", "r") as f:
#     config_data = yaml.safe_load(f)
#
# # Validate configuration against schema
# try:
#     config = BootstrapConfig(**config_data["bootstrap"])
#     print("Configuration is valid!")
# except Exception as e:
#     print(f"Configuration validation error: {e}")
