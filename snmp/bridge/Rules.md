Development Rules

Rule 0: Consult Rules Before Changes

These rules must be consulted before any change is made
The rules document should be placed in the project root
Team members must acknowledge rules review in commit messages

Rule 1: Test-Backed Changes

Every change must be backed by suitable tests
Tests must be written before or alongside code changes
No code merges without passing tests

Rule 2: Version Control Discipline

Git will be used for version control
Commits will be frequent (at least daily)
All commits will have descriptive comments
Commit messages will explain the "why" not just the "what"

Rule 3: Component Isolation

Changes to previously tested components are prohibited
New functionality should be built as new components
Interfaces between components must remain stable
Component boundaries will be clearly defined

Rule 4: Network Decoupling

Components that communicate across networks must be decoupled
Core application logic must not depend directly on network components
Design for potential future parallelization
Strive for simplicity but avoid tight coupling with network operations

Rule 5: Configuration Update Handling

Runtime configuration will be periodically updated in Elasticsearch
Processes will maintain a local copy of configuration
After each action, process will check if configuration is current
If configuration is outdated, process should be reaped and replaced
New processes should start with fresh configuration

Rule 6: Bootstrap Configuration Sources

Bootstrap configuration can come from multiple sources
Support file-based configuration, environment variables, and command line arguments
Implement clear precedence order for configuration sources
Document all configuration options across all sources

Rule 7: Minimal Bootstrap Configuration

Minimal bootstrap configuration must include:

Elasticsearch server URL
Elasticsearch credentials
Configuration index name



Rule 8: Runtime Configuration Structure

Runtime configuration consists of one or more named records
Each record is a complete configuration containing:

Prometheus exporter URL
Optional Prometheus credentials
Query string for Prometheus
Custom mappings for ECS format conversion
Collection interval
Elasticsearch output URL
Elasticsearch output credentials
Target index or pipeline information



Rule 9: Time-Bracketed Batching

Elasticsearch batching should be time-bracketed
Support both time and size limits for batches
Flush batches on time limit regardless of size
Flush batches on size limit regardless of time

Rule 10: Prometheus Connection Timeout

All connections to Prometheus exporters must have a timeout
Timeout should be configurable in the runtime configuration
Failed connections should be properly handled and logged
Appropriate retry mechanisms should be implemented
