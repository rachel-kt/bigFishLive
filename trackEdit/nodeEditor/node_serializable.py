#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov 29 13:24:24 2023

@author: rachel
"""

class Serializable():
    def __init__(self):
        self.id = id(self)
        
        
    def serialize(self):
        raise NotImplemented()
    
    def deserialize(self, data, hashmap={}):
        raise NotImplemented
        
        
            
