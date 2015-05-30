#!/usr/bin/env python
from functions import *
from config import *
import uuid
from pprint import pprint
import ujson as json
import requests
import signal
import sys

requestedShutdown = False

def signal_handler(signal, frame):
  print 'You pressed Ctrl+C!'
  global requestedShutdown
  requestedShutdown = True

signal.signal(signal.SIGINT, signal_handler)

while True:

  #get job
  response = requests.get( "http://elite.luddite.nl:5000/get_job" )  
  
  jobData = json.loads( response.content )  

  print "starting job with startnumber: " + str(jobData['currentNumber'])
  mypass = bruteForceSort(jobData['bestPath'],jobData['bestRange'],100000)
  data = {}  
  
  data['bestPath'] = mypass
  data['bestRange'] = getTotalRange( mypass )
  data['currentNumber'] = jobData['currentNumber']  

  response = requests.post( "http://elite.luddite.nl:5000/put_results", data = json.dumps( data ) )

  if requestedShutdown == True:
    exit()

