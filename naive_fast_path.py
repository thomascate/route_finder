#!/usr/bin/env python
import numpy
import json
from pprint import pprint
import random

systemsFile = open("systems.json")
rareSystemsFile = open("systems")

systems = json.loads(systemsFile.read())
rareSystems = rareSystemsFile.read().split('\n')

for index, system in enumerate(rareSystems):
  rareSystems[index] = unicode(system)

for system in systems:
  if system['name'] == unicode("Achenar"):
    startSystem = system
    startLocation = numpy.array([startSystem['x'],startSystem['y'],startSystem['z']])
    endSystem = system
    endLocation = numpy.array([endSystem['x'],endSystem['y'],endSystem['z']])

targetSystems = []
for rareSystem in rareSystems:
  for system in systems:
    if system['name'] == rareSystem:
      curLocation = numpy.array([system['x'],system['y'],system['z']])
      startRange = numpy.linalg.norm(startLocation-curLocation)
      endRange = numpy.linalg.norm(endLocation-curLocation)
      if startRange > 200 and endRange > 200:
        targetSystems.append( system )


finalSystems = [ startSystem ]
curLocation = numpy.array([startSystem['x'],startSystem['y'],startSystem['z']])

destSystems = list(targetSystems)
totalRange = 0
for item in targetSystems:

  bestRange = 0
  for index, system in enumerate(destSystems):
    nextLocation = numpy.array([system['x'],system['y'],system['z']])
    curRange = numpy.linalg.norm(nextLocation-curLocation)
    if curRange < bestRange or bestRange == 0:
      bestRange = curRange
      nextHop = system
      delIndex = index

  del destSystems[delIndex]
  finalSystems.append(nextHop)
  print ( "{:15}\t\t\t\t{:.2f}".format(nextHop['name'], bestRange) )
  curLocation = numpy.array([nextHop['x'],nextHop['y'],nextHop['z']])
  totalRange += bestRange

curRange = numpy.linalg.norm(endLocation-curLocation)
print ( "{:15}\t\t\t\t{:.2f}".format(endSystem['name'], curRange) )
totalRange += curRange
print totalRange
exit()
