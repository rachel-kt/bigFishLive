#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Oct 13 16:20:26 2023

@author: rachel
"""
import math
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from PyQt5.QtGui import *

from PyQt5.QtCore import pyqtSignal as Sgnl

class Helper(QObject):
    messageSignal = Sgnl(int, int)
    
class QDMGraphicsScene(QGraphicsScene):


    def __init__(self, scene, parent=None):
        super().__init__(parent)

        self.itemSelected = Helper()
        self.scene = scene     
        
        self.start_xpos = self.scene.scene_width//2 - 50 # 300
        self.start_ypos = self.scene.scene_height//2 #45400

        #settings        
        
        self.gridSize = 20
        self.gridSquares = 5
        self.numberofFrames = 900
        self.extraSpace = 100
        
        self._color_background = QColor("#393939")
        self._color_light = QColor("#2f2f2f")
        self._color_dark = QColor("#292929")
        
        self._pen_light = QPen(self._color_light)
        self._pen_light.setWidth(1)
        self._pen_dark = QPen(self._color_dark)
        self._pen_dark.setWidth(2)
        
       
        self.setBackgroundBrush(self._color_background)
    
    def setGrScene(self, width, height):
        self.setSceneRect(-width//2,-height//2, width, height)
            
    
    def drawBackground(self, painter, rect):
        super().drawBackground(painter, rect)
        
        # create grid
        
        left = int(math.floor(rect.left()))
        right = int(math.ceil(rect.right()))
        top = int(math.floor(rect.top()))
        bottom = int(math.ceil(rect.bottom()))
        
        
        first_left = left - (left % self.gridSize)
        first_top = top - top % self.gridSize

        # compute lines to be drawn
        
        lines_light, lines_dark = [], []
        for x in range(first_left, right, self.gridSize):
            if (x % (self.gridSize*self.gridSquares) != 0): lines_light.append(QLine(x, top, x, bottom))
            else: lines_dark.append(QLine(x, top, x, bottom))
        for y in range(first_top, bottom, self.gridSize):
            if (y % (self.gridSize*self.gridSquares) != 0): lines_light.append(QLine(left, y, right, y))
            else: lines_dark.append(QLine(left, y, right, y))
            
        # draw the lines
        painter.setPen(self._pen_light)
        painter.drawLines(*lines_light)
        
        painter.setPen(self._pen_dark)
        painter.drawLines(*lines_dark)
        
        greenBrush = QBrush(Qt.green)
        outlinePen = QPen(Qt.black)
        outlinePen.setWidth(2)


        frameLabelPos = []
        for i in range(900):
            text = QGraphicsTextItem("Frame "+str(i))
            text.setPos(-self.start_xpos,-(self.start_ypos-((i+1)*self.gridSize*self.gridSquares)))
            text.setDefaultTextColor(QColor.fromRgbF(1., 1.0, 1.0))
            self.scene.grScene.addItem(text)
