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

while True:

  try:

    #get job
    response = requests.get( "http://localhost:5000/get_job" )  
  
    jobData = json.loads( response.content )  
      
    print "starting job with startnumber: " + str(jobData['currentNumber'])
    mypass = bruteForceSort(jobData['bestPath'],jobData['bestRange'],100000)
    data = {}  
  
    data['bestPath'] = mypass
    data['bestRange'] = getTotalRange( mypass )
    data['currentNumber'] = jobData['currentNumber']  

    response = requests.post( "http://localhost:5000/put_results", data = json.dumps( data ) )

    if requestedShutdown == True:
      break

  except (KeyboardInterrupt, SystemExit):
    requestedShutdown = True
    print "shutting down once current pass finishes"
