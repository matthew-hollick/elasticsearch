#!/usr/bin/env bash

PROJECT_ROOT="$(git rev-parse --show-toplevel)/snmp"

pushd $PROJECT_ROOT
  uv sync
popd
