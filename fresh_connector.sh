#!/usr/bin/env bash
cd "${0%/*}"
source ./bin/activate
./bin/python fresh_connector.py "$@"
deactivate
