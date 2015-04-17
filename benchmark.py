#!/usr/bin/env python
from elasticsearch import Elasticsearch
from elasticsearch import helpers
import json
from pprint import pprint
import pymongo
import re
import time

testSystems = [
  'Vanayequi',
  'Kinago',
  'Geawen',
  'Helvetitj',
  'Vidavanta',
  'Heike',
  'Karetii',
  'HIP 80364',
  'Kongga',
  'Esuseku',
  'Ochoeng',
  'Haiden',
  'Uzumoku',
  'Thrutis',
  'Rusani',
  'HIP 41181',
  'Volkhab',
  'Damna',
  'Ethgreze',
  'Cherbones',
  'Borasetani',
  'Alacarakmo',
  'Rajukru',
  'Mukusubii',
  'Wulpa',
  'Sanuma'
]

tests = 10
client = pymongo.MongoClient('localhost', 27017)
db = client['route_finder']
collection = db.systems

print "Mongo: Getting all systems within 2000LY of Earth."
locationStart = time.time()
for x in range(0, tests):
  #Get 2000 LY cube around earth
  mongoResponse = []
  for system in collection.find(
    {
      '$and':
      [
        {
          'x':
            {
              '$gt': ( 0 - 10000 )
            }
        },
        {
          'x':
            {
              '$lt': ( 0 + 10000 )
            }
        },
        {
          'y':
            {
              '$gt': ( 0 - 10000 )
            }
        },
        {
          'y':
            {
              '$lt': ( 0 + 10000 )
            }
        },
        {
          'z':
            {
              '$gt': ( 0 - 10000 )
            }
        },
        {
          'z':
            {
              '$lt': ( 0 + 10000 )
            }
          }
        ]
      } 
    ):
    mongoResponse.append(system)  
#print len(mongoResponse)
locationEnd = time.time()
print locationEnd - locationStart
print (locationEnd - locationStart)/tests

print "Mongo: Getting test systems by name"
bynameStart = time.time()
for x in range(0, tests):
  #Get testSystems by name
  for system in testSystems:
    test = collection.find( {'name': system})
    for response in test:
      blah = response
bynameEnd = time.time()
print bynameEnd - bynameStart
print (bynameEnd - bynameStart)/tests

print "Mongo: testing autocomplete"
autoStart = time.time()
for x in range(0, tests):
  #full text testing
  characters = list(testSystems[0])
  for index, item in enumerate(characters):
    if index > -1:
      searchString = "".join(list(testSystems[0])[:index+1]) + ".*"
      test = collection.find({ 'name': {'$regex': searchString} })
      for response in test:
        blah = response
autoEnd = time.time()
print autoEnd - autoStart
print (autoEnd - autoStart)/tests

elk_host = Elasticsearch('localhost', sniff_on_start=True, request_timeout=600)
esIndex = "route_finder"

print "ES: Getting all systems within 2000LY of Earth."
locationStart = time.time()
for x in range(0, tests):
  res = elk_host.search(
    index=esIndex,
    size=500000,
    body={
      'query' : {
        'filtered' : {
          'query' : {
            'match' : { "_type" : "system" }
          },
          'filter' : {
            'bool' : {
              'must': [
                { 'range' : { 'x':  { "gte" : 0 - 1000 } } },
                { 'range' : { 'x':  { "lte" : 0 + 1000 } } },
                { 'range' : { 'y':  { "gte" : 0 - 1000 } } },
                { 'range' : { 'y':  { "lte" : 0 + 1000 } } },
                { 'range' : { 'z':  { "gte" : 0 - 1000 } } },
                { 'range' : { 'z':  { "lte" : 0 + 1000 } } }
              ]
            }
          }
        }
      }
    }
  )
locationEnd = time.time()
print locationEnd - locationStart
print (locationEnd - locationStart)/tests
#print len(res['hits']['hits'])

print "ES: Getting test systems by name"
bynameStart = time.time()
for x in range(0, tests):
  #Get testSystems by name
  for system in testSystems:
#    test = collection.find( {'name': system})
    res = elk_host.search(
      index=esIndex,
      size=1,
      body={
        'query' : {
          'bool' : {
            'should': [
              { 'match' : { "name" : system } }
            ],
            'must': [
              { 'match' : { "_type" : "system" } }
            ]
          }
        }
      }
    )

bynameEnd = time.time()
print bynameEnd - bynameStart
print (bynameEnd - bynameStart)/tests

print "ES: testing autocomplete"
autoStart = time.time()
for x in range(0, tests):
  #full text testing
  characters = list(testSystems[0])
  for index, item in enumerate(characters):
    if index > -1:
      searchString = "".join(list(testSystems[0])[:index+1])

      res = elk_host.search(
        index=esIndex,
        size=10,
        body={
          'query' : {
            'bool' : {
              'should' : [
                { 'match_phrase_prefix' : { 'name' : searchString } }
              ],
              'must' : [
                { 'match' : { '_type' : 'system' } }
              ]
            }
          }
        }
      )
      #pprint(res)
      #test = collection.find({ 'name': {'$regex': searchString} })
      for response in test:
        blah = response
autoEnd = time.time()
print autoEnd - autoStart
print (autoEnd - autoStart)/tests


exit()










