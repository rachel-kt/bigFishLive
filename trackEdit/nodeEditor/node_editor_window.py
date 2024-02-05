#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 25 13:48:00 2023

@author: rachel
"""

from PyQt5.QtWidgets import *
from node_editor_widget import *
from node_node import Node
import numpy as np
import napari
import os

class setNapari():
    def __init__(self, image, spotsFrame, pts_coordinates, cluster_coordinate, clusterBF):
        
        self.bfResults = clusterBF
        self.viewer = napari.Viewer()

        self.flood_widget = NodeEditorWindow(self.viewer, self.bfResults)
        self.image_layer = self.viewer.add_image(
                image, colormap='green' #maxImageCell
                )
        
        if self.image_layer.data.ndim == 4:
            self.bigfishSpots = spotsFrame
        elif self.image_layer.data.ndim == 3:
            self.bigfishSpots = self.getDetectedPointsForFrame(pts_coordinates,int((np.shape(image)[0]-1)/2))
            
        self.bigfish_Spots = self.viewer.add_points(
                self.bigfishSpots,
                face_color='#00000000',
                size=4,
                edge_width=0.3,
                edge_width_is_relative=False,
                edge_color='white',
                face_color_cycle = ['white'],
                name = 'bigFish Detected Spots'
                )
    
        self.bigfish_clusters = self.viewer.add_points(
                self.getDetectedClustersForFrame(cluster_coordinate,int(np.shape(image)[0]/2)),
                face_color='#00000000',
                size=8,
                edge_width=0.3,
                edge_width_is_relative=False,
                edge_color='red',
                face_color_cycle = ['red'],
                symbol='diamond',
                name = 'bigFish Clusters'
                )
        
        self.annotations_layer = self.viewer.add_points([],name = 'Bigfish Results')
        
        @self.viewer.bind_key('b')
        def applyAnnotations(viewer):
            currStep = list(self.viewer.dims.current_step)
            annotCoord = self.bfResults[currStep[0]][:,1:3]
            mrnaN = self.bfResults[currStep[0]][:,3]
            self.features = {
                'N': mrnaN,
                #'good_point': np.array([True, False, False]),
            }
            self.text = {
                'string': '{N:.1f}',
                'size': 8,
                'color': 'white',
                'translation': np.array([-5, 0]),
            }
            face_color_cycle = ['white']
            
            self.annotations_layer = self.viewer.add_points(
                annotCoord,
                face_color='#00000000',
                features=self.features,
                text=self.text,
                size=2,
                edge_width=2,
                edge_width_is_relative=False,
                edge_color='N',
                edge_colormap='gray',
                name = 'Bigfish Results'
            )
    
        #bigfish_TxSite = viewer.add_labels(Tx_label_clean, name='Tx Site',opacity=0.3)
    
        self.viewer.dims.events.current_step.connect(
                lambda event: self.set_pts_features(self.bigfish_Spots,self.bigfish_clusters, pts_coordinates, cluster_coordinate, event.value,self.annotations_layer, self.bfResults) # 
                )
        

        # Create instance from our class
        self.viewer.window.add_dock_widget(self.flood_widget, area='right')         
        self.flood_widget.nodeeditor.scene.grScene.itemSelected.messageSignal.connect(self.applyNodeSelection)    


    def getDetectedPointsForFrame(self, pts_coordinates, frameNumer):
        sd = np.shape(pts_coordinates[frameNumer][:])
        pts_coords = np.empty([sd[0],sd[1]-1])
        for ii in range(np.shape(pts_coordinates[frameNumer][:])[0]):
            pts_coords[ii,:] = pts_coordinates[frameNumer][ii][1:]
        return pts_coords

    def getDetectedClustersForFrame(self, pts_coordinates, frameNumer):
        sd = np.shape(pts_coordinates[frameNumer][:])
        pts_coords = np.empty([sd[0],sd[1]-3])
        for ii in range(np.shape(pts_coordinates[frameNumer][:])[0]):
            pts_coords[ii,:] = pts_coordinates[frameNumer][ii][1:3]
        return pts_coords

    def getBFResults(self, clustercds, frameNumber):
        annotCoord = clustercds[frameNumber][:,1:3]
        mrnaN = clustercds[frameNumber][:,3]
        return annotCoord, mrnaN
    
    def set_pts_features(self, pts_layer,cls_layer, pts_coordinates, cluster_coordinate, step, ants_layer, bfclustercds): 
        # step is a 4D coordinate with the current slider position for each dim
        frameNumber = step[0]  # grab the leading ("time") coordinate
        pts_layer.data = self.getDetectedPointsForFrame(pts_coordinates,frameNumber)
        cls_layer.data = self.getDetectedClustersForFrame(cluster_coordinate,frameNumber)
        annotdata, mrnaNumber = self.getBFResults(bfclustercds, frameNumber)
        ants_layer.data = annotdata
        ants_layer.features = {
            'N': mrnaNumber,
        }
        
        # pts_layer.selected_data = set([])
        # cls_layer.selected_data = set([])


    def applyNodeSelection(self, tcoord, xcoord):
        print('Currrent step:', self.viewer.dims.current_step)
        tempTup = self.viewer.dims.current_step
        tempTupList = list(tempTup)
        tempTupList[0] = tcoord
        if len(self.viewer.layers[2].data)==2:
            if xcoord == -300:
                clid=1
            elif xcoord== -500:
                clid=0
            self.viewer.layers[2].selected_data = set([clid])
        else:
            self.viewer.layers[2].selected_data = set([0])
        self.viewer.dims.current_step = tuple(tempTupList)
        print('Updated step:', self.viewer.dims.current_step)
    


class NodeEditorWindow(QMainWindow):
    def __init__(self, napari_viewer, bfRes): #napari_viewer
        super().__init__()
        self.viewer = napari_viewer
        self.bfResults = bfRes
        self.initUI()
        self.filename = None

        
    def createAct(self, name, shortcut, tooltip, callback):
        act = QAction(name, self)
        act.setToolTip(tooltip)
        act.setShortcut(shortcut)
        act.triggered.connect(callback)
        return act
        
    def initUI(self):
        menubar = self.menuBar()
        
        # inititalise Menu
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(self.createAct('&New', 'Ctrl+N', "Create New Graph", self.onFileNew))
        fileMenu.addAction(self.createAct('Create from &Trackfile', 'Ctrl+T', "Create New Graph from Track data", self.onFileNewFromTracks))
        fileMenu.addSeparator()
        fileMenu.addAction(self.createAct('&Open', 'Ctrl+N', "Open New Graph", self.onFileOpen))
        fileMenu.addAction(self.createAct('&Save', 'Ctrl+S', "Save Graph", self.onFileSave))
        fileMenu.addAction(self.createAct('Save &As..', 'Ctrl+Shift+S', "Save Graph As", self.onFileSaveAs))
        fileMenu.addSeparator()
        fileMenu.addAction(self.createAct('&Quit', 'Ctrl+Q', "Quit Application", self.close))
        
        editMenu = menubar.addMenu('&Edit')
        editMenu.addAction(self.createAct('&Undo', 'Ctrl+Z', "Undo Last", self.onEditUndo))
        editMenu.addAction(self.createAct('&Redo', 'Ctrl+Shift+Z', "Redo Last", self.onEditRedo))
        editMenu.addAction(self.createAct('Add &Node', 'Ctrl+A', "Add Node to Selected Point", self.onAddNodeToSelection))
        
        # featureMenu = menubar.addMenu('Features')
        # featureMenu.addAction(self.createAct('Show bigfish results', 'Ctrl+B', "View BF results", self.onShowBFResults))
        
        
        self.xpos = 500
        self.ypos = 45400
        self.frameLabelPos = []
        for i in range(900):
            self.frameLabelPos.append([i, -self.xpos,-self.ypos+i*100])           
        self.frameLabelPos = np.array(self.frameLabelPos)

        self.nodeeditor = NodeEditorWidget(self)
        self.setCentralWidget(self.nodeeditor)



        # Status Bar
        self.statusBar().showMessage("")
        self.status_mouse_pos = QLabel("")
        self.statusBar().addPermanentWidget(self.status_mouse_pos)
        self.nodeeditor.view.scenePosChanged.connect(self.onSceneChanged)
        
        

        
        # set window properties
        self.setGeometry(0,0, 700, 1000)
        self.setWindowTitle("Track Editor")
        self.show()

    def onSceneChanged(self, x, y):
        self.status_mouse_pos.setText("Scene Pos: [%d, %d]" % (x, y))


    def onFileNew(self):
        self.centralWidget().scene.clear()
        
    def onFileNewFromTracks(self):
        print("Get track File")
        self.centralWidget().scene.clear()
        trackfile = '/home/rachel/single/hela_K11_ON-_F_particle_1.csv'
        
        npzfile = np.load('/media/rachel/9d56c1ff-e031-4e35-9f3c-fcd7d3e80033/Analysis/20230720/Hela_h9_h2_k11_mcpsg_1hrbasal_14hr_10ng.ml_tnf_exp1_4_F11/cellNumber_1trackData.npz', allow_pickle=True)
        no_of_tracks = len(npzfile)-2
        self.clusterFrames = npzfile[npzfile.files[-2]]

        for txsites in range(no_of_tracks):
            self.trackData = npzfile[npzfile.files[txsites]]
            self.totalNumberOfFrames = len(self.trackData)
            self.nodeFrames = np.where(self.trackData[:,4]!=0)[0]
            self.xpos = 500
            self.ypos = 45400
            self.frameLabelPos = []
            self.lastXpos = -self.xpos+txsites*200
            for i in range(self.totalNumberOfFrames):
                self.frameLabelPos.append([i, -self.xpos+txsites*200,-self.ypos+i*100])
                
            self.frameLabelPos = np.array(self.frameLabelPos)
            self.nodePositions = self.frameLabelPos[self.nodeFrames]
            self.nodeeditor.addNodes(nodePositions=self.nodePositions)

        # self.numberOfTracks = 1
        # self.trackData = np.genfromtxt(trackfile, delimiter=',', skip_header=1)
        # self.totalNumberOfFrames = len(self.trackData)
        # self.nodeFrames = np.where(self.trackData[:,2]!=0)[0]

        # self.xpos = 500
        # self.ypos = 45400
        
        # self.frameLabelPos = []
        # for i in range(self.totalNumberOfFrames):
        #     self.frameLabelPos.append([i, -self.xpos,-self.ypos+i*100])
            
        # self.frameLabelPos = np.array(self.frameLabelPos)
        
        # self.nodePositions = self.frameLabelPos[self.nodeFrames]
        
        

        
    def onFileOpen(self):
        fname, _ = QFileDialog.getOpenFileName(self, "Open graph from file ",options=QFileDialog.DontUseNativeDialog)
        if fname == '':
            return
        if os.path.isfile(fname):
            self.centralWidget().scene.loadFromFile(fname)

    def onFileSave(self):
        if self.filename is None: return self.onFileSaveAs()
        self.centralWidget().scene.saveToFile(self.filename)
        self.statusBar().showMessage("Successfully saved %s" % self.filename)
        print("On file save")

    def onFileSaveAs(self):
        fname, filter_ = QFileDialog.getSaveFileName(self, "Save graph to file",options=QFileDialog.DontUseNativeDialog)
        if fname == "":
            return
        self.filename  = fname
        self.onFileSave()
        
        print("On file saveas")

    def onEditUndo(self):
        print("On Undo")
        
    def onEditRedo(self):
        print("On Redo")
    
    def onAddNodeToSelection(self):
        print("Selected Node :")
        # print(self.viewer.layers[1].data[list(self.viewer.layers[1].selected_data)[0]])
        currStep = list(self.viewer.dims.current_step)
        # print('current step = ',currStep[0])
        self.newNodeToAdd = self.frameLabelPos[currStep[0]]
        self.newNodeToAdd[1] = self.lastXpos+200
        print(self.newNodeToAdd.reshape([1,3]))
        self.nodeeditor.addNodes(self.newNodeToAdd.reshape([1,3]))
        
