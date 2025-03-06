"""
Runtime configuration schema definition using Pydantic.
This module provides classes for validating runtime configuration.
"""

from enum import Enum
from typing import Dict, List, Optional, Union, Any
from pydantic import BaseModel, Field, HttpUrl, validator


class ECSFieldType(str, Enum):
    """Valid ECS field types."""

    KEYWORD = "keyword"
    TEXT = "text"
    LONG = "long"
    INTEGER = "integer"
    SHORT = "short"
    BYTE = "byte"
    DOUBLE = "double"
    FLOAT = "float"
    DATE = "date"
    BOOLEAN = "boolean"
    IP = "ip"


class TLSConfig(BaseModel):
    """TLS/SSL configuration for HTTP connections."""

    verify: bool = Field(default=True, description="Whether to verify TLS certificates")
    ca_cert: Optional[str] = Field(None, description="Path to CA certificate file")
    client_cert: Optional[str] = Field(
        None, description="Path to client certificate file"
    )
    client_key: Optional[str] = Field(None, description="Path to client key file")


class UsernamePasswordAuth(BaseModel):
    """Username and password authentication."""

    username: str = Field(..., description="Username for basic authentication")
    password: str = Field(..., description="Password for basic authentication")


class BearerTokenAuth(BaseModel):
    """Bearer token authentication."""

    bearer_token: str = Field(..., description="Bearer token for authentication")


class ApiKeyAuth(BaseModel):
    """API key authentication."""

    api_key: str = Field(..., description="API key for authentication")


class ElasticsearchConfig(BaseModel):
    """Configuration for Elasticsearch connection."""

    auth: Union[UsernamePasswordAuth, ApiKeyAuth] = Field(
        ..., description="Authentication credentials for Elasticsearch"
    )
    tls: Optional[TLSConfig] = Field(None, description="TLS/SSL configuration")


class ExporterConfig(BaseModel):
    """Configuration for a Prometheus exporter."""

    type: str = Field(
        ..., description="Type of the exporter (e.g., snmp, node, blackbox)"
    )
    url: HttpUrl = Field(..., description="URL of the exporter")
    auth: Optional[Union[UsernamePasswordAuth, BearerTokenAuth, ApiKeyAuth]] = Field(
        None, description="Authentication configuration for the exporter"
    )
    tls: Optional[TLSConfig] = Field(None, description="TLS/SSL configuration")
    headers: Optional[Dict[str, str]] = Field(
        None, description="Additional HTTP headers to include in requests"
    )
    timeout: Optional[int] = Field(
        10, description="Timeout for requests in seconds", ge=1
    )
    metadata: Optional[Dict[str, Any]] = Field(
        None, description="Additional metadata for the exporter"
    )


class ECSMapping(BaseModel):
    """Mapping to ECS fields."""

    field: str = Field(..., description="ECS field to map to")
    type: ECSFieldType = Field(..., description="ECS field type")


class MetricConfig(BaseModel):
    """Configuration for a metric to collect."""

    name: str = Field(..., description="Name of the metric")
    path: str = Field(..., description="Path or pattern to match the metric")
    labels: Optional[List[str]] = Field(
        None, description="Labels to include with the metric"
    )
    ecs_mapping: Optional[ECSMapping] = Field(None, description="Mapping to ECS fields")


class TargetConfig(BaseModel):
    """Configuration for a target to scrape."""

    exporter: str = Field(
        ..., description="Reference to an exporter defined in the exporters section"
    )
    interval: int = Field(..., description="Scrape interval in seconds", ge=1)
    # Parameters can be specified either directly or via params dictionary
    params: Optional[Dict[str, str]] = Field(
        None, description="Parameters to include in the request URL (legacy format)"
    )
    module: Optional[str] = Field(None, description="Module name for SNMP exporter")
    target: Optional[str] = Field(None, description="Target address for SNMP exporter")
    auth: Optional[str] = Field(
        None, description="Authentication type for SNMP exporter"
    )
    metrics: List[MetricConfig] = Field(
        ..., description="Metrics to collect from this target"
    )
    timeout: Optional[int] = Field(
        None,
        description="Timeout for requests in seconds, overrides exporter timeout",
        ge=1,
    )
    metadata: Optional[Dict[str, Any]] = Field(
        None, description="Additional metadata for the target"
    )
    index: Optional[str] = Field(
        "hedgehog-snmp-metrics", description="Elasticsearch index to write metrics to"
    )


class GlobalConfig(BaseModel):
    """Global settings for all exporters and targets."""

    timeout: int = Field(30, description="Global timeout for requests in seconds", ge=1)
    retries: int = Field(3, description="Number of retries for failed requests", ge=0)
    retry_interval: int = Field(
        5, description="Interval between retries in seconds", ge=1
    )
    concurrency: int = Field(
        10, description="Maximum number of concurrent scrapes", ge=1
    )
    metadata: Optional[Dict[str, Any]] = Field(
        None, description="Global metadata to include with all metrics"
    )
    elasticsearch: Optional[ElasticsearchConfig] = Field(
        None, description="Elasticsearch configuration for writing metrics"
    )


class RuntimeConfig(BaseModel):
    """Runtime configuration for the application.
    This configuration is stored in Elasticsearch and defines what metrics to collect.
    """

    version: str = Field(..., description="Version of the configuration schema")
    exporters: Dict[str, ExporterConfig] = Field(
        ..., description="Definition of Prometheus exporters"
    )
    targets: Dict[str, TargetConfig] = Field(
        ..., description="Definition of targets to scrape"
    )
    global_: Optional[GlobalConfig] = Field(
        None,
        alias="global",
        description="Global settings for all exporters and targets",
    )

    @validator("targets")
    def validate_exporter_references(cls, v, values):
        """Validate that all exporter references in targets exist in exporters."""
        if "exporters" in values:
            exporters = values["exporters"]
            for target_name, target in v.items():
                if target.exporter not in exporters:
                    raise ValueError(
                        f"Target '{target_name}' references unknown exporter '{target.exporter}'"
                    )
        return v
