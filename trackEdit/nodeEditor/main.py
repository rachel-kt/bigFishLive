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

imsQ = '10'
moviePath = homeFolder+nameKey+imsQ+'/'
cellNumber = 1
pathToTimeFramesCell = homeFolder+nameKey+imsQ+'/cell_'+str(cellNumber)+'/*.tif'
stackCell = imr(pathToTimeFramesCell)
maxImageCell = np.max(stackCell, axis=1)

npzfile = np.load(moviePath+'/cellNumber_1trackData.npz', allow_pickle=True)

clustersFrames = npzfile[npzfile.files[-2]]
spcl = np.load(homeFolder+nameKey+imsQ+'/cell_'+str(cellNumber)+'/'+str(cellNumber)+'_spots_and_clusters.npz',allow_pickle=True)

spotsFrame = spcl['spotsFrame']
clustersBigfish = spcl['clustersFrames']
pts_coordinates = spotsFrame

napariBox = setNapari(maxImageCell, spotsFrame, pts_coordinates, clustersFrames, clustersBigfish)
napariBox.flood_widget.onFileNewFromTracks()

# if __name__ == '__main__':
#     app = QApplication(sys.argv)
#     # MainWindow = napariBox.flood_widget.MainWindow
#     sys.exit(app.exec())
#     napariBox.viewer.close_all()
#     # wnd = NodeEditorWindow()
    
#     # ex = App()
#     # sys.exit(app.exec_())
# # try:
    
# # except:
#     # print("Exiting")

