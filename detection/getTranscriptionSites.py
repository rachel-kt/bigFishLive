# -*- coding: utf-8 -*-
"""
Created on Tue Feb 2 10:39:14 2024

@author: rachel

"""

import pandas as pd
import numpy as np

def getTranscrtiptionSites(maxImageCell, particle_1, MaxTimePoint, spotsFrame, clustersFrames, clusterID):
    """Identify potential transcription sites based on particle coordinates.

    Parameters
    ----------
    maxImageCell : list
        List of maximum intensity projections for each time point.
    particle_1 : pandas.DataFrame
        DataFrame containing particle coordinates.
    MaxTimePoint : int
        Maximum time point in the sequence.
    spotsFrame : list
        List of detected spots at each time point.
    clustersFrames : list
        List of detected clusters at each time point.
    clusterID : int
        Identifier for the cluster.

    Returns
    -------
    pandas.DataFrame
        DataFrame containing potential transcription sites with frame, z, y, x, and mRNA columns.

    Notes
    -----
    This function identifies potential transcription sites based on particle coordinates and
    associated spot and cluster information.

    Example
    -------
    transcription_sites = getTranscriptionSites(particle_1, MaxTimePoint, spotsFrame, clustersFrames, clusterID=1)
    """
    # Function implementation...
    # ...
    potentialTxs = pd.DataFrame(np.zeros([MaxTimePoint, 1+3+1]), columns=['frame', 'z', 'y', 'x', 'mrna'])
    potentialTxs['frame']= np.arange(0,MaxTimePoint,1)
    

    for frameNumber in range(MaxTimePoint):
        t = particle_1.frame.values[np.argmin(abs(particle_1.frame.values-frameNumber))]
        particleCoordinates = np.asarray(particle_1[particle_1['frame']==t])[0][:2]
        coordinatesFound = spotsFrame[frameNumber][np.sum((spotsFrame[frameNumber][:,1:]-particleCoordinates)**2, axis=1)<=25,:]
        if coordinatesFound.size!=0:   
            if len(coordinatesFound) > 1:
                brightest = []
                for kk in range(len(coordinatesFound)):
                    brightest.append(np.array(maxImageCell[frameNumber][coordinatesFound[kk,1],coordinatesFound[kk,2]]))
                brightest = np.argmax(brightest)
                coordinatesFound = coordinatesFound[brightest].reshape((1,3))

            if len(coordinatesFound) ==1:
                potentialTxs.iloc[frameNumber,1:4] = coordinatesFound[0]
    # finding non empty frames

    txIndexes = np.where(np.sum(potentialTxs.iloc[:,1:4], axis=1)!=0)
    if np.size(txIndexes)!=0:
        txIndexes = txIndexes[0]
    
    # adding the mrna number

    for gg in txIndexes: 
        if np.sum(potentialTxs.iloc[gg,1:4])!=0:
            potentialTxs.iloc[gg,4]=1
        if clustersFrames[gg].size!=0:
            ixmin = np.argmin(np.sum((clustersFrames[gg][:,1:3] - np.array(potentialTxs.iloc[gg,2:4]))**2,axis=1))
            potentialTxs.iloc[gg,4]=clustersFrames[gg][ixmin,3]
    
    potentialTxs['cluster_id']=clusterID
    return potentialTxs