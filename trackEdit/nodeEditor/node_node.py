#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 16 12:01:45 2023

@author: rachel
"""
from collections import OrderedDict
from node_serializable import Serializable
from node_graphics_node import QDMGraphicsNode
from node_socket import *

DEBUG=True


class Node(Serializable):
    def __init__(self, scene, title="Undefined Node", inputs=[], outputs=[]):
        super().__init__()
        self._title = title
        self.scene = scene

        self.grNode = QDMGraphicsNode(self, self.scene.grScene.itemSelected)
        
        self.title = title        
        self.scene.addNode(self)
        self.scene.grScene.addItem(self.grNode)
        
        
        # create sockets for inout and outputs
        
        self.inputs = []
        self.outputs = []
        
        counter = 0
        
        for item in inputs:
            socket = Socket(node=self, index=counter, position=CENTER_TOP)
            counter += 1
            self.inputs.append(socket)
            
        counter = 0
        for item in outputs:
            socket = Socket(node=self, index=counter, position=CENTER_BOTTOM)
            counter += 1
            self.outputs.append(socket)
            
    def __str__(self):
        return "<Node  %s..%s>" % (hex(id(self))[2:5], hex(id(self))[-3:])
    
    @property
    def title(self): return self._title
    
    @title.setter
    def title(self, value):
        self._title = value
        self.grNode.title = self._title
        
    @property
    def pos(self):
        return self.grNode.pos()  # QPointF ...    
    
    def setPos(self, x, y):
        self.grNode.setPos(x, y)
        

    def getSocketPosition(self, index, position):
        x = self.grNode.width//2
        y = 0 if (position==CENTER_TOP) else self.grNode.height
        
        return [x, y]
    
    def updateConnectedEdges(self):
        for socket in self.inputs + self.outputs:
            
            if socket.hasEdge():
                socket.edge.updatePosition()
                
    
    def remove(self):
        if DEBUG: print("> Removing Node", self)
        if DEBUG: print(" - remove edges from sockets")
        for socket in (self.inputs+self.outputs):
            if socket.hasEdge():
                if DEBUG: print("Removing edge", socket.edge)
                socket.edge.remove()
                    
        if DEBUG: print(" - remove grNode")
        self.scene.grScene.removeItem(self.grNode)
        self.grNode = None
        if DEBUG: print(" - remove node from scene")
        self.scene.removeNode(self)
        if DEBUG: print(" - all good")
        
    def serialize(self):
        inputs, outputs = [], []
        for socket in self.inputs: inputs.append(socket.serialize())
        for socket in self.outputs: outputs.append(socket.serialize())
        return OrderedDict([
            ('id', self.id),
            ('title', self.title),
            ('pos_x', self.grNode.scenePos().x()),
            ('pos_y', self.grNode.scenePos().y()),
            ('inputs', inputs),
            ('outputs', outputs),
        ])
    
    def deserialize(self, data, hashmap={}):
        self.id = data['id']
        hashmap[data['id']] = self
        
        self.setPos(data['pos_x'], data['pos_y'])
        self.title = data['title']    
        
        data['inputs'].sort(key=lambda socket: socket['index'] + socket['position'] * 10000)
        data['outputs'].sort(key=lambda socket: socket['index'] + socket['position'] * 10000)
        
        self.inputs = []
        for socket_data in data['inputs']:
            new_socket = Socket(node=self, index=socket_data['index'], position=socket_data['position'])
            new_socket.deserialize(socket_data, hashmap)
            self.inputs.append(new_socket)


        self.outputs = []
        for socket_data in data['outputs']:
            new_socket = Socket(node=self, index=socket_data['index'], position=socket_data['position'])
            new_socket.deserialize(socket_data, hashmap)
            self.outputs.append(new_socket)
        
        print(hashmap)
        return True
    