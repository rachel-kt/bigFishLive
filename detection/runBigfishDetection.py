# -*- coding: utf-8 -*-
"""
Created on Tue Jul 3 14:59:14 2023

@author: rachel

This function is for reading cell z stacks crops and running bigfish spot and cluster detection on each movie frame. 

Parameters
----------

1. pathTocellCrops : the path to the folder of the cell to be opened. (dir)
               type : str

2. reference_spot :


3. cellnumber : default 1. The nuclei to be used to perform the detection
               type : int
          
4. startTime  : default 0. starting Time of the series to be analysed
               type : int
       
5. stopTime  : default 2. stop Time of the series to be analysed


6. thresholdManual :


Returns
-------

1. spotsFrame  : list of numpy arrays of coordinate of the detected spots.
               type : list of numpy.array
               
2. clustersFrames : list of numpy arrays of coordinates of the detected clusters.
               type : list of numpy.array

3. ThresholdFrames : List of numpy.ndarray of automatic thresholds
               type : list of numpy.ndarray


"""


import os
import numpy as np
import matplotlib.pyplot as plt
import bigfish
import bigfish.stack as stack
import bigfish.detection as detection
import bigfish.multistack as multistack
import bigfish.plot as plot
from copy import deepcopy
from reorderStack import reorderZstack

# def normalize(img, maxI):
#     lmin =float(img.min())
#     lmax =float(img.max())
#     return np.floor((img-lmin)/(lmax-lmin)*maxI).astype('uint16')

def getSpotAndClusters(pathTocellCrops,reference_spot, cellnumber=1, startTime=0, stopTime=900, thresholdManual=50, beta=1, gamma=1,numberOfSpots=2, radiusCluster=400, voxelSize=(600,121,121), objectSize=(400,202,202), reorder=False, extensionMov='.tif'):
    cell = cellnumber
    spotsFrame = []
    ThresholdFrames = []
    clustersFrames = []
    #referenceSpots = []
    denseRegions = []
    #reference_spot_previous=[]
    #reference_spot_previous = np.asarray(reference_spot_previous)
    path_input = pathTocellCrops
    movieName = path_input.split('/')[-3]
    for t in range(startTime, stopTime):
        path = os.path.join(path_input, movieName+"_cell_"+str(cell)+'_t'+str(f"{t:03}")+extensionMov)
        rna = stack.read_image(path)
        if reorder:
            rna = reorderZstack(rna,4)
        #rna = normalize(rna,6000)
        rna_mip = stack.maximum_projection(rna)
        
        # spot radius
        spot_radius_px = detection.get_object_radius_pixel(
            voxel_size_nm=voxelSize,#(600, 80, 80), 
            object_radius_nm=objectSize, 
            ndim=3)
        
        # LoG filter
        rna_log = stack.log_filter(rna, sigma=spot_radius_px)

        # local maximum detection
        mask = detection.local_maximum_detection(rna_log, min_distance=spot_radius_px)

        # thresholding
        threshold = detection.automated_threshold_setting(rna_log, mask)
        spots_current, _ = detection.spots_thresholding(rna_log, mask, thresholdManual)

        spotsFrame.append(spots_current)
        ThresholdFrames.append(threshold)
        print(t)
        spots_post_decomposition, dense_regions, reference_spot_current = detection.decompose_dense_2(
            image=rna, 
            spots=spots_current,
            reference_spot_previous=reference_spot,
            voxel_size=voxelSize, 
            spot_radius=objectSize, 
           # alpha=alpha,  # alpha impacts the number of spots per candidate region
            beta=beta,  # beta impacts the number of candidate regions to decompose
            gamma=gamma)  # gamma the filtering step to denoise the image
        reference_spot_previous = deepcopy(reference_spot_current)
        
        #clustering
        spots_post_clustering, clusters = detection.detect_clusters(
            spots=spots_post_decomposition, 
            voxel_size=voxelSize, 
            radius=radiusCluster, 
            nb_min_spots=numberOfSpots)
        clustersFrames.append(clusters)
    print('done!')
    return spotsFrame, clustersFrames, ThresholdFrames


def saveSpotsNPZ(spotsFrame, clustersFrames, ThresholdFrames, cellName, pathTocellCrops, reference_spot):
    outfileName = os.path.join(pathTocellCrops,str(cellName)+'_spots_and_clusters')
    np.savez(outfileName, 
             spotsFrame=spotsFrame, 
             clustersFrames=clustersFrames,
             ThresholdFrames=ThresholdFrames,
             reference_spot=reference_spot) 