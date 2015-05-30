#!/usr/bin/env python
import argparse
from config import *
import itertools
import numpy
from random import shuffle, choice
import requests
import ujson as json
from pprint import pprint

def get_input():
  parser = argparse.ArgumentParser(description='Find rares more than 200LY away')
  parser.add_argument(
                      '-s',
                      action='store',
                      dest='system',
                      help='system name you are at'
                      )

  results = parser.parse_args()
  if not (results.system):
    parser.error('no system provided')
  return results

#currently filters for systems with rares, large pad, non-illegal goods, <10k distance
def getSystemList():

  #rare systems that sell possibly illegal goods
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
    'Tarach Tor',
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

  return goodStars

def esFastSearch( esHost, esPort, esIndex, esQuery ):

  #Significantly faster than default ES library when handling
  #very large responses.
  url = "http://{}:{}/{}/_search".format( esHost, esPort, esIndex )
  response = requests.post( url, data = json.dumps( esQuery ) )

  return json.loads( response.content )

def esInsert( esHost, esPort, docType, esQuery):

  url = "http://{}:{}/{}/{}".format( esHost, esPort, esIndex, docType )
  response = requests.post( url, data = json.dumps( esQuery ) )

  return json.loads( response.content )

def esRefresh( esHost, esPort, esIndex ):
  url = "http://{}:{}/{}/_refresh".format( esHost, esPort, esIndex )
  response = requests.post( url )

  return json.loads( response.content )

def esUpdate( esHost, esPort, docType, docID, esQuery):

  url = "http://{}:{}/{}/{}/{}".format( esHost, esPort, esIndex, docType, docID )
  response = requests.put( url, data = json.dumps( esQuery ) )

  return json.loads( response.content )

def getStationDistance(stationID):
  esQuery = {
    'query' : {
      'bool' : {
        'must' : [
          { 'match' : { "_type" : "station" } },
          { 'match' : { "id" : stationID } }
        ]
      }
    },
    'size': 1,
    'fields': [ 'distance_to_star' ]
  }

  response = esFastSearch( esHost, esPort, esIndex, esQuery )

  if len(response['hits']['hits']) == 1:
    stationDistance = response['hits']['hits'][0]['fields']['distance_to_star'][0]
  else:
    stationDistance = -1

  return stationDistance

def getStationID(stationName):

  esQuery = {
    'query' : {
      'bool' : {
        'must' : [
          { 'match' : { "_type" : "station" } },
          { 'match' : { "name" : stationName } }
        ]
      }
    },
    'size': 1,
    'fields': [ 'id' ]
  }

  response = esFastSearch( esHost, esPort, esIndex, esQuery )
  if len(response['hits']['hits']) == 1:
    stationID = response['hits']['hits'][0]['fields']['id'][0]
  #['hits']['hits'][0]['fields']['id'][0]
  else:
    stationID = -1

  #systemID = 10
  return stationID

def getRareStationFromSystem(systemID):

  esQuery = {
    "query" : {
      "bool" : {
        "must" : [
          { "match" : { "_type" : "commodity" } },
          { "match" : { "category_id" : 1000 } },
          { "match" : { "system_id" : systemID } }
        ]
      }
    },
    "size": 100,
    "fields": [ "station" ]
  }

  response = esFastSearch( esHost, esPort, esIndex, esQuery )
  if len(response['hits']['hits']) > 0:
    stationName = str(response['hits']['hits'][0]['fields']['station'])[2:-1]
  else:
    stationName = -1

  return stationName

def getStationPadSize(stationID):
  esQuery = {
    'query' : {
      'bool' : {
        'must' : [
          { 'match' : { "_type" : "station" } },
          { 'match' : { "id" : stationID } }
        ]
      }
    },
    'size': 1,
    'fields': [ 'max_landing_pad_size' ]
  }

  response = esFastSearch( esHost, esPort, esIndex, esQuery )

  if len(response['hits']['hits']) == 1:
    padSize = response['hits']['hits'][0]['fields']['max_landing_pad_size'][0]
  else:
    padSize = -1

  return padSize

#Get system distance with location. Expects two dictionaries with keys of x, y, z that have stellar coords.
def getSystemDistanceWithLoc(system1, system2):

  location1 = numpy.array([system1['x'],system1['y'],system1['z']])
  location2 = numpy.array([system2['x'],system2['y'],system2['z']])
  distance = numpy.linalg.norm(location1-location2)

  return distance

def getSystemID(systemName):

  esQuery = {
    'query' : {
      'bool' : {
        'must' : [
          { 'match' : { "_type" : "system" } },
          { 'match' : { "name" : systemName } }
        ]
      }
    },
    'size': 1,
    'fields': [ 'id' ]
  }

  response = esFastSearch( esHost, esPort, esIndex, esQuery )
  if len(response['hits']['hits']) == 1:
    systemID = response['hits']['hits'][0]['fields']['id'][0]
  else:
    systemID = -1

  #systemID = 10
  return systemID

