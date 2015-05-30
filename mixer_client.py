#!/usr/bin/env python
from functions import *
from config import *
import uuid
from pprint import pprint
import ujson as json
import requests
import signal
import sys
import random

requestedShutdown = False

def signal_handler(signal, frame):
  print 'You pressed Ctrl+C!'
  global requestedShutdown
  requestedShutdown = True

signal.signal(signal.SIGINT, signal_handler)

while True:

  #get job, don't increment counter since we're not going to do normal incrementing
  #these guys are just hammering on random and swaps to get a best match faster
  response = requests.get( "http://elite.luddite.nl:5000/get_best" )  
  jobData = json.loads( response.content )

  diceRoll = random.randrange(1,3)
  if diceRoll == 1:
    mypath = randSort(jobData['bestPath'],jobData['bestRange'],100000)
  else:
    mypath = swapSort(jobData['bestPath'],jobData['bestRange'],100000)

  data = {}
  
  data['bestPath'] = mypath
  data['bestRange'] = getTotalRange( mypath )
  data['currentNumber'] = jobData['currentNumber']  

  response = requests.post( "http://elite.luddite.nl:5000/put_results", data = json.dumps( data ) )

  if requestedShutdown == True:
    exit()
