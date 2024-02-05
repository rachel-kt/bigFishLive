#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Nov 30 13:43:22 2023

@author: rachel
"""

import numpy as np
numberOfTracks = 1
trackfile = '/home/rachel/single/hela_K11_ON-_F_particle_1.csv'
trackData = np.genfromtxt(trackfile, delimiter=',', skip_header=1)

nodeFrames = np.where(trackData[:,2]!=0)[0]

totalNumberOfFrames = len(trackData)

xpos = 300
ypos = 45400
frameLabelPos = []

for i in range(totalNumberOfFrames):
    frameLabelPos.append([i, -xpos,-ypos+i*100])
    
frameLabelPos = np.array(frameLabelPos)
nodePositions = frameLabelPos[nodeFrames]