def getSystemLocation(systemID):

  esQuery = {
    'query' : {
      'bool' : {
        'must' : [
          { 'match' : { "_type" : "system" } },
          { 'match' : { "id" : systemID } }
        ]
      }
    },
    'size': 1,
    'fields': [ 'x', 'y', 'z' ]
  }

  response = esFastSearch( esHost, esPort, esIndex, esQuery )
  if len(response['hits']['hits']) == 1:
    stationLocation = response['hits']['hits'][0]['fields']
  else:
    stationLocation = -1

  return stationLocation

def getTotalRange(systems):

  totalRange = 0
  for index,system in enumerate(systems):
  
    if index < len(systems) -1:
      curRange = getSystemDistanceWithLoc(system,systems[index+1])
      totalRange += curRange
    else:
      curRange = getSystemDistanceWithLoc(system,systems[0])
      totalRange += curRange

  return totalRange

#This function expects a list of systems and returns a next best order
#starting and ending on the first system in the list. Each entry in the list
#must be a dict with the keys, 'name', 'id', 'x', 'y', 'z'.
def naiveFastSort(systems):

  finalSystems = []
  destSystems = list(systems)
  for index, item in enumerate(systems):

    bestRange = 0
    for index, system in enumerate(destSystems):
      curRange = getSystemDistanceWithLoc(item,system)

      if curRange < bestRange or bestRange == 0:
        bestRange = curRange
        nextHop = system
        delIndex = index

    del destSystems[delIndex]
    finalSystems.append(nextHop)

  finalSystems.append(finalSystems[0])

  return finalSystems

#This function expects a list in the same format as naiveFastSort, as well as
#an int limit on how many times to run and a target. If target is not beaten
#the original list is returned
def bruteForceSort(systems,target,limit):

  bestRange = target
  bestPath = list(systems)
  startSystem = systems[0]
  endSystem = systems[-1]
  del systems[0]
  del systems[-1]

  for index, item in enumerate(itertools.permutations(systems)):

    if index > limit:
      break

    tempSystems = list(item)
    tempSystems.insert(0,startSystem)
    tempSystems.append(endSystem)

    curRange = getTotalRange(tempSystems)
    if curRange < bestRange:
      bestRange = curRange
      bestPath = list(tempSystems)

  return bestPath

def bruteWithStart(systems,target,limit,start):

  bestRange = target
  bestPath = list(systems)
  startSystem = systems[0]
  endSystem = systems[-1]
  del systems[0]
  del systems[-1]

  #this will get progressively slower
  #not sure of a better way to handle it though
#  for index, item in enumerate(itertools.permutations(systems)):
#    if index > start:
#      systems = item
#      break

  print "starting consume"
  consume(itertools.permutations(systems), start)
  print "done counsuming"
  for index, item in enumerate(itertools.permutations(systems)):

    if index > start + limit:
      break

    tempSystems = list(item)
    tempSystems.insert(0,startSystem)
    tempSystems.append(endSystem)

    curRange = getTotalRange(tempSystems)
    if curRange < bestRange:
      bestRange = curRange
      bestPath = list(tempSystems)
    if index == start:
      print curRange
      print tempSystems[1]
      print tempSystems[-2]
  return bestPath

#This function is similar to bruteForceSort but will run until it finds a better
#match and return. This may run forever.
def bruteNoLimit(systems,target):
  bestRange = target
  bestPath = list(systems)
  startSystem = systems[0]
  endSystem = systems[-1]
  del systems[0]
  del systems[-1]

  for index, item in enumerate(itertools.permutations(systems)):

    tempSystems = list(item)
    tempSystems.insert(0,startSystem)
    tempSystems.append(endSystem)

    curRange = getTotalRange(tempSystems)
    if curRange < bestRange:
      bestRange = curRange
      bestPath = list(tempSystems)
      break

  return bestPath

def randSort(systems,target,limit):

  bestRange = target
  bestPath = list(systems)
  startSystem = systems[0]
  endSystem = systems[-1]
  del systems[0]
  del systems[-1]


  for x in range(0, limit):

    tempSystems = list(systems)
    shuffle(tempSystems)
    tempSystems.insert(0,startSystem)
    tempSystems.append(endSystem)

    curRange = getTotalRange(tempSystems)
    if curRange < bestRange:
      bestRange = curRange
      bestPath = list(tempSystems)

  return bestPath

def swapSort(systems,target,limit):

  bestRange = target
  bestPath = list(systems)
  startSystem = systems[0]
  endSystem = systems[-1]
  del systems[0]
  del systems[-1]

  for x in range(0, limit):

    tempSystems = list(systems)
    a, b = systems.index(choice(systems)), systems.index(choice(systems))
    if not a == b:
      systems[b], systems[a] = systems[a], systems[b]

      tempSystems.insert(0,startSystem)
      tempSystems.append(endSystem)
  
      curRange = getTotalRange(tempSystems)
      if curRange < bestRange:
        bestRange = curRange
        bestPath = list(tempSystems)


  return bestPath

def consume(iterator, n):
  "Advance the iterator n-steps ahead. If n is none, consume entirely."
  # Use functions that consume iterators at C speed.
  if n is None:
    # feed the entire iterator into a zero-length deque
    collections.deque(iterator, maxlen=0)
  else:
    # advance to the empty slice starting at position n
    next(itertools.islice(iterator, n, n), None)

  print iterator
