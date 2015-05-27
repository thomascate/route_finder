#!/usr/bin/env python
from functions import *
from config import *
from pprint import pprint
import random
from datetime import datetime
import uuid
import Queue
import sys
import threading

threads = 4

illegalList = [
  'Bast',
  'HIP 59533',
  'Alpha Centauri',
  'Aerial',
  'Eranin',
  'Geras',
  'Epsilon Indi',
  'Kappa Fornacis',
  'Kamitra',
  'Kongga',
  'Lave',
  'Orrere',
  'Rusani',
  'Wolf 1301',
  'Wuthielo Ku',
  'Yaso Kondi'
]

esQuery = {
  'query' : {
    'bool' : {
      'must' : [
        { 'match' : { "_type" : "commodity" } },
        { 'match' : { "category_id" : 1000 } } 
      ],
      'must_not' : [
        { 'match' : { "station_id" : 99 } },
        { 'match' : { "station_id" : 276 } },
        { 'match' : { "station_id" : 51 } }
      ]
    }
  },
  'size': 1000
}

for index,good in enumerate(illegalList):
  esQuery['query']['bool']['must_not'].append( { 'match' : { 'name' : good}} )

rares = esFastSearch(esHost,esPort,esIndex,esQuery)['hits']['hits']

goodStars = []

for station in rares:

  padSize = getStationPadSize( station['_source']['station_id'] )
  stationDistance = getStationDistance( station['_source']['station_id'] )

  if padSize == "L" and stationDistance < 10000:
    systemLocation = getSystemLocation( station['_source']['system_id'] )

    goodStars.append({
      'name' : station['_source']['system'],
      'id' : station['_source']['system_id'],
      'x' : systemLocation['x'][0],
      'y' : systemLocation['y'][0],
      'z' : systemLocation['z'][0]
    })

#make sure we have no dupe systems
starNames = []
for star in enumerate(goodStars):
  starNames.append(star[1]['name'])


for index,star in enumerate(goodStars):
  #print starNames.count(star['name'])
  if starNames.count(star['name']) > 1:
    del goodStars[index]
    starNames.remove(star['name'])


pprint (goodStars)
