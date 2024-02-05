#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 16 16:23:21 2023

@author: rachel
"""
from collections import OrderedDict
from node_serializable import Serializable
from node_graphics_socket import QDMGraphicsSocket

CENTER_TOP = 1
CENTER_BOTTOM = 2

class Socket(Serializable):
    def __init__(self, node, index=0, position = CENTER_TOP):
        #pass
        super().__init__()
        
        self.node = node
        self.index = index
        self.position = position
        
        self.grSocket = QDMGraphicsSocket(self)#.node.grNode)
        
        self.grSocket.setPos(*self.node.getSocketPosition(index, position))
        
        self.edge = None
        
        
    def __str__(self):
        return "<Socket  %d %s..%s>" % (
            self.index, hex(id(self))[2:5], hex(id(self))[-3:]
        )
    
    
    def getSocketPosition(self):
        return self.node.getSocketPosition(self.index, self.position)
        
    def setConnectedEdge(self, edge = None):
        self.edge = edge
        
    def hasEdge(self):
        return self.edge is not None
    
    def serialize(self):
        return OrderedDict([
            ('id', self.id),
            ('index', self.index),
            ('position', self.position),
        ])
    
    def deserialize(self, data, hashmap={}):
        self.id = data['id']
        hashmap[data['id']] = self
        return True