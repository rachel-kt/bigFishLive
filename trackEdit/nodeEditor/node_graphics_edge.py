#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Oct 20 12:47:46 2023

@author: rachel
"""
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from node_socket import *
import math

EDGE_CP_ROUNDNESS = 100
DEBUG = False

class QDMGraphicsEdge(QGraphicsPathItem):
    def __init__(self, edge, parent=None):
        super().__init__(parent)
        
        self.edge = edge
        
        # init our flags
        # self.pathCalculator = self.determineEdgePathClass()(self)
        
        self._last_selected_state = False
        
        self.posSource = [0, 0]
        self.posDest = [200, 100]
        
        self.initAssets()
        self.initUI()
        
        
    def initUI(self):
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setZValue(-1)
        
        
    def initAssets(self):
        self._color = QColor("#001000")
        self._color_selected = QColor("#00ff00")
        
        self._pen = QPen(self._color)
        self._pen_selected = QPen(self._color_selected)
        self._pen_dragging = QPen(self._color_selected)
        
        self._pen.setWidth(6)
        self._pen_selected.setWidth(6)
        self._pen_dragging.setWidth(3)
        self._pen_dragging.setStyle(Qt.DashLine)
        

    def onSelected(self):
        print("Edge selected")
        self.edge.scene.grScene.itemSelected.emit()
        
    def setSource(self, x, y):
        self.posSource = [x, y]
        
    def setDest(self, x, y):
        self.posDest = [x, y]
    
    def boundingRect(self):
        """Defining Qt' bounding rectangle"""
        return self.shape().boundingRect()

    def shape(self):
        """Returns ``QPainterPath`` representation of this `Edge`

        :return: path representation
        :rtype: ``QPainterPath``
        """
        return self.calcPath()
        
    
    def paint(self, painter, QStyleOptionsGraphicsItem, widget=None):
        self.setPath(self.calcPath())
        
        if self.edge.end_socket is None:
            painter.setPen(self._pen_dragging)
        else:
            painter.setPen(self._pen if not self.isSelected() else self._pen_selected)
        painter.setBrush(Qt.NoBrush)
        painter.drawPath(self.path())
        
    def intersectsWith(self, p1, p2):
        cutpath = QPainterPath(p1)
        cutpath.lineTo(p2)
        path = self.calcPath()
        return cutpath.intersects(path)
        

    def calcPath(self):
        raise NotImplemented("This method")
                
        
class QDMGraphicsEdgeDirect(QDMGraphicsEdge):
    def calcPath(self):
        path = QPainterPath(QPointF(self.posSource[0], self.posSource[1]))
        path.lineTo(self.posDest[0], self.posDest[1])
        # self.setPath(path)
        return path

class QDMGraphicsEdgeBezier(QDMGraphicsEdge):
    def calcPath(self):
        s = self.posSource
        d = self.posDest        
        dist_x = (d[0]-s[0])*0.5
        dist_y = (d[1]-s[1])*0.5

        cpy_s = +dist_y      
        cpy_d = -dist_y
        cpx_s = 0
        cpx_d = 0
        
        if self.edge.start_socket is not None:
            
            startingSocketPos = self.edge.start_socket.position
    
            
            if (s[1] > d[1] and startingSocketPos in [2]):#or (s[1] < d[1] and startingSocketPos in [1]
                cpy_d += -1
                cpy_s += -1
                
                cpx_d = ((s[0] - d[0])/math.fabs((s[0] - d[0]) if (s[0] - d[0])!=0 else 0.000001))*EDGE_CP_ROUNDNESS
    
                cpx_s = ((d[0] - s[0])/math.fabs((d[0] - s[0]) if (d[0] - s[0])!=0 else 0.000001))*EDGE_CP_ROUNDNESS

        path = QPainterPath(QPointF(self.posSource[0], self.posSource[1]))
        path.cubicTo(s[0] + cpx_s, s[1]+ cpy_s, d[0] + cpx_d, d[1] + cpy_d, self.posDest[0], self.posDest[1])
        # self.setPath(path)
        return path

