#!/usr/bin/env python
from elasticsearch import Elasticsearch
from elasticsearch import helpers
import json
import simplejson
import ujson
from pprint import pprint
import pymongo
import re
import time
from pyes import *
import requests




conn = ES('127.0.0.1:9200')

q = {
    'query' : {
    'filtered' : {
      'query' : {
        'match' : { "_type" : "system" }
      },
      'filter' : {
        'bool' : {
          'must': [
            { 'range' : { 'x':  { "gte" : -100 } } },
            { 'range' : { 'x':  { "lte" : 100 } } },
            { 'range' : { 'y':  { "gte" : -100 } } },
            { 'range' : { 'y':  { "lte" : 100 } } },
            { 'range' : { 'z':  { "gte" : -100 } } },
            { 'range' : { 'z':  { "lte" : 100 } } }
          ]
        }
      }
    }
  },
  'size': 1000000,
  'fields': [ 'name', 'x', 'y', 'z' ]
}

locationStart = time.time()
print json.dumps(q)

r = requests.post('http://localhost:9200/route_finder/_search', data = json.dumps(q) )
locationEnd = time.time()
print "time in elasticsearch"
print locationEnd - locationStart

print "responses found"
print len(json.loads(r.content)['hits']['hits'])
locationEnd = time.time()
print "time in built in json"
print locationEnd - locationStart

locationStart = time.time()

print len(simplejson.loads(r.content)['hits']['hits'])
locationEnd = time.time()
print "time in simplejson"
print locationEnd - locationStart

locationStart = time.time()

print len(ujson.loads(r.content)['hits']['hits'])
locationEnd = time.time()
print "time in ujson"
print locationEnd - locationStart

locationStart = time.time()

pyres = conn._send_request('POST', 'route_finder/_search', json.dumps(q) )

print type(pyres)

locationEnd = time.time()
print locationEnd - locationStart

elk_host = Elasticsearch('localhost', sniff_on_start=True, request_timeout=600)
esIndex = "route_finder"

print "ES: Getting all systems within 2000LY of Earth."
locationStart = time.time()
res = elk_host.search(
  index=esIndex,
  size=1000000,
  body={
    'query' : {
      'filtered' : {
        'query' : {
          'match' : { "_type" : "system" }
        },
        'filter' : {
          'bool' : {
            'must': [
              { 'range' : { 'x':  { "gte" : -100 } } },
              { 'range' : { 'x':  { "lte" : 100 } } },
              { 'range' : { 'y':  { "gte" : -100 } } },
              { 'range' : { 'y':  { "lte" : 100 } } },
              { 'range' : { 'z':  { "gte" : -100 } } },
              { 'range' : { 'z':  { "lte" : 100 } } }
            ]
          }
        }
      }
    },
    'fields': [ 'name', 'x', 'y', 'z' ]
  }
)
print type(res)
locationEnd = time.time()
print locationEnd - locationStart
#print len(res['hits']['hits'])


exit()










