#!/usr/bin/env python
import argparse
from config import *
import itertools
import numpy
from random import shuffle
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

def esFastSearch( esHost, esPort, esIndex, esQuery ):

  #Significantly faster than default ES library when handling
  #very large responses.
  url = "http://{}:{}/{}/_search".format( esHost, esPort, esIndex )
  response = requests.post( url, data = json.dumps( esQuery ) )

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

  return finalSystems

#This function expects a list in the same format as naiveFastSort, as well as
#an int limit on how many times to run and a target. If target is not beaten
#the original list is returned
def bruteForceSort(systems,target,limit):

  startLocation = systems[0]
  del systems[0]

  bestRange = target
  bestPath = systems

  for index, item in enumerate(itertools.permutations(systems)):
    if index > limit:
      break

    tempSystems = list(item)
    tempSystems.append(startLocation)
    tempSystems = list(reversed(tempSystems))
    tempSystems.append(startLocation)

    curRange = getTotalRange(tempSystems)
    if curRange < bestRange:
      bestRange = curRange
      bestPath = tempSystems

  return bestPath

def randSort(systems,target,limit):
  startLocation = systems[0]
  del systems[0]

  bestRange = target
  bestPath = systems

  for x in range(0, limit):

    tempSystems = list(systems)
    shuffle(tempSystems)
    tempSystems.append(startLocation)
    tempSystems = list(reversed(tempSystems))
    tempSystems.append(startLocation)

    curRange = getTotalRange(tempSystems)
    if curRange < bestRange:
      bestRange = curRange
      bestPath = tempSystems

  return bestPath