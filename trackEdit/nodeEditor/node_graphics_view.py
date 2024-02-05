#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Oct 13 17:50:40 2023

@author: rachel
"""

from PyQt5.QtWidgets import QGraphicsView, QApplication
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from node_graphics_socket import QDMGraphicsSocket
from node_graphics_edge import QDMGraphicsEdge
from node_edge import Edge, EDGE_TYPE_BEZIER
from node_node import QDMGraphicsNode
from node_graphics_cutline import QDMCutLine


MODE_NOOP = 1
MODE_EDGE_DRAG = 2
MODE_EDGE_CUT = 3           #: Mode representing when we draw a cutting edge
EDGE_DRAG_START_THRESHOLD = 10
DEBUG = True




class QDMGraphicsView(QGraphicsView):
    scenePosChanged = pyqtSignal(int, int)
    def __init__(self, grScene, parent=None):
        super().__init__(parent)
        self.grScene = grScene
        
        self.initUI()
        
        self.setScene(self.grScene)
        
        self.mode = MODE_NOOP
        
        self.rubberBandDraggingRectangle = False
    
    def initUI(self):
        self.setRenderHints(QPainter.Antialiasing | 
                            QPainter.HighQualityAntialiasing | 
                            QPainter.TextAntialiasing |
                            QPainter.SmoothPixmapTransform)
                            
        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
        self.setDragMode(QGraphicsView.RubberBandDrag)
        
        # cutline
        self.cutline = QDMCutLine()
        self.grScene.addItem(self.cutline)

        
    def mousePressEvent(self, event):
        """Dispatch Qt's mousePress event to corresponding function below"""
        if event.button() == Qt.MiddleButton:
            self.middleMouseButtonPress(event)
        elif event.button() == Qt.LeftButton:
            self.leftMouseButtonPress(event)
        elif event.button() == Qt.RightButton:
            self.rightMouseButtonPress(event)
        else:
            super().mousePressEvent(event)
            
            
    def mouseReleaseEvent(self, event: QMouseEvent):
        """Dispatch Qt's mouseRelease event to corresponding function below"""
        if event.button() == Qt.MiddleButton:
            self.middleMouseButtonRelease(event)
        elif event.button() == Qt.LeftButton:
            self.leftMouseButtonRelease(event)
        elif event.button() == Qt.RightButton:
            self.rightMouseButtonRelease(event)
        else:
            super().mouseReleaseEvent(event)

            
    def leftMouseButtonPress(self, event):
        """Get item which we clicked on by Left mouse button press"""

        # get the item we clicked on
        item = self.getItemAtClick(event)
        # store position of LMB click
        self.last_left_mouse_click_scene_pos = self.mapToScene(event.pos())
        
        if DEBUG: print("LMB Click on", item, self.debug_modifiers(event))
        
        if hasattr(item, "node") or isinstance(item, QDMGraphicsEdge) or item is None:
            if event.modifiers() & Qt.ShiftModifier:
                if DEBUG: print("LMB +Shift on", item)
                event.ignore()
                fakeEvent = QMouseEvent(QEvent.MouseButtonPress, event.localPos(), event.screenPos(), Qt.LeftButton, event.buttons() | Qt.LeftButton, event.modifiers() | Qt.ControlModifier)
                super().mousePressEvent(fakeEvent)
                return
        # logic
        if type(item) is QDMGraphicsSocket:
            if self.mode == MODE_NOOP:
                self.mode = MODE_EDGE_DRAG
                self.edgeDragStart(item)
                return
            
        if self.mode == MODE_EDGE_DRAG:
            res = self.edgeDragEnd(item)
            if res: return   
            
        
        if type(item) is QDMGraphicsNode:
            print("Node is selected")
            self.NodeIsSelected = True
        
        # if item is None:
        #     self.grScene.itemsDeselected.emit() 
        
        if item is None:
            if event.modifiers() & Qt.ControlModifier:
                self.mode = MODE_EDGE_CUT
                fakeEvent = QMouseEvent(QEvent.MouseButtonRelease, 
                                        event.localPos(), event.screenPos(),
                                        Qt.LeftButton, Qt.NoButton, 
                                        event.modifiers())
                super().mouseReleaseEvent(fakeEvent)
                QApplication.setOverrideCursor(Qt.CrossCursor)
                return
            else:
                self.rubberBandDraggingRectangle = True
        
        super().mousePressEvent(event)
        # 
        
        
        
                             
    def leftMouseButtonRelease(self, event):
        """Get item which we clicked on by Left mouse button release"""
        
        # get item which we clicked on
        item = self.getItemAtClick(event)
        
        if hasattr(item, "node") or isinstance(item, QDMGraphicsEdge) or item is None:
            if event.modifiers() & Qt.ShiftModifier:
                if DEBUG: print("LMB Release +Shift on", item)
                event.ignore()
                fakeEvent = QMouseEvent(event.type(), event.localPos(), event.screenPos(),
                                        Qt.LeftButton, Qt.NoButton,
                                        event.modifiers() | Qt.ControlModifier)
                super().mouseReleaseEvent(fakeEvent)
                return
        
        if self.mode==MODE_EDGE_CUT:
            if DEBUG: print("LMB Release +Shift on", item)
            self.cutIntersectingEdges()
            self.cutline.line_points = []
            self.cutline.update()
            QApplication.setOverrideCursor(Qt.ArrowCursor)
            self.mode = MODE_NOOP       
            return
        
        
        # logic        
        if self.mode==MODE_EDGE_DRAG:
            if self.distanceBetweenClickAndReleaseIsOff(event):
                res = self.edgeDragEnd(item)
                if res: return 
                
        # if self.dragMode() == QGraphicsView.RubberBandDrag:
        if self.rubberBandDraggingRectangle:
            self.rubberBandDraggingRectangle = False
            pass
            
        super().mouseReleaseEvent(event)
    
        
        
    def rightMouseButtonPress(self, event):
        super().mousePressEvent(event)
        # get item which we clicked on
        item = self.getItemAtClick(event)
        
        if DEBUG:
            if isinstance(item, QDMGraphicsEdge): print('RMB DEBUG', item.edge, 'connecting :',
                                                        item.edge.start_socket, '<--->', item.edge.end_socket)
            if type(item) is QDMGraphicsSocket: print('RMB DEBUG', item.socket, 'has edge:', item.socket.edge)
            
            if item is None:
                print('SCENE:')
                print('     Nodes:')
                for node in self.grScene.scene.nodes: print('        ', node)
                
                print('     Edges:')
                for edge in self.grScene.scene.edges: print('        ', edge)
         
            
    def mouseMoveEvent(self, event):
        if self.mode == MODE_EDGE_DRAG:
            pos = self.mapToScene(event.pos())
            self.dragEdge.grEdge.setDest(pos.x(), pos.y())
            self.dragEdge.grEdge.update()
        
        self.last_scene_nouse_pos = self.mapToScene(event.pos())
        self.scenePosChanged.emit(
            int(self.last_scene_nouse_pos.x()),int(self.last_scene_nouse_pos.y())
            )
        
        if self.mode == MODE_EDGE_CUT:
            pos = self.mapToScene(event.pos())
            self.cutline.line_points.append(pos)
            self.cutline.update()
        
        super().mouseMoveEvent(event)
        
    def debug_modifiers(self, event):
        out = "MODS: "
        if event.modifiers() & Qt.ShiftModifier: out += "SHIFT "
        if event.modifiers() & Qt.ControlModifier: out += "CTRL "
        if event.modifiers() & Qt.AltModifier: out += "ALT "
        return out
        
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Delete:
            self.deleteSelected()
        elif event.key() == Qt.Key_S and event.modifiers() & Qt.ShiftModifier:
            self.grScene.scene.saveToFile('graph.json.txt')
        elif event.key() == Qt.Key_L and event.modifiers() & Qt.ControlModifier:
            print('L pressed')
            self.grScene.scene.loadFromFile('graph.json.txt')
        else:
            super().keyPressEvent(event)
            
    
    def cutIntersectingEdges(self):
        # pass
        for ix in range(len(self.cutline.line_points)-1):
            p1 = self.cutline.line_points[ix]
            p2 = self.cutline.line_points[ix + 1]
            
            for edge in self.grScene.scene.edges:
                if edge.grEdge.intersectsWith(p1,p2):
                    edge.remove()
    

    def deleteSelected(self):
        for item in self.grScene.selectedItems():
            if isinstance(item, QDMGraphicsEdge):
                item.edge.remove()
            elif hasattr(item, 'node'):
                item.node.remove()
        
    def getItemAtClick(self, event):
        """ return object on which we have clicked/released the button"""
        pos = event.pos()
        obj = self.itemAt(pos)
        return obj
    


    def edgeDragStart(self, item):
        if DEBUG: print('View:: edgeDragStart ~ Start dragging edge')
        if DEBUG: print('View:: edgeDragStart ~    assign Start Socket to:', item.socket)
        self.previousEdge = item.socket.edge
        self.last_start_socket = item.socket
        self.dragEdge = Edge(self.grScene.scene, item.socket, None, EDGE_TYPE_BEZIER)
        if DEBUG: print('View: edgeDragStart -- dragEdge:', self.dragEdge)
        print("View: edgeDragStart Socket Type",self.dragEdge.start_socket.position)



    def edgeDragEnd(self, item):
        """ return True if you want to skip the rest of the code"""
        self.mode = MODE_NOOP

        if type(item) is QDMGraphicsSocket and (self.last_start_socket.position!=item.socket.position):
            
            if DEBUG: print('View: edgeDragStart ~     assign End socket', item.socket)
            if item.socket.hasEdge():
                item.socket.edge.remove()
            if self.previousEdge is not None: self.previousEdge.remove()
            self.dragEdge.start_socket = self.last_start_socket
            self.dragEdge.end_socket = item.socket
            self.dragEdge.start_socket.setConnectedEdge(self.dragEdge)
            self.dragEdge.end_socket.setConnectedEdge(self.dragEdge)
            if DEBUG: print('View: edgeDragEnd -- assigned')
            self.dragEdge.updatePosition()
            return True
        
        if DEBUG: print('View: edgeDragEnd ~ End dragging edge')
        self.dragEdge.remove()
        self.dragEdge = None
        
        if DEBUG: print("View: edgeDragEnd - about to set socket to previous edge")
        if self.previousEdge is not None:
            self.previousEdge.start_socket.edge = self.previousEdge
        return False
        
    

    def distanceBetweenClickAndReleaseIsOff(self, event):
        """ measures if we are too far from the last left mouse button clicked scene postion"""
        
        new_left_mouse_release_scene_pos = self.mapToScene(event.pos())
        distance_scene = new_left_mouse_release_scene_pos - self.last_left_mouse_click_scene_pos
        edge_drag_threshold_sq = EDGE_DRAG_START_THRESHOLD*EDGE_DRAG_START_THRESHOLD
        return (distance_scene.x()*distance_scene.x() + distance_scene.y()*distance_scene.y()) > edge_drag_threshold_sq
    
