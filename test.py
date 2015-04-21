#!/usr/bin/env python
from functions import *
from config import *
from pprint import pprint
from elasticsearch import Elasticsearch
import random

#FH = open("stations.json", "r")
#FH2 = open("stationfix.json", "w")
#test = json.loads(FH.read())

#for index,station in enumerate(test):
#  if station['id'] == 3002:
#    test[index]['distance_to_star'] = 728
#    pprint ( station )

#FH2.write(json.dumps(test))

#pprint (test)
#exit()

#rare systems that sell possibly illegal goods
illegalList = [
  'Bast',
  'HIP 59533',
  'Alpha Centauri',
  'Aerial',
  'Eranin',
  'Geras',
  'Epsilon Indi',
  'Kamitra',
  'Kongga',
  'Lave',
  'Orrere',
  'Rusani'
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
        { 'match' : { "station_id" : 276 } }
      ]
    }
  },
  'size': 1000
}

for index,good in enumerate(illegalList):
  esQuery['query']['bool']['must_not'].append( { 'match' : { 'name' : good}} )

#print json.dumps(esQuery)
#WHY THE FLYING FUCK ARE LAVE AND ORRERE STILL IN HERE!

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

#for station in rares:
  #print station['_source']['system']
#  if station['_source']['system'] == '47 Ceti':
#    pprint (station)

print "finding closest next hop for each star"
#first do a naive fast path to get these systems into an ok order
pass1 = naiveFastSort(goodStars)
 #   print ( "{:18}\t=>\t{:18}\t{:10}".format(system['name'], naiveFinalSystems[0]['name'], round(curRange)) )  
bestRange = getTotalRange( pass1 )
print ( "{} LY from Greedy first pass ".format(bestRange) )

for index,system in enumerate(pass1):
  if index < len(pass1) -1:
    curRange = getSystemDistanceWithLoc(system,pass1[index+1])
#    print ( "{:18}\t{:18}\t{:10}".format(system['name'], pass1[index+1]['name'], round(curRange)) )

bestPath = list(pass1)

print "let's just try some things"
while True:
  #diceRoll = 1
  diceRoll = random.randrange(1,4)
  if diceRoll == 1:
    response = bruteForceSort(bestPath,bestRange,1000)
    #print "brute"
  elif diceRoll == 2:
    #print "rand"
    response = randSort(bestPath,bestRange,1000)
  else:
    #print "swap"
    response = swapSort(bestPath,bestRange,1000)


  if getTotalRange( response ) < bestRange:
    for index,system in enumerate(response):
      #print system['name']
      if index < len(response) -1:
        curRange = getSystemDistanceWithLoc(system,response[index+1])
        #print type(curRange)
        print ( "{:18}\t{:18}\t{:10}".format(system['name'], response[index+1]['name'], round(curRange)) )
    print ("{} LY is now the Best".format(round(getTotalRange( response ))) )
    print ""

  bestRange = getTotalRange( response )
  bestPath = response
exit()