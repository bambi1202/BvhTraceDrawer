import numpy as np
import time
import os

from PyQt5.Qt import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from OpenGL.GL import *
from OpenGL.GLU import *

from python_bvh import BVHNode, getNodeRoute
import pandas as pd


import glm
import math
from pyrr import Matrix44, Vector3, vector
import similaritymeasures

COLORS = {
    'hip':[0, 0, 255]
}

class PaintWidgetGlobal(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.hParentWidget = parent
        self.setMinimumSize(500, 500)
        self.csv_pds = self.hParentWidget.csv_pds
        self.keynodes = ['hip']
        self.hip_sets = []
        self.ranked = []
        self.viewFlag = 'top'
        self.retrieving = False
        self.pressed = False

        self.camposTop = glm.vec3(0, 150, 0)
        self.camposSide = glm.vec3(0, 75, 100)
        self.camposFront = glm.vec3(100 ,75, 0)
        self.prepareNodeSets()

        self.motionFile = None
        self.px = None
        self.py = None
        self.points = []
        '''
        for file in os.listdir(path):
            file_name = path + file
            self.readMyCsv(file_name)
            # rename PENG
            # os.rename(file_name, (path + str(fileid) + '.csv'))
            fileid = fileid + 1  
        
        self.pen_points = []
        self.hip_points = []
        self.head_points = []

        self.hip_p_matrix = []
        self.hip_shadow = []
        self.best_matched = 1
            
        self.drawSketchFlag = None
        self.px = []
        self.py = []
        self.py_inverse = []

        self.points = []
        self.psets = {
            'hip1': {
                'color': QColor(0, 0, 255, 255),
                'points': []
            },
            'hip2': {
                'color': QColor(0, 0, 255, 255),
                'points': []
            },
            'hip3': {
                'color': QColor(0, 0, 255, 255),
                'points': []
            },
            'hip4': {
                'color': QColor(0, 0, 255, 255),
                'points': []
            },
            'hip5': {
                'color': QColor(0, 0, 255, 255),
                'points': []
            },
        }

        self.strokes = {
            'pen': {
                'color': QColor(0, 0, 0, 255),
                'points': self.pen_points
            }
        }
        '''

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
                
                # if self.viewFlag == 'front':
                #     norm_vec = glm.normalize(hip - sideview)
                #     norm_vec = glm.vec3(-norm_vec.z, norm_vec.y, norm_vec.x)
                # if self.viewFlag == 'side':
                #     norm_vec = glm.normalize(hip - sideview)
                # if self.viewFlag == 'top':
                #     norm_vec = glm.normalize(hip - topview)
                # camera_pos = hip - 150 * norm_vec
                if self.viewFlag == 'top':
                    camera_pos = self.camposTop
                    camera_ground = glm.vec3(0, 0, -1)
                if self.viewFlag == 'front':
                    camera_pos = self.camposFront
                    camera_ground = glm.vec3(0, 75, 0)
                if self.viewFlag == 'side':
                    camera_pos = self.camposSide
                    camera_ground = glm.vec3(0, 75, 0)
                camera_up = glm.vec3(0, 1, 0)
                projection_mat = glm.perspective(60.0 * math.pi / 180.0, 1.0, 1.0, 1000.0) * glm.lookAt(camera_pos, camera_ground, camera_up)

                viewport = glm.vec4(0.0, 0.0, 500.0, 500.0)
                modelview = glm.mat4(1.0)
                # hip_coords = glm.project(glm.vec3(hip), modelview, projection_mat, viewport)
                # self.psets['hip']['points'].append(QPointF(hip_coords.x, 500 - hip_coords.y))

                for keynode in self.keynodes:
                    node = glm.vec3(row[1][f'{keynode}.X'], row[1][f'{keynode}.Y'], row[1][f'{keynode}.Z'])
                    node_coords = glm.project(glm.vec3(node), modelview, projection_mat, viewport)
                    csv_node_traje[keynode].append([node_coords.x, 500 - node_coords.y])
            self.hip_sets.append(csv_node_traje)

    # def readMyCsv(self, path):
    #     # print(path)
    #     csv_input = pd.read_csv(filepath_or_buffer=path, sep=",")
    #     hip_p_matrix = []
    #     hip_points = []
    #     for row in csv_input.iterrows():
    #         hip = glm.vec3(row[1]['hip.X'], row[1]['hip.Y'], row[1]['hip.Z'])

            # if self.viewFlag == 'top':
            #     camera_pos = glm.vec3(0, 400, 0)
            #     camera_ground = glm.vec3(0, 0, -1)
            # if self.viewFlag == 'front':
            #     camera_pos = glm.vec3(300, 100, 0)
            #     camera_ground = glm.vec3(0, 100, 0)
            # if self.viewFlag == 'side':
            #     camera_pos = glm.vec3(0, 100, 300)
            #     camera_ground = glm.vec3(0, 100, 0)

    #         camera_up = glm.vec3(0, 1, 0)
    #         projection_mat = glm.perspective(60.0 * math.pi / 180.0, 1.0, 1.0, 1000.0) * glm.lookAt(camera_pos, camera_ground, camera_up)
    #         viewport = glm.vec4(0.0, 0.0, 500.0, 500.0)
    #         modelview = glm.mat4(1.0)

    #         hip_coords = glm.project(glm.vec3(hip), modelview, projection_mat, viewport)
    #         hip_points.append(QPointF(hip_coords.x, 500 - hip_coords.y))

    #         hip_p_matrix.append([hip_coords.x, 500 - hip_coords.y])

    #     self.hip_sets.append(hip_p_matrix)


    def mousePressEvent(self, event):
        self.pressed = True
        self.retrieving = False
        self.points = []
        self.points.append(event.pos())
        self.drawSketchFlag = None
        self.update()

    def mouseMoveEvent(self, event):
        self.pressed = True
        self.points.append(event.pos())
        # self.pen_points.append(self.points)
        # self.px.append(event.x())
        # self.py.append(event.y())
        self.update()

    def mouseReleaseEvent(self, event):
        self.pressed = False
        self.retrieving = True
        '''
        self.strokes['pen']={
            'color': QColor(0, 0, 0, 255),
            'points': self.points    
        }
        self.drawSketchFlag = True

        # similarity measuring
        query_stroke = np.zeros((len(self.px),2))
        print(len(self.px))
        query_stroke[:,0] = self.px
        query_stroke[:,1] = self.py
        rank = []
        self.px = []
        self.py = []
        
        # ranking by scores
        for hip_stroke in self.hip_sets:
            difference = 0
            difference = similaritymeasures.frechet_dist(query_stroke, hip_stroke)
            # print(difference)
            rank.append(difference)
        self.ranked = np.argsort(rank)
        score = np.sort(rank)
        print(score)
        print(rank)
        print(self.ranked)
        self.best_matched = self.ranked[0] + 1

        # drawing result
        for i in range(len(self.ranked)):
            if i < 5:
                self.csv_input = pd.read_csv(filepath_or_buffer="bvh/from0_worldpos/"+ str(int(self.ranked[i])+1) +"_worldpos.csv", sep=",")
                for row in self.csv_input.iterrows():
                    hip = glm.vec3(row[1]['hip.X'], row[1]['hip.Y'], row[1]['hip.Z'])
                    
                    if self.viewFlag == 'front':
                        camera_pos = glm.vec3(300, 100, 0)
                        camera_ground = glm.vec3(0, 100, 0)
                    if self.viewFlag == 'side':
                        camera_pos = glm.vec3(0, 100, 300)
                        camera_ground = glm.vec3(0, 100, 0)
                    if self.viewFlag == 'top':
                        camera_pos = glm.vec3(0, 400, 0)
                        camera_ground = glm.vec3(-1, 0, 0)
                    camera_up = glm.vec3(0, 1, 0)
                    projection_mat = glm.perspective(60.0 * math.pi / 180.0, 1.0, 1.0, 1000.0) * glm.lookAt(camera_pos, camera_ground, camera_up)

                    viewport = glm.vec4(0.0, 0.0, 500.0, 500.0)
                    modelview = glm.mat4(1.0)

                    hip_coords = glm.project(glm.vec3(hip), modelview, projection_mat, viewport)      
                    self.hip_points.append(QPointF(hip_coords.x, 500 - hip_coords.y))
                    self.hip_p_matrix.append([hip_coords.x, 500 - hip_coords.y])
                self.hip_shadow.append(self.hip_points)
                self.hip_points = []
        self.psets = {
            'hip1': {
                'color': QColor(0, 0, 255, 255),
                'points': self.hip_shadow[0]
            },
            'hip2': {
                'color': QColor(0, 0, 255, 255),
                'points': self.hip_shadow[1]
            },
            'hip3': {
                'color': QColor(0, 0, 255, 255),
                'points': self.hip_shadow[2]
            },
            'hip4': {
                'color': QColor(0, 0, 255, 255),
                'points': self.hip_shadow[3]
            },
            'hip5': {
                'color': QColor(0, 0, 255, 255),
                'points': self.hip_shadow[4]
            },
        }
        # print(len(self.hip_shadow))
        '''
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

                for node_traje in self.hip_sets:
                    to_compare_coords = node_traje['hip']
                    to_compare = np.array(to_compare_coords)
                    difference = similaritymeasures.frechet_dist(query_stroke, to_compare)
                    print(difference)
                    rank.append(difference)
                    self.ranked = np.argsort(rank)

                print(self.ranked)
                # self.best_matched = 1

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
                            camera_pos = glm.vec3(100, 75, 0)
                            camera_ground = glm.vec3(0, 75, 0)
                        if self.viewFlag == 'side':
                            camera_pos = glm.vec3(0, 75, 100)
                            camera_ground = glm.vec3(0, 75, 0)
                        if self.viewFlag == 'top':
                            camera_pos = glm.vec3(0, 150, 0)
                            camera_ground = glm.vec3(-1, 0, 0)
                        camera_up = glm.vec3(0, 1, 0)
                        projection_mat = glm.perspective(60.0 * math.pi / 180.0, 1.0, 1.0, 1000.0) * glm.lookAt(camera_pos, camera_ground, camera_up)

                        viewport = glm.vec4(0.0, 0.0, 500.0, 500.0)
                        modelview = glm.mat4(1.0)

                        for keynode in self.keynodes:
                            node = glm.vec3(row[1][f'{keynode}.X'], row[1][f'{keynode}.Y'], row[1][f'{keynode}.Z'])
                            node_coords = glm.project(glm.vec3(node), modelview, projection_mat, viewport)
                            single_traje[keynode].append(QPointF(node_coords.x, 500 - node_coords.y))

                    for k, v in single_traje.items():
                        painter.setOpacity(0.5)
                        painter.setPen(QColor(*COLORS[k], 255))
                        painter.drawPolyline(*v)
                        painter.setOpacity(1)
            
                self.retrieving = False
        if len(self.ranked) > 0:        
            self.motionFile = self.hParentWidget.bvh_dir + str(self.ranked[0]) + '_n_test.bvh'        
            self.hParentWidget.playFile(self.motionFile)
        # print(self.motionFile)
    '''    
        # draw historical points
        # for k, v in self.psets.items():
        #     # print(k)
        #     painter.setPen(v['color'])
        #     painter.drawPolyline(*v['points'])

        # draw current points
        
        if self.drawSketchFlag:
            # painter.drawPolyline(*self.pen_points)
            for k, v in self.psets.items():
                # print(k)  
                painter.setPen(v['color'])
                painter.setOpacity(0.5)
                painter.drawPolyline(*v['points'])
            for k, v in self.strokes.items():
                # print(k)
                painter.setPen(v['color'])
                painter.setOpacity(1)
                painter.drawPolyline(*v['points']) 
            # self.hip_points = []
            self.hip_shadow = []
        # if self.points:
        #     painter.drawPolyline(*self.points)
    '''
    # def callbk(self):
    #     bestMatched = self.best_matched
    #     return bestMatched

    def frontView(self):
        self.viewFlag = 'front'
    
    def sideView(self):
        self.viewFlag = 'side'
    
    def topView(self):
        self.viewFlag = 'top'

    # # draw current points PENG
    # def paintSketch(self):
    #     painter = QPainter(self)
    #     painter.setPen(Qt.NoPen)
    #     painter.setBrush(Qt.white)
    #     painter.drawRect(self.rect())
    #     for k, v in self.strokes.items():
    #         print(k)
    #         painter.setPen(v['color'])
    #         painter.drawPolyline(*v['points'])