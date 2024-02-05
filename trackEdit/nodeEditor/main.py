#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Oct 13 13:44:28 2023

@author: rachel
"""

import sys
from dask.array.image import imread as imr
import numpy as np
from node_editor_window import *


homeFolder = '/media/rachel/9d56c1ff-e031-4e35-9f3c-fcd7d3e80033/Analysis/20230720/'
nameKey = 'Hela_h9_h2_k11_mcpsg_1hrbasal_14hr_10ng.ml_tnf_exp1_4_F'

imsQ = '11'
moviePath = homeFolder+nameKey+imsQ+'/'
cellNumber = 1
pathToTimeFramesCell = homeFolder+nameKey+imsQ+'/cell_'+str(cellNumber)+'/*.tif'
stackCell = imr(pathToTimeFramesCell)
maxImageCell = np.max(stackCell, axis=1)



npzfile = np.load('/media/rachel/9d56c1ff-e031-4e35-9f3c-fcd7d3e80033/Analysis/20230720/Hela_h9_h2_k11_mcpsg_1hrbasal_14hr_10ng.ml_tnf_exp1_4_F11/cellNumber_1trackData.npz', allow_pickle=True)

clustersFrames = npzfile[npzfile.files[-2]]
spcl = np.load(homeFolder+nameKey+imsQ+'/cell_'+str(cellNumber)+'/'+str(cellNumber)+'_spots_and_clusters.npz',allow_pickle=True)

spotsFrame = spcl['spotsFrame']#[450:460,]
clustersBigfish = spcl['clustersFrames']
pts_coordinates = spotsFrame
cluster_coordinate = clustersFrames

napariBox = setNapari(maxImageCell, spotsFrame, pts_coordinates, cluster_coordinate, clustersBigfish)
# napariBox.flood_widget.onFileNewFromTracks()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    # wnd = NodeEditorWindow()
    
    ex = App()
    # sys.exit(app.exec_())
try:
    sys.exit(app.exec())
except:
    print("Exiting")

