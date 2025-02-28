#!/usr/bin/env bash

set -e

max_length=3000
this_length=1
es_username=elastic
es_password=changeme
es_url="https://localhost:9200"
es_index="fred"

curl -sk -u ${es_username}:${es_password} "${es_url}/${es_index}/_mapping?pretty" | grep type | wc -l
