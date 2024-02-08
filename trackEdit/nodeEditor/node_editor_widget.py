#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Oct 13 15:51:15 2023

@author: rachel
"""

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from node_scene import Scene
from node_node import Node
#from node_socket import Socket
from node_edge import Edge
from node_graphics_view import QDMGraphicsView



class NodeEditorWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        
        self.initUI()
        
    def initUI(self):
        
        
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        
        # create graphics scene
        self.scene = Scene()
        #self.grScene = self.scene.grScene
        self.defaultNodes = None
        
        self.addNodes(self.defaultNodes)
        
        
        # create graphics veiw
        self.view = QDMGraphicsView(self.scene.grScene, self)
        self.layout.addWidget(self.view)
        
        
        
    
    def addNodes(self, nodePositions):
        if nodePositions is not None:          
            nodesFromData = []
            self.newNodes = nodePositions
            for iii in range(len(nodePositions)):#len(nodePositions)):
                nodesFromData.append(Node(self.scene, "ID 10"+format(self.newNodes[iii,0], '03d'), inputs=[1], outputs=[2]))
                nodesFromData[iii].setPos(self.newNodes[iii,1],self.newNodes[iii,2])
                
                
            newEdges = []
            for iii in range(len(nodePositions)-1):
                newEdges.append(Edge(self.scene, nodesFromData[iii].outputs[0], nodesFromData[iii+1].inputs[0], edge_type=2))
                
        else:
            xpos = self.scene.grScene.start_xpos*(-1) + 200
            ypos = 600            
            node1 = Node(self.scene, "ID 10025", inputs=[1], outputs=[2])
            node2 = Node(self.scene, "ID 10026", inputs=[1], outputs=[2])
            node3 = Node(self.scene, "ID 10027", inputs=[1], outputs=[2])
            node4 = Node(self.scene, "ID 10028", inputs=[1], outputs=[2])
            
            node1.setPos(xpos+0,-ypos+100*1)
            node2.setPos(xpos+200,-ypos+100*2)
            node3.setPos(xpos+200,-ypos+100*3)
            node4.setPos(xpos+0,-ypos+100*4)
            
            edge1 = Edge(self.scene, node1.outputs[0], node2.inputs[0], edge_type=2)
            edge2 = Edge(self.scene, node2.outputs[0], node3.inputs[0], edge_type=2)
            edge3 = Edge(self.scene, node3.outputs[0], node4.inputs[0], edge_type=2)

        
        
        
    # def addDebugContent(self):
    #     greenBrush = QBrush(Qt.green)
    #     outlinePen = QPen(Qt.black)
    #     outlinePen.setWidth(1.5)
    #     rect = QGraphicsRectItem(-100, -100, 80, 50) 
    #     rect.setBrush(greenBrush)
    #     rect.setPen(outlinePen)
    #     rect.setFlag(QGraphicsItem.ItemIsMovable)
        
    #     xpos = 300
    #     ypos = 45400

    #     # rect.setPos(0,-ypos+100)
    #     for i in range(900):
    #         text = QGraphicsTextItem("Frame "+str(i))
    #         text.setPos(-xpos,-ypos+i*100)
    #         text.setDefaultTextColor(QColor.fromRgbF(1., 1.0, 1.0))
    #         self.grScene.addItem(text)

    #     self.grScene.addItem(rect)
    
            
        
        