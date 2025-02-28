#!/usr/bin/env bash

set -e

max_length=30000000
this_length=1
es_username=elastic
es_password=changeme
es_url="https://localhost:9200"
es_index="fred"

while [ $this_length -le $max_length ]; do
 field_name=`pwgen -AN1 ${this_length} | tr -d '\n'`
 echo "field name $field_name and is  $this_length long"
 curl -sk -u ${es_username}:${es_password} -XPUT "${es_url}/${es_index}/_mapping" -H "Content-Type: application/json" -d"{\"properties\":{\"${field_name}\":{\"type\":\"text\",\"fields\":{}}}}"  > /dev/null
 curl -sk -u ${es_username}:${es_password} "${es_url}/${es_index}/_doc/" -H "Content-Type: application/json" -d"{ \"${field_name}\": \"test\"}" > /dev/null
 let this_length=this_length+1
done
