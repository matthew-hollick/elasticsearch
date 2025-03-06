#!/usr/bin/env bash

git clone https://github.com/prometheus/snmp_exporter.git
pushd snmp_exporter
make
popd
