#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 16 12:07:41 2023

@author: rachel
"""

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class QDMGraphicsNode(QGraphicsItem):
    def __init__(self, node, helper, parent=None):
        super().__init__(parent)
        
        self.node = node
        self.helper = helper
        # init our flags
        
        self._last_selected_state = False
        
        self.initSizes()
        self.initAssets()
        
        self.initUI()
        
        
    def initUI(self):
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        # self.setFlag(QGraphicsItem.ItemIsMovable)
        self.initTitle()
        self.title = self.node.title
        
        self.initSockets()


    def initSizes(self):
        self.width = 100
        self.height = 60
        self.edge_size = 10.0
        self.title_height = 20.0
        self._padding = 10.0
        
        
    def initAssets(self):
        self._title_color = Qt.white  
        self._title_font = QFont("Ubuntu", 10)  
        
        self._pen_default = QPen(QColor("#7F000000"))
        self._pen_selected = QPen(QColor("#FFFFA637"))
        
        self._brush_title = QBrush(QColor("#FF313131"))
        self._brush_background = QBrush(QColor("#d7d6d5"))
        
    def onSelected(self):
        xcoord = self.node.grNode.pos().x()
        ycoord = self.node.grNode.pos().y()
        tcoord = int(-1*(-1*ycoord - 45400)/100)
        self.helper.messageSignal.emit(int(tcoord), int(xcoord))
        
        
    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)    
        
        for node in self.scene().scene.nodes:
             if node.grNode.isSelected():
                 node.updateConnectedEdges()
        
    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        if self._last_selected_state!=self.isSelected():
            self.node.scene.resetLastSelectedState()
            self._last_selected_state = self.isSelected()
            self.onSelected()
        
    def boundingRect(self):
        return QRectF(
            0,
            0,
            self.width,
            self.height
        ).normalized()
        
    
    def initTitle(self):
        self.title_item = QGraphicsTextItem(self)
        self.title_item.node = self.node
        self.title_item.setDefaultTextColor(self._title_color)
        self.title_item.setFont(self._title_font)
        self.title_item.setTextWidth(self.width-2*self._padding)
        self.title_item.setPos(self._padding,0)
        
    def initSockets(self):
        pass
        
    @property
    def title(self): return self._title
    @title.setter
    def title(self, value):
        self._title = value
        self.title_item.setPlainText(self._title)
        
        
    def paint(self, painter, QStyleOptionGraphicsItem, widget=None):
        
        # title
        path_title = QPainterPath()
        path_title.setFillRule(Qt.WindingFill)
        path_title.addRoundedRect(0,0,self.width, self.title_height, self.edge_size, self.edge_size)
        path_title.addRect(0,self.title_height - self.edge_size, self.edge_size, self.edge_size)
        path_title.addRect(self.width - self.edge_size ,self.title_height - self.edge_size, self.edge_size, self.edge_size)
        painter.setPen(Qt.NoPen)
        painter.setBrush(self._brush_title)
        painter.drawPath(path_title.simplified())
        
        
        # content
        path_content = QPainterPath()
        path_content.setFillRule(Qt.WindingFill)
        path_content.addRoundedRect(0, self.title_height, self.width, self.height - self.title_height, self.edge_size, self.edge_size)
        path_content.addRect(0, self.title_height, self.edge_size, self.edge_size)
        path_content.addRect(self.width - self.edge_size, self.title_height, self.edge_size, self.edge_size)
        painter.setPen(Qt.NoPen)
        painter.setBrush(self._brush_background)
        painter.drawPath(path_content.simplified())
        
        # outline
        path_outline = QPainterPath()
        path_outline.addRoundedRect(0,0, self.width, self.height, self.edge_size, self.edge_size)
        painter.setPen(self._pen_default if not self.isSelected() else self._pen_selected)
        painter.setBrush(Qt.NoBrush)
        painter.drawPath(path_outline.simplified())
        
        