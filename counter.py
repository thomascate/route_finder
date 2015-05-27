#!/usr/bin/env python
from functions import *
from config import *
import uuid

#Just stupidly count up through all options
goodStars = getSystemList()

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

print "now let's just count up forever"

while True:
  response = bruteNoLimit(bestPath,bestRange)

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