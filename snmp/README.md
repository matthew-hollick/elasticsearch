# Getting SNMP data into Elasticsearch

## Requirements

- Use Prometheus SNMP exporter
- Metrics in ECS

## Tasks
1. Get a snmp simulator up and running in a container
  - Focus on SNMP 2c to start with
2. Build Prometheus SNMP exporter into a container
3. Curl Prometheus SNMP exporter to demonstrate viability
4. Elastic-agent configuration to pull from Prometheus SNMP exporter and push to Elasticsearch
5. Python script to pull from snmp exporter and push to Elasticsearch
  - bootstrap configuration in a file / env vars
  - SNMP configuration in Elasticsearch index

## SNMP Simulator

https://docs.lextudio.com/snmp/

Whut?
https://chatgpt.com/g/g-ZWj5VHbh7-snmp-guru
