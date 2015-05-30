#!/usr/bin/env python
from elasticsearch import Elasticsearch
from elasticsearch import helpers
from pprint import pprint


esSourceHost = "localhost"
esDestHost = "104.236.21.171"
esIndexSettings = {
                   "settings": {
                     "number_of_shards": 5,
                     "number_of_replicas": 0,
                    }
                  }


esSource = Elasticsearch([esSourceHost], sniff_on_start=True)
esDest = Elasticsearch([esDestHost], sniff_on_start=True)

res = esSource.search(index="route_finder", body={
  "query": {
    "match_all": {
    }
  },
  'size': 100000
#  'size': 3
})
#pprint(res)
uploadData = []

for document in res['hits']['hits']:
#  for key in document:
  document.pop("_id", None)
  document.pop("_score", None)

  uploadData.append(document)

esDest.indices.create(index="route_finder", body = esIndexSettings, ignore=400)

if len(uploadData) > 0:
  helpers.bulk(esDest, uploadData)
