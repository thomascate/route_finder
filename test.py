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

esQuery = {
  'query' : {
    'bool' : {
      'must' : [
        { 'match' : { "_type" : "commodity" } },
        { 'match' : { "category_id" : 1000 } } 
#        { 'match' : { "name" : "39 Tauri" } }
      ]
    }
  },
  'size': 1000
#  'fields': [ 'name', 'x', 'y', 'z' ]
}

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
dupeStars = []
for index,star in enumerate(goodStars):
  if star['name'] in dupeStars:
    del goodStars[index]
  else:
    dupeStars.append(star['name'])

print "finding closest next hop for each star"
#first do a naive fast path to get these systems into an ok order
pass1 = naiveFastSort(goodStars)
 #   print ( "{:18}\t=>\t{:18}\t{:10}".format(system['name'], naiveFinalSystems[0]['name'], round(curRange)) )  
print ( "{} LY according to naiveFastSort".format( round( getTotalRange( pass1) ) ) )

print "trying 1,000,000 bruteforce"
pass2 = bruteForceSort( pass1, getTotalRange( pass1 ), 1000000 )
print ( "{} LY according to bruteForceSort".format( round( getTotalRange( pass2 ) ) ) )

print "trying our luck, 1,000,000 random sorts"
pass3 = randSort( pass2, getTotalRange( pass2 ), 1000000 )
print ( "{} LY according to randSort".format( round( getTotalRange( pass3 ) ) ) )

print "let bruteforce play with those results"
pass4 = bruteForceSort( pass3, getTotalRange( pass3 ), 1000000 )

for index,system in enumerate(pass4):
  if index < len(pass4) -1:
    curRange = getSystemDistanceWithLoc(system,pass4[index+1])
    print ( "{:18}\t{:18}\t{:10}".format(system['name'], pass4[index+1]['name'], round(curRange)) )

print ( "{} LY is the best we have".format( round( getTotalRange( pass4 ) ) ) )


exit()