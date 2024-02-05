#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Oct 20 12:44:51 2023

@author: rachel
"""
from collections import OrderedDict
from node_serializable import Serializable
from node_graphics_edge import *

EDGE_TYPE_DIRECT = 1
EDGE_TYPE_BEZIER = 2

DEBUG = False
class Edge(Serializable):
    def __init__(self, scene, start_socket=None, end_socket=None, edge_type=EDGE_TYPE_DIRECT):
        super().__init__()
        self.scene = scene
        
        self.start_socket = start_socket
        self.end_socket = end_socket
        self.edge_type = edge_type
        
        self.scene.addEdge(self)

        
    def __str__(self):
        return "<Edge  %s..%s>" % (hex(id(self))[2:5], hex(id(self))[-3:])
        
        
    @property    
    def start_socket(self): return self._start_socket
    
    @start_socket.setter
    def start_socket(self, value):
        self._start_socket = value
        if self.start_socket is not None:
            self.start_socket.edge = self
            
            
    @property    
    def end_socket(self): return self._end_socket
    
    @end_socket.setter
    def end_socket(self, value):
        self._end_socket = value
        if self.end_socket is not None:
            self.end_socket.edge = self
                
    
    @property
    def edge_type(self): return self._edge_type

    @edge_type.setter
    def edge_type(self, value):
             
        self._edge_type = value
        
        if hasattr(self, 'grEdge') and self.grEdge is not None:
            self.scene.grScene.removeItem(self.grEdge)
        
        
        self._edge_type = value
        
        if self.edge_type == EDGE_TYPE_DIRECT:            
            self.grEdge = QDMGraphicsEdgeDirect(self)
        elif self.edge_type == EDGE_TYPE_BEZIER: 
            self.grEdge = QDMGraphicsEdgeBezier(self)
        else:
            self.grEdge = QDMGraphicsEdgeBezier(self)
        
        self.scene.grScene.addItem(self.grEdge)
            
        if self.start_socket is not None:
            self.updatePosition()
            
            
    def updatePosition(self):
        sourcePosition = self.start_socket.getSocketPosition()
        sourcePosition[0] += self.start_socket.node.grNode.pos().x()
        sourcePosition[1] += self.start_socket.node.grNode.pos().y()
        self.grEdge.setSource(*sourcePosition)
        if self.end_socket is not None:
            endPosition = self.end_socket.getSocketPosition()
            endPosition[0] += self.end_socket.node.grNode.pos().x()
            endPosition[1] += self.end_socket.node.grNode.pos().y()
            self.grEdge.setDest(*endPosition)
        else:
            self.grEdge.setDest(*sourcePosition)
        self.grEdge.update()
        

    def remove_from_socket(self):
        if self.start_socket is not None:
            self.start_socket.edge = None
        if self.end_socket is not None:
            self.end_socket.edge = None
        self.end_socket = None
        self.start_socket = None
        
    def remove(self):
        self.remove_from_socket()
        self.scene.grScene.removeItem(self.grEdge)
        self.grEdge = None
        try:
            self.scene.removeEdge(self)
        except ValueError:
            pass

    def serialize(self):
        return OrderedDict([
            ('id', self.id),
            ('edge_type', self.edge_type),
            ('start', self.start_socket.id),
            ('end', self.end_socket.id)
        ])
    
    def deserialize(self, data, hashmap={}):
        self.id = data['id']
        self.start_socket = hashmap[data['start']]
        self.end_socket = hashmap[data['end']] 
        self.edge_type = data['edge_type']