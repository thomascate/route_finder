#!/usr/bin/env python
from functions import *
from config import *
import uuid
from pprint import pprint
import ujson as json
from flask import Flask
from flask import request
import logging

#logging.basicConfig(filename='error.log',level=logging.DEBUG)

#Just stupidly count up through all options
goodStars = getSystemList()

print "finding closest next hop for each star"
#first do a naive fast path to get these systems into an ok order
pass1 = naiveFastSort(goodStars)
bestRange = getTotalRange( pass1 )
data = {}
data['bestPath'] = pass1
data['bestRange'] = bestRange
data['currentNumber'] = 0

FH = open('current.json', 'w')
FH2 = open('best.json', 'w')
FH.write( json.dumps( data ) )
FH2.write( json.dumps( data ) )
FH.close()
FH2.close()

app = Flask(__name__)

@app.route('/get_job', methods=['GET'])
def send_job():
  FH = open('current.json', 'r')
  data = json.loads( FH.read() )
  FH.close()
  returnData = data.copy()
  if data['currentNumber'] > 0:
    startSystem = data['bestPath'][0]
    endSystem = data['bestPath'][-1]
    del data['bestPath'][0]
    del data['bestPath'][-1]
    data['bestPath'] = list(next(itertools.islice(itertools.permutations(data['bestPath']), data['currentNumber']-1, data['currentNumber'])))
    data['bestPath'].insert(0,startSystem)
    data['bestPath'].append(endSystem)


  data['currentNumber'] += 100000
  data['bestRange'] = getTotalRange( data['bestPath'] )

  FH = open('current.json', 'w')
  FH.write (json.dumps(data))
  FH.close()

  return json.dumps(returnData)

@app.route('/put_results', methods=['POST'])
def recieve_results():
  clientData = request.get_json(force=True)
  FH = open('best.json', 'r')
  data = json.loads( FH.read() )
  FH.close()

  if clientData['bestRange'] < data['bestRange']:
    clientData['currentNumber'] = data['currentNumber']
    FH = open('best.json', 'w')
    FH.write (json.dumps(clientData))
    FH.close()

  return "received"

if __name__ == '__main__':
  app.run(host='0.0.0.0')

