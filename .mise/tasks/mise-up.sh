#!/usr/bin/env bash

PROJECT_ROOT="$(git rev-parse --show-toplevel)"

pushd $PROJECT_ROOT
  mise install
popd
