# How big can I make things in Elasticsearch?

# Field names
It is more common than not to leave index mapping as dynamic. I was interested to see if this conuld be abused by creating huge field names. Here is a simple script to create progressively larger field names. TLDR: Elasticsearch can create field names longer than 4000 charcters. I've not witnessed any issues. A naive question, the field id is probably stored in memory, not the field name. I have not explored the impact to replication, this might be more interesting. A dumb question with a dumb implementation and probably a dumb answerr..

## Setup

```
DELETE fred

PUT fred
{
  "settings": {
    "number_of_shards": 1,
    "number_of_replicas": 1,
    "index.mapping.total_fields.limit": 6000,
    "index.refresh_interval": "1s"
  }
}

```

### Run it

./field_name_max_size.sh

### Note
2 curl requests are made for each field name

- define the field with forced type of text (prevent elasticsearch creating an associted keyword field)
- realise a single record using the field.
