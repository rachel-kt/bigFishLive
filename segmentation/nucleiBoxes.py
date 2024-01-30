
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
import matplotlib.pyplot as plt

def getNucleiCoordinates(maskPath, shouldIplot=False):
    image = io.imread(maskPath)
    label_img = label(image)
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

def cropNuclei(moviePath, maskPath, nucNumber=1,tillTime=25, extensionMov='.tiff'):
    imageName = moviePath.split('/')[-2]
    nuclei = nucNumber
    maxTime = tillTime
    cellTimeSeriesPath = os.path.join(moviePath, 'cell_'+str(nuclei))
    if not os.path.exists(cellTimeSeriesPath):
        os.makedirs(cellTimeSeriesPath)
        for t in range(maxTime):
            cropBoxCoordinates, centroids, noNuclei = getNucleiCoordinates(maskPath, False)
            fileExtTime = '_t'+str(f"{t:03}")+extensionMov
            cellExt = '_cell_'+str(nuclei)+'_t'+str(f"{t:03}")+extensionMov
            image = io.imread(os.path.join(moviePath,imageName+fileExtTime))
            nucIdx = np.where(noNuclei==nuclei)[0]
            bx = np.asarray(cropBoxCoordinates[nucIdx[0]][0])
            by = np.asarray(cropBoxCoordinates[nucIdx[0]][1])
            bx[bx<0]=0
            bx[bx>1024]=1024
            by[by<0]=0
            by[by>1024]=1024

            B = image[:,math.floor(by[0]):math.ceil(by[2]),math.floor(bx[0]):math.ceil(bx[1])]

            sdn = np.shape(B)
            B = B.reshape(1,1,sdn[0],sdn[1],sdn[2])
            cellFileName = os.path.join(cellTimeSeriesPath,imageName+cellExt)
            with tifffile.TiffWriter(cellFileName, imagej=True) as tif:
                tif.save(B)
    else:
        print('Cell crop exits! check location below!')
        print(cellTimeSeriesPath)
    return cellTimeSeriesPath

