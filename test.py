#!/usr/bin/env python
from functions import *
from config import *
from pprint import pprint
import random
from datetime import datetime
import uuid

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

goodStars = getSystemList()

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
    print ( "{:18}\t{:18}\t{:10}".format(system['name'], pass1[index+1]['name'], round(curRange)) )

bestPath = list(pass1)

indexID = str(uuid.uuid4())
docType = 'route'

storeDict = {
  'indexID': indexID,
  'routes': [ bestPath ]
}
print json.dumps(indexID)
res = esInsert( esHost, esPort, docType, storeDict)
docID = res['_id']

print "let's just try some things"

while True:
  diceRoll = random.randrange(1,4)
  if diceRoll == 1:
    response = bruteForceSort(bestPath,bestRange,1000)
  elif diceRoll == 2:
    response = randSort(bestPath,bestRange,1000)
  else:
    response = swapSort(bestPath,bestRange,1000)

  if getTotalRange( response ) < bestRange:

    storeDict[ 'routes' ].append(response)
    res = esUpdate( esHost, esPort, docType, docID, storeDict)
    esRefresh(esHost, esPort, esIndex)
    for index,system in enumerate(response):
      #print system['name']
      if index < len(response) -1:
        curRange = getSystemDistanceWithLoc(system,response[index+1])
        #print type(curRange)
        print ( "{:18}\t{:18}\t{:10}\t{:4}".format(system['name'], response[index+1]['name'], round(curRange), getRareStationFromSystem(system['id']) ) )
    print ("{} LY is now the Best".format(round(getTotalRange( response ))) )
    print ""

  bestRange = getTotalRange( response )
  bestPath = response
exit()