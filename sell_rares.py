#!/usr/bin/env python
from functions import *
from config import *
from pprint import pprint
from elasticsearch import Elasticsearch
arguments = get_input()

#get rares
esQuery = {
  'query' : {
    'bool' : {
      'must' : [
        { 'match' : { "_type" : "commodity" } },
        { 'match' : { "category_id" : 1000 } } 
      ]
    }
  },
  'size': 1000
}

rares = esFastSearch(esHost,esPort,esIndex,esQuery)['hits']['hits']

goodStars = []

for station in rares:

  padSize = getStationPadSize( station['_source']['station_id'] )
  stationDistance = getStationDistance( station['_source']['station_id'] )

  if padSize == "L" and stationDistance < 10000:
    systemLocation = getSystemLocation( station['_source']['system_id'] )
    goodStars.append({
      'good' : station['_source']['name'],
      'name' : station['_source']['system'],
      'id' : station['_source']['system_id'],
      'x' : systemLocation['x'][0],
      'y' : systemLocation['y'][0],
      'z' : systemLocation['z'][0]
    })

#make sure we have no dupe systems
dupeStars = []
for index,star in enumerate(goodStars):
  if star['name'] in dupeStars:
    del goodStars[index]
  else:
    dupeStars.append(star['name'])

esQuery = {
  'query' : {
    'bool' : {
      'must' : [
        { 'match' : { "_type" : "system" } },
        { 'match' : { "name" : arguments.system } } 
      ]
    }
  },
  'size': 1
}

currentSystem = esFastSearch(esHost,esPort,esIndex,esQuery)['hits']['hits'][0]['_source']

for star in goodStars:

  if getSystemDistanceWithLoc(star, currentSystem) > 200:
    print star['good']

#pprint(currentSystem)
#pprint(goodStars)



