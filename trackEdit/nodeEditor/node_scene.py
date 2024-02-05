#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 16 11:40:34 2023

@author: rachel
"""
import json
from collections import OrderedDict
from node_serializable import Serializable
from node_graphics_scene import QDMGraphicsScene
from node_node import Node
from node_edge import Edge

class Scene(Serializable):
    def __init__(self):
        super().__init__()
        self.nodes = []
        self.edges = []
        
        self.gridSize = 20
        self.gridSquares = 5
        self.numberofFrames = 900
        self.extraSpace = 1000
        
        self.scene_width = 1500
        self.scene_height = (self.gridSize*self.gridSquares*self.numberofFrames)+self.extraSpace
        
        self._last_selected_items = []
        self._item_Selected_listeners = []
        self._items_deselected_listeners = []
        
        self.initUI()
        
        # self.grScene.itemSelected.selectedNode.connect(self.onItemSelected)
        
    def initUI(self):
        self.grScene = QDMGraphicsScene(self)
        self.grScene.setGrScene(self.scene_width, self.scene_height)
        
    def resetLastSelectedState(self):
        for node in self.nodes:
            node.grNode._last_selected_state = False
        for edge in self.edges:
            edge.grEdge._last_selected_state = False
            
    def addItemSelectedListener(self, callback):
        self._item_Selected_listeners.append(callback)
        
    def addItemDeselectedListener(self, callback):
        self._items_deselected_listeners.append(callback)
        
        
    # def onItemSelected(self):
    #     print("on i s")
        
    def addNode(self, node):
        self.nodes.append(node)
        
    def addEdge(self, edge):
        self.edges.append(edge)
        
    def removeNode(self, node):
        self.nodes.remove(node)
        
    def removeEdge(self, edge):
        self.edges.remove(edge)
        
    def clear(self):
        while len(self.nodes) > 0 :
            self.nodes[0].remove()
    
    def saveToFile(self, filename):
        with open(filename, 'w') as file:
            file.write(json.dumps(self.serialize(), indent=4))
        print("Saving to ", filename, "was successful.")
            
    
    def loadFromFile(self, filename):
        with open(filename, 'r', encoding='utf-8') as file:
            raw_data = file.read()
            data = json.loads(raw_data)
            self.deserialize(data)
    
    
    def serialize(self):
        nodes, edges = [], []
        for node in self.nodes: nodes.append(node.serialize())
        for edge in self.edges: edges.append(edge.serialize())
        return OrderedDict([
            ('id', self.id),
            ('scene_width', self.scene_width),
            ('scene_height', self.scene_height),
            ('nodes', nodes),
            ('edges', edges),
        ])
    
    def deserialize(self, data, hashmap={}):
        print(" deserializing data", data)
        
        self.clear()
        
        hashmap = {}
        
        # create nodes
        for node_data in data['nodes']:
            Node(self).deserialize(node_data, hashmap)
            
        # create nodes
        for edge_data in data['edges']:
            Edge(self).deserialize(edge_data, hashmap)
        
        return True
        
    def clear(self):
        """Remove all `Nodes` from this `Scene`. This causes also to remove all `Edges`"""
        while len(self.nodes) > 0:
            self.nodes[0].remove()

        self.has_been_modified = False

        