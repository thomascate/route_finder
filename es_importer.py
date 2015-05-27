#!/usr/bin/env python
from elasticsearch import Elasticsearch
from elasticsearch import helpers
import json
from pprint import pprint

filename = "stationfix.json"
filename2 = "commodities.json"
index    = "route_finder"
doctype  = "station"

FH = open(filename)

documents = json.loads(FH.read())

esHost = "localhost"
esIndexSettings = {
                   "settings": {
                     "number_of_shards": 5,
                     "number_of_replicas": 0,
                    }
                  }

allDocuments = []

for document in documents:

  currentDoc = {
                  '_index': index,
                  '_type': doctype,
                  '_source': document
                }

  allDocuments.append( currentDoc )

es = Elasticsearch([esHost], sniff_on_start=True)
es.indices.create(index=index, body = esIndexSettings, ignore=400)

if len(allDocuments) > 0:
  helpers.bulk(es, allDocuments)
