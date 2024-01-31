
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 14 17:18:14 2023

@author: rachel

This function is for reading image masks and obtaining coordinates of individual nuclei in a movie frame. 

Parameters
----------

1. maskPath : the whole path of the image to be opened. (dir+filename)
               type : str
                
2. shouldIplot : default False. To plot the mask along with centroid and crop box around each nuclei 
               type : Boolean

Returns
-------

1. cropBoxCoordinates : list of coordinate of the crop box
               type : list
               
2. nucleiCentroids : list of [x,y] coordinates of the centroid of each cell
               type : list

3. noNuclei : numpy.ndarray of nuclei labels
               type : numpy.ndarray


"""

from skimage.measure import label, regionprops
from skimage import io, data
import numpy as np
import math
import os
import tifffile
from cellpose.utils import remove_edge_masks
import numpy.ma as ma

import matplotlib.pyplot as plt

def getBackgroundTimeProfile(path_input, nameKey, imsQ, minc, minr, maxc, maxr, start=0, stop=0, extensionF='.tif'):
    imagePath = path_input
    maxTimePoint=stop
    meanofRandomImageSample = []
    timePoint = start
    nucleiStackName = nameKey+imsQ+'_t'+str(f"{timePoint:03}")+extensionF
    nucleiStackPath = os.path.join(imagePath, nucleiStackName) 
    newimage = io.imread(nucleiStackPath)
    imageShape = np.shape(newimage)
    projectionNuclei = np.max(newimage, axis=0)
    cropBoxForIntensity = projectionNuclei[minr:maxr,minc:maxc]
    imageSampleMean = np.mean(cropBoxForIntensity)
    meanofRandomImageSample.append(imageSampleMean)
    for ii in range(timePoint, maxTimePoint):
        timePoint = ii
        nucleiStackName =  nameKey+imsQ+'_t'+str(f"{timePoint:03}")+extensionF
        nucleiStackPath = os.path.join(imagePath, nucleiStackName)     
        newimage = io.imread(nucleiStackPath)
        projectionNuclei = np.max(newimage, axis=0)
        cropBoxForIntensity = projectionNuclei[minr:maxr,minc:maxc]
        imageSampleMean = np.mean(cropBoxForIntensity)
        meanofRandomImageSample.append(imageSampleMean)  
    return meanofRandomImageSample



def getNucleiCoordinates(maskPath, shouldIplot=False):

    """
    This function is for reading image masks and obtaining coordinates of individual nuclei in a movie frame. 

    Parameters
    ----------

    1. maskPath : the whole path of the image to be opened. (dir+filename)
           type : str

    2. shouldIplot : default False. To plot the mask along with centroid and crop box around each nuclei 
           type : Boolean

    Returns
    -------

    1. cropBoxCoordinates : list of coordinate of the crop box
           type : list

    2. nucleiCentroids : list of [x,y] coordinates of the centroid of each cell
           type : list

    3. noNuclei : numpy.ndarray of nuclei labels
           type : numpy.ndarray

    4. orientations :


    """
    image = io.imread(maskPath)
    label_img = label(image)
    label_img = remove_edge_masks(label_img, change_index=True)
    regions = regionprops(label_img)
    noNuclei = np.unique(label_img)
    noNuclei = np.delete(noNuclei,0)
    if shouldIplot==True:
        fig, ax = plt.subplots()
        ax.imshow(image, cmap=plt.cm.gray)
    cropBoxCoordinates = []
    nucleiCentroids = []
    orientations = []
    kk=0
    for props in regions:
        y0, x0 = props.centroid
        orientation = props.orientation
        x1 = x0 + math.cos(orientation) * 0.5 * props.axis_minor_length
        y1 = y0 - math.sin(orientation) * 0.5 * props.axis_minor_length
        x2 = x0 - math.sin(orientation) * 0.5 * props.axis_major_length
        y2 = y0 - math.cos(orientation) * 0.5 * props.axis_major_length
        if shouldIplot==True:           
            ax.plot((x0, x1), (y0, y1), '-r', linewidth=.7)
            ax.plot((x0, x2), (y0, y2), '-r', linewidth=.7)
            ax.plot(x0, y0, '.g', markersize=15)  
        minr_, minc_, maxr_, maxc_ = props.bbox
        maxcc = np.max([abs(minr_-maxr_),abs(minc_-maxc_)])
        minr = minr_-0.1*maxcc
        minc = minc_-0.1*maxcc
        maxr = maxr_+0.1*maxcc
        maxc = maxc_+0.1*maxcc
        bx = (minc, maxc, maxc, minc, minc)
        by = (minr, minr, maxr, maxr, minr)
        if shouldIplot==True:            
            ax.plot(bx, by, '-b', linewidth=.7)
            ax.text(x0,y0,noNuclei[kk], color='white')

        nucleiCentroids.append([y0,x0])
        cropBoxCoordinates.append([bx,by])
        orientations.append([x1,y1,x2,y2])
        kk=kk+1
    if shouldIplot==True: 
        ax.axis((0, 1024, 1024, 0))
    plt.show()
    return cropBoxCoordinates, nucleiCentroids, noNuclei, orientations

def getTimeProfile(path_input,nucleiStackForm, cellNumber, label_image_name, labeldf, start=0, stop=0, extensionF='.tif'):
    label_image = io.imread(label_image_name)
    label_image = remove_edge_masks(label_image, change_index=True)
    nuclei=np.int64(cellNumber)
    nucIdx = np.where(labeldf['label']==np.int64(nuclei))
    minr = labeldf.loc[nucIdx]['minr'].values[0]
    minc = labeldf.loc[nucIdx]['minc'].values[0]
    sizex = np.int64(labeldf.loc[nucIdx]['sizex'].values[0])
    sizey = np.int64(labeldf.loc[nucIdx]['sizey'].values[0])
    nucleiMask = label_image[math.floor(minr):math.floor(minr)+sizex,math.floor(minc):math.floor(minc)+sizey]
    
    
    maskNum = nuclei
    imagePath = path_input
    meanofRandomImageSample_within = []
    meanofRandomImageSample_outside = []

    timePoint = start
    maxTimePoint = stop
    nucleiStackName =  nucleiStackForm+str(nuclei)+'_t'+str(f"{timePoint:03}")+extensionF
    nucleiStackPath = os.path.join(imagePath, nucleiStackName) 
    newimage = io.imread(nucleiStackPath)
    imageShape = np.shape(newimage)
    projectionNuclei = np.max(newimage, axis=0)
    withinNuc = ma.masked_where(nucleiMask!=maskNum, projectionNuclei)
    outsideNuc =  ma.masked_where(nucleiMask==maskNum, projectionNuclei)
    imageSampleMean_within = np.mean(withinNuc)
    imageSampleMean_outside = np.mean(outsideNuc)
    meanofRandomImageSample_within.append(imageSampleMean_within)
    meanofRandomImageSample_outside.append(imageSampleMean_outside)

    for ii in range(timePoint,maxTimePoint):
        timePoint = ii
        nucleiStackName =  nucleiStackForm+str(nuclei)+'_t'+str(f"{timePoint:03}")+extensionF
        nucleiStackPath = os.path.join(imagePath, nucleiStackName)     
        newimage = io.imread(nucleiStackPath)
        imageShape = np.shape(newimage)
        projectionNuclei = np.max(newimage, axis=0)
        withinNuc = ma.masked_where(nucleiMask!=maskNum, projectionNuclei)
        outsideNuc =  ma.masked_where(nucleiMask==maskNum, projectionNuclei)
        imageSampleMean_within = np.mean(withinNuc)
        imageSampleMean_outside = np.mean(outsideNuc)
        meanofRandomImageSample_within.append(imageSampleMean_within)
        meanofRandomImageSample_outside.append(imageSampleMean_outside)   

    return meanofRandomImageSample_within, meanofRandomImageSample_outside

