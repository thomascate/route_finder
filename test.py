#!/usr/bin/env python
from functions import *
from config import *
from pprint import pprint
from elasticsearch import Elasticsearch

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

for index,system in enumerate(pass1):
  if index < len(pass1) -1:
    curRange = getSystemDistanceWithLoc(system,pass1[index+1])
    print ( "{:18}\t{:18}\t{:10}".format(system['name'], pass1[index+1]['name'], round(curRange)) )

print ( "{} LY according to naiveFastSort".format( round( getTotalRange( pass1) ) ) )

print "trying 10000 random"
pass2 = randSort( pass1, getTotalRange( pass1 ), 10000 )

for index,system in enumerate(pass2):
  if index < len(pass2) -1:
    curRange = getSystemDistanceWithLoc(system,pass2[index+1])
    print ( "{:18}\t{:18}\t{:10}".format(system['name'], pass2[index+1]['name'], round(curRange)) )
print ( "{} LY according to randsort".format( round( getTotalRange( pass2 ) ) ) )

print "trying 10000 bruteforce"
pass3 = bruteForceSort( pass2, getTotalRange( pass2 ), 10000 )

for index,system in enumerate(pass3):
  if index < len(pass3) -1:
    curRange = getSystemDistanceWithLoc(system,pass3[index+1])
    print ( "{:18}\t{:18}\t{:10}".format(system['name'], pass3[index+1]['name'], round(curRange)) )
print ( "{} LY according to bruteForceSort".format( round( getTotalRange( pass3 ) ) ) )


print "trying our luck, 10,000 random sorts"
pass4 = randSort( pass3, getTotalRange( pass3 ), 100000000 )

for index,system in enumerate(pass4):
  if index < len(pass4) -1:
    curRange = getSystemDistanceWithLoc(system,pass4[index+1])
    print ( "{:18}\t{:18}\t{:10}".format(system['name'], pass4[index+1]['name'], round(curRange)) )
print ( "{} LY according to randSort".format( round( getTotalRange( pass4 ) ) ) )


print "let bruteforce play with those results"
pass5 = bruteForceSort( pass4, getTotalRange( pass4 ), 1000000 )

for index,system in enumerate(pass5):
  if index < len(pass5) -1:
    curRange = getSystemDistanceWithLoc(system,pass5[index+1])
    print ( "{:18}\t{:18}\t{:10}".format(system['name'], pass5[index+1]['name'], round(curRange)) )

print ( "{} LY is the best we have".format( round( getTotalRange( pass5 ) ) ) )

exit()