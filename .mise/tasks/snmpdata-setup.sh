#!/usr/bin/env bash

PROJECT_ROOT="$(git rev-parse --show-toplevel)/snmp"

pushd $PROJECT_ROOT
  mkdir data
  uv run setup-snmpsim-data ./data
popd
