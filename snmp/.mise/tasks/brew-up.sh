#!/usr/bin/env bash

PROJECT_ROOT="$(git rev-parse --show-toplevel)/snmp"

brew bundle install --file=${PROJECT_ROOT}/Brewfile
