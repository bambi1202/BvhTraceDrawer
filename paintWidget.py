import numpy as np
import time

from PyQt5.Qt import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from OpenGL.GL import *
from OpenGL.GLU import *
import similaritymeasures

from python_bvh import BVHNode, getNodeRoute
from node_editor import NodeEditor
import pandas as pd


import glm
import math
from pyrr import Matrix44, Vector3, vector

COLORS = {
    'rHand': [128, 0, 0],
    'lHand': [0, 128, 0],
    'rFoot': [128, 128, 0],
    'lFoot': [0, 0, 128],
    'head': [128, 0, 128]
}

class PaintWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.hParentWidget = parent
        self.setMinimumSize(500, 500)
        self.csv_pds = self.hParentWidget.csv_pds
        self.keynodes = ['rHand', 'lHand', 'rFoot', 'lFoot', 'head']
        self.node_sets = []
        self.ranked = []
        self.viewFlag = 'side'
        self.lhand_rank = 0
        self.rhand_rank = 0
        

        self.retrieving = False
        self.pressed = False
        self.editor = NodeEditor(self.hParentWidget.lhand_rot, self.hParentWidget.rhand_rot)

        self.prepareNodeSets()
        
        # for csv_input in self.csv_pds:
        #     csv_node_traje = {}
        #     for keynode in self.keynodes:
        #         csv_node_traje[keynode] = []
        #     for row in csv_input.iterrows():
        #         hip = glm.vec3(row[1]['hip.X'], row[1]['hip.Y'], row[1]['hip.Z'])
        #         sideview = glm.vec3(row[1]['rButtock.X'], row[1]['hip.Y'], row[1]['rButtock.Z'])
        #         norm_vec = glm.normalize(hip - sideview)
        #         camera_pos = hip - norm_vec * 150
        #         camera_up = glm.vec3(0, 1.0, 0)
        #         projection_mat = glm.perspective(60.0 * math.pi / 180.0, 1.0, 1.0, 1000.0) * glm.lookAt(camera_pos, hip, camera_up)
        #         viewport = glm.vec4(0.0, 0.0, 500.0, 500.0)
        #         modelview = glm.mat4(1.0)
        #         # hip_coords = glm.project(glm.vec3(hip), modelview, projection_mat, viewport)
        #         # self.psets['hip']['points'].append(QPointF(hip_coords.x, 500 - hip_coords.y))

        #         for keynode in self.keynodes:
        #             node = glm.vec3(row[1][f'{keynode}.X'], row[1][f'{keynode}.Y'], row[1][f'{keynode}.Z'])
        #             node_coords = glm.project(glm.vec3(node), modelview, projection_mat, viewport)
        #             csv_node_traje[keynode].append([node_coords.x, 500 - node_coords.y])
        #     self.node_sets.append(csv_node_traje)
        

        # self.psets = {
        #     'rHand': {
        #         'color': QColor(128,   0,   0, 255),
        #         'points': []
        #     },
        #     'lHand': {
        #         'color': QColor(  0, 128,   0, 255),
        #         'points': []
        #     },
        #     'rFoot': {
        #         'color': QColor(128, 128,   0, 255),
        #         'points': []
        #     },
        #     'lFoot': {
        #         'color': QColor(  0,   0, 128, 255),
        #         'points': []
        #     },
        #     'head': {
        #         'color': QColor(128,   0, 128, 255),
        #         'points': []
        #     },
        #     # 'hip': {
        #     #     'color': QColor(  0, 128, 128, 255),
        #     #     'points': []
        #     # }
        # }
        
        self.px = None
        self.py = None
        self.points = []
        # print(self.psets)

    def setViewFlag(self, flag):
        assert flag in ['top', 'side', 'front']
        self.viewFlag = flag
        self.prepareNodeSets()
        self.update()
    
    def prepareNodeSets(self):
        for csv_input in self.csv_pds:
            csv_node_traje = {}
            for keynode in self.keynodes:
                csv_node_traje[keynode] = []
            for row in csv_input.iterrows():
                hip = glm.vec3(row[1]['hip.X'], row[1]['hip.Y'], row[1]['hip.Z'])
                sideview = glm.vec3(row[1]['rButtock.X'], row[1]['hip.Y'], row[1]['rButtock.Z'])
                topview = glm.vec3(row[1]['hip.X'], row[1]['hip.Y'] + 150, row[1]['hip.Z'])
                
                if self.viewFlag == 'front':
                    norm_vec = glm.normalize(hip - sideview)
                    norm_vec = glm.vec3(-norm_vec.z, norm_vec.y, norm_vec.x)
                if self.viewFlag == 'side':
                    norm_vec = glm.normalize(hip - sideview)
                if self.viewFlag == 'top':
                    norm_vec = glm.normalize(hip - topview)
                camera_pos = hip - 150 * norm_vec
                camera_up = glm.vec3(0, 1, 0)
                projection_mat = glm.perspective(60.0 * math.pi / 180.0, 1.0, 1.0, 1000.0) * glm.lookAt(camera_pos, hip, camera_up)

                viewport = glm.vec4(0.0, 0.0, 500.0, 500.0)
                modelview = glm.mat4(1.0)
                # hip_coords = glm.project(glm.vec3(hip), modelview, projection_mat, viewport)
                # self.psets['hip']['points'].append(QPointF(hip_coords.x, 500 - hip_coords.y))

                for keynode in self.keynodes:
                    node = glm.vec3(row[1][f'{keynode}.X'], row[1][f'{keynode}.Y'], row[1][f'{keynode}.Z'])
                    node_coords = glm.project(glm.vec3(node), modelview, projection_mat, viewport)
                    csv_node_traje[keynode].append([node_coords.x, 500 - node_coords.y])
            self.node_sets.append(csv_node_traje)

    def mousePressEvent(self, event):
        self.pressed = True
        self.retrieving = False
        self.points = []
        self.points.append(event.pos())
        self.update()

    def mouseMoveEvent(self, event):
        assert self.pressed is True
        self.points.append(event.pos())
        self.update()

    def mouseReleaseEvent(self, event):
        self.pressed = False
        self.retrieving = True
        # self.psets.append(self.points)
        # self.points = []
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setPen(Qt.NoPen)
        painter.setBrush(Qt.white)
        painter.drawRect(self.rect())

        if len(self.points) > 0:
            painter.setPen(QColor(0,   0,   0,  255))
            painter.drawPolyline(*self.points)
            if self.retrieving:
                query_stroke_coords = [[p.x(), p.y()] for p in self.points]
                query_stroke = np.array(query_stroke_coords)

                rank = []

                for node_traje in self.node_sets:
                    if self.hParentWidget.nodeFlag == 'lHand':
                        to_compare_coords = node_traje['lHand']
                    if self.hParentWidget.nodeFlag == 'rHand':
                        to_compare_coords = node_traje['rHand']  
                    if self.hParentWidget.nodeFlag == 'lFoot':
                        to_compare_coords = node_traje['lFoot']    
                    if self.hParentWidget.nodeFlag == 'rFoot':
                        to_compare_coords = node_traje['rFoot']  
                    if self.hParentWidget.nodeFlag == 'head':
                        to_compare_coords = node_traje['head']
                    to_compare = np.array(to_compare_coords)
                    difference = similaritymeasures.frechet_dist(query_stroke, to_compare)
                    # print(difference)
                    rank.append(difference)
                    self.ranked = np.argsort(rank)

                print(self.ranked)
                # self.best_matched = 1
                if self.hParentWidget.nodeFlag == 'lHand':
                    self.lhand_rank = self.ranked[0]
                if self.hParentWidget.nodeFlag == 'rHand':
                    self.rhand_rank = self.ranked[0]            

                for idx, i in enumerate(self.ranked[:5]):
                    csv_input = self.csv_pds[i]
                    single_traje = {}
                    for keynode in self.keynodes:
                        single_traje[keynode] = []
                    for row in csv_input.iterrows():
                        hip = glm.vec3(row[1]['hip.X'], row[1]['hip.Y'], row[1]['hip.Z'])
                        sideview = glm.vec3(row[1]['rButtock.X'], row[1]['hip.Y'], row[1]['rButtock.Z'])
                        topview = glm.vec3(row[1]['hip.X'], row[1]['hip.Y'] + 150, row[1]['hip.Z'])
                        
                        if self.viewFlag == 'front':
                            norm_vec = glm.normalize(hip - sideview)
                            norm_vec = glm.vec3(-norm_vec.z, norm_vec.y, norm_vec.x)
                        if self.viewFlag == 'side':
                            norm_vec = glm.normalize(hip - sideview)
                        if self.viewFlag == 'top':
                            norm_vec = glm.normalize(hip - topview)
                        camera_pos = hip - 150 * norm_vec
                        camera_up = glm.vec3(0, 1, 0)
                        projection_mat = glm.perspective(60.0 * math.pi / 180.0, 1.0, 1.0, 1000.0) * glm.lookAt(camera_pos, hip, camera_up)

                        viewport = glm.vec4(0.0, 0.0, 500.0, 500.0)
                        modelview = glm.mat4(1.0)

                        for keynode in self.keynodes:
                            node = glm.vec3(row[1][f'{keynode}.X'], row[1][f'{keynode}.Y'], row[1][f'{keynode}.Z'])
                            node_coords = glm.project(glm.vec3(node), modelview, projection_mat, viewport)
                            single_traje[keynode].append(QPointF(node_coords.x, 500 - node_coords.y))

                    for k, v in single_traje.items():
                        if k == self.hParentWidget.nodeFlag:
                            painter.setOpacity(0.5)
                            painter.setPen(QColor(*COLORS[k], 255))
                            painter.drawPolyline(*v)
                            painter.setOpacity(1)
                
                self.retrieving = False
        if self.hParentWidget.paintGlobalPanel.motionFile is not None: 
            motionFile = self.hParentWidget.paintGlobalPanel.motionFile 
            skeletonRank = self.hParentWidget.paintGlobalPanel.ranked[0]        
            self.editor.editBVH(motionFile, self.lhand_rank, self.rhand_rank)
            print(self.lhand_rank, self.rhand_rank)
            editedFile = 'bvh/output/' + str(skeletonRank) + '_n_test_edited.bvh'
            self.hParentWidget.playFile(editedFile)


        # query_stroke = np.zeros((len(self.px), 2))
        # query_stroke[:, 0] = self.
        
        

        # # draw historical points
        # for k, v in self.psets.items():
        #     # print(k)
        #     painter.setPen(v['color'])
        #     painter.drawPolyline(*v['points'])

        # # draw current points
        # if self.points:
        #     painter.drawPolyline(*self.points)