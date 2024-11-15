#!/usr/bin/env  python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 16 16:27:37 2023

@author: rachel
"""

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

class QDMGraphicsSocket(QGraphicsItem):
    def __init__(self, socket):
        self.socket = socket
        super().__init__(socket.node.grNode)
        
        self.radius = 4.0
        self.outline_width = 1.0
        self._color_background = QColor("#FFFF7700")
        self._color_outline = QColor("#FF000000")
        
        self._pen = QPen(self._color_outline)
        self._pen.setWidth(self.outline_width)
        self._brush = QBrush(self._color_background)
        
    def paint(self, painter, QStyleOptionGraphicsItem, widget = None):
        
        # painting circle
        
        painter.setBrush(self._brush)
        painter.setPen(self._pen)
        painter.drawEllipse(-self.radius, -self.radius, 2* self.radius, 2*self.radius)
        
    def boundingRect(self):
        return QRectF(
            -self.radius - self.outline_width,
            -self.radius - self.outline_width,
            2 * self.radius + self.outline_width,
            2 * self.radius + self.outline_width,
        )
    
