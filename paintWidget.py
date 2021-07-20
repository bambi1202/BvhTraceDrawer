import numpy as np
import time

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

class PaintWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.hParentWidget = parent
        self.setMinimumSize(500, 500)
        self.csv_input = pd.read_csv(filepath_or_buffer="../bvh/from0_worldpos/141_2_n_worldpos.csv", sep=",")
        
        hip_points = []
        head_points = []
        rButtock_points = []
        for row in self.csv_input.iterrows():
            hip = glm.vec3(row[1]['hip.X'], row[1]['hip.Y'], row[1]['hip.Z'])
            rButtock = glm.vec3(row[1]['rButtock.X'], row[1]['rButtock.Y'], row[1]['rButtock.Z'])
            head = glm.vec3(row[1]['rHand.X'], row[1]['rHand.Y'], row[1]['rHand.Z'])
            norm_vec = glm.normalize(hip - rButtock)
            camera_pos = hip - norm_vec * 200
            camera_up = glm.vec3(0, 1.0, 0)
            projection_mat = glm.perspective(60.0 * math.pi / 180.0, 1.0, 1.0, 1000.0) * glm.lookAt(camera_pos, hip, camera_up)
            # print(projection_mat)
            viewport = glm.vec4(0.0, 0.0, 500.0, 500.0)
            modelview = glm.mat4(1.0)
            head_coords = glm.project(glm.vec3(head), modelview, projection_mat, viewport)
            hip_coords = glm.project(glm.vec3(hip), modelview, projection_mat, viewport)
            hip_points.append(QPointF(hip_coords.x, 500 - hip_coords.y))
            head_points.append(QPointF(head_coords.x, 500 - head_coords.y))
        self.px = None
        self.py = None
        self.points = []
        self.psets = {
            'head': {
                'color': QColor(255, 0, 0, 255),
                'points': head_points
            },
            'hip': {
                'color': QColor(0, 0, 255, 255),
                'points': hip_points
            }
        }
        # print(self.psets)
        

    # def mousePressEvent(self, event):
    #     self.points.append(event.pos())
    #     self.update()

    # def mouseMoveEvent(self, event):
    #     self.points.append(event.pos())
    #     self.update()

    # def mouseReleaseEvent(self, event):
    #     self.pressed = False
    #     self.psets.append(self.points)
    #     self.points = []
    #     self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setPen(Qt.NoPen)
        painter.setBrush(Qt.white)
        painter.drawRect(self.rect())
        

        # draw historical points
        for k, v in self.psets.items():
            # print(k)
            painter.setPen(v['color'])
            painter.drawPolyline(*v['points'])

        # # draw current points
        # if self.points:
        #     painter.drawPolyline(*self.points)