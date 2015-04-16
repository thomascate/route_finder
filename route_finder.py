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

bestRange = 0

for x in range(0, 10000000):
  totalRange = 0
  randTargetSystems = list(targetSystems)
  random.shuffle(randTargetSystems,random.random)
  randTargetSystems.append(startSystem)
  randTargetSystems.reverse()
  randTargetSystems.append(endSystem)
  
  for index, system in enumerate(randTargetSystems):
    curLocation = numpy.array([system['x'],system['y'],system['z']])
    if index < len(randTargetSystems) - 1:
      nextLocation = numpy.array([randTargetSystems[index+1]['x'],randTargetSystems[index+1]['y'],randTargetSystems[index+1]['z']])
      curRange = numpy.linalg.norm(nextLocation-curLocation)
      totalRange += curRange

  if totalRange < bestRange or bestRange == 0:
    bestRange = totalRange
    bestRoute = list(randTargetSystems)

    for index, system in enumerate(bestRoute):
      curLocation = numpy.array([system['x'],system['y'],system['z']])
      if index < len(bestRoute) - 1:
        nextLocation = numpy.array([bestRoute[index+1]['x'],bestRoute[index+1]['y'],bestRoute[index+1]['z']])
        curRange = numpy.linalg.norm(nextLocation-curLocation)
        totalRange += curRange
        print ( "{:15}\t\t\t\t{:.2f}".format(system['name'], curRange) )

    print "Achenar"
    print bestRange
    print ""

exit()
