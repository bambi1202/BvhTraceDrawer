# -*- coding: utf-8 -*-

# "BVHPlayerPy" OpenGL drawing component
# Author: T.Shuhei
# Last Modified: 2017/09/28

import numpy as np
import time
import cv2
import math
import scipy.linalg as linalg

from PyQt5.Qt import *
from OpenGL.GL import *
from OpenGL.GLU import *

from python_bvh import BVHNode

class GLWidget(QOpenGLWidget):
    frameChanged = pyqtSignal(int)
    hParentWidget = None
    checkerBoardSize = 50
    camDist = 500
    floorObj = None
    rotateXZ = 0
    rotateY = 45
    translateX = 0
    translateY = 0
    frameCount = 0
    isPlaying = True
    fastRatio = 1.0
    scale = 1.0
    root = None
    motion = None
    frames = None
    frameTime = None
    drawMode = 0    # 0:rotation, 1:position

    # draw mode
    drawline = False
    viewmode = True

    def __init__(self, parent=None):
        super().__init__(parent)
        self.hParentWidget = parent
        self.setMinimumSize(500, 500)
        self.lastPos = QPoint()

        # Set stroke
        self.mouRelease = True
        self.mouPress = False
        self.pos_move = False
        self.stroke_posX = []
        self.stroke_posY = []
        self.last_stroke_pos = []

        self.rotate_axisX = [1,0,0]
        self.rotate_axisY = [0,1,0]
        self.rotate_axisZ = [0,0,1]
        self.rot_posx = [0,0,0]
        self.rot_posy = [0,0,0]
        self.rot_posz = [0,0,0]

        # Set trace
        self.jointX = []
        self.jointY = []
        self.jointZ = []

    def resetCamera(self):
        self.rotateXZ = 0
        self.rotateY = 45
        self.translateX = 0
        self.translateY = 0
        self.camDist = 500

    def setMotion(self, root:BVHNode, motion, frames:int, frameTime:float):
        self.root = root
        self.motion = motion
        self.frames = frames
        self.frameTime = frameTime
        self.frameCount = 0
        self.isPlaying = True

        self.jointpos = [[]]
        # print(np.shape(self.jointpos))
        # print(self.jointpos)
        # print(self.root)

    def initializeGL(self):
        glEnable(GL_DEPTH_TEST)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_CONSTANT_ALPHA)
        glEnable(GL_BLEND)
        glClearColor(0.2, 0.2, 0.2, 0)
        self.floorObj = self.makeFloorObject(0)
        self.start = time.time()

    def updateFrame(self):
        if (self.frames is not None) and (self.frameTime is not None):
            now = time.time()
            if self.isPlaying:
                # print(self.motion[self.frameCount][0])
                jointpos_cur = [self.motion[self.frameCount][0],
                                self.motion[self.frameCount][1],
                                self.motion[self.frameCount][2]]
                self.jointpos.append(jointpos_cur)
                # print(np.shape(self.jointpos))
                # print(self.jointpos)
                

                self.frameCount += int(1 * self.fastRatio) if abs(self.fastRatio) >= 1.0 else 1
                
                if self.frameCount >= self.frames:
                    self.frameCount = 0
                    self.jointpos = [[]]
                elif self.frameCount < 0:
                    self.frameCount = self.frames - 1
                self.frameChanged.emit(self.frameCount)
                
        self.drawStroke()
        self.update()
        self.hParentWidget.infoPanel.updateFrameCount(self.frameCount)

    def paintGL(self):
        # glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        # glViewport(0, 0, 500, 500)
        glMatrixMode(GL_PROJECTION)
        
        glLoadIdentity()
        qs = self.sizeHint()
        gluPerspective(60.0, float(qs.width()) / float(qs.height()), 1.0, 10000.0)
        camPx = self.camDist * np.cos(self.rotateXZ / 180.0)
        camPy = self.camDist * np.tanh(self.rotateY / 180.0)
        camPz = self.camDist * np.sin(self.rotateXZ / 180.0)
        transX = self.translateX * -np.sin(self.rotateXZ / 180.0)
        transZ = self.translateX * np.cos(self.rotateXZ / 180.0)

        # print(camPz)
        # print(transX, self.translateY, transZ)

        '''
        # Current camare matrix (R T, 0 1)
        camera_matrix, rvec, tvec = camera_params()
        # (R T, 0 1)
        trans_matrix = np.hstack((rvec, [[tvec[0]], [tvec[1]], [tvec[2]]]))
        temp = np.dot(camera_matrix, trans_matrix)
        pp = np.linalg.pinv(temp)

        # test point
        test_point = np.array([605, 341, 1], np.float)
        print("world pos:", p1)

        X =np.dot(pp, test_point)
        print("X:", X)

        X1 = np.array(X[:3], np.float)/X[3]
        print("X1:". X1)
        '''    

        gluLookAt(camPx + transX, camPy + self.translateY, camPz + transZ, 
                  transX, self.translateY, transZ,
                  0.0, 1.0, 0.0)
        # if self.isPlaying == False:
        #     gluLookAt(camPx + transX, camPy + self.translateY, camPz + transZ, 
        #             transX, self.translateY, transZ,
        #             0.0, 1.0, 0.0)
        # if self.isPlaying:
        #     gluLookAt(camPx + transX, camPy + self.translateY, camPz + transZ, 
        #             self.motion[self.frameCount][0], self.motion[self.frameCount][1], self.motion[self.frameCount][2],
        #             0.0, 1.0, 0.0)

        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glCallList(self.floorObj)
        self.drawSkeleton()
        glPopMatrix()
        glFlush()
        self.drawStroke()
#        self.update()
        self.updateFrame()

    # rotation function
    def rotate_mat(self, axis, radian):
        rot_matrix = linalg.expm(np.cross(np.eye(3), axis / linalg.norm(axis) * radian))
        return rot_matrix

    def drawSkeleton(self):
        def _RenderBone(quadObj, x0, y0, z0, x1, y1, z1):
            dir = [x1 - x0, y1 - y0, z1 - z0]
            boneLength = np.sqrt(dir[0]**2 + dir[1]**2 + dir[2]**2)
            # print(x1, y1, z1)
            self.jointX.append(x1)
            self.jointY.append(y1)
            self.jointZ.append(z1)
   

            if quadObj is None:
                quadObj = GLUQuadric()
            gluQuadricDrawStyle(quadObj, GLU_FILL)
            gluQuadricNormals(quadObj, GLU_SMOOTH)

            glPushMatrix()
            glTranslated(x0, y0, z0)

            length = np.sqrt(dir[0]**2 + dir[1]**2 + dir[2]**2)
            if length < 0.0001:
                dir = [0.0, 0.0, 1.0]
                length = 1.0
            dir = [data / length for data in dir]            
            
#            up   = [0.0, 1.0, 0.0]
#            side = [up[1]*dir[2] - up[2]*dir[1], up[2]*dir[0] - up[0]*dir[2], up[0]*dir[1] - up[1]*dir[0]]
            side = [dir[2], 0.0, -dir[0]]
            length = np.sqrt(side[0]**2 + side[1]**2 + side[2]**2)
            if length < 0.0001:
                side = [1.0, 0.0, 0.0]
                length = 1.0
            side = [data / length for data in side]

            up = [dir[1]*side[2] - dir[2]*side[1], dir[2]*side[0] - dir[0]*side[2], dir[0]*side[1] - dir[1]*side[0]]
            glMultMatrixd((side[0], side[1], side[2], 0.0,
                             up[0],   up[1],   up[2], 0.0,
                            dir[0],  dir[1],  dir[2], 0.0,
                               0.0,     0.0,     0.0, 1.0))
            # print(dir)
            radius = 1.5
            slices = 8
            stack = 1
            # gluCylinder(quadObj, radius, radius, boneLength, slices, stack)
            glPopMatrix()

        def _RenderJoint(quadObj):
            if quadObj is None:
                quadObj = GLUQuadric()
            gluQuadricDrawStyle(quadObj, GLU_FILL)
            gluQuadricNormals(quadObj, GLU_SMOOTH)

            if self.drawMode == 0:  # rotation mode
                glColor3f(1.000, 0.271, 0.000)
            else:                   # position mode
                glColor3f(0.000, 1.052, 0.000)

            gluSphere(quadObj, 3.0, 16, 16)            

            if self.drawMode == 0:  # rotation mode
                glColor3f(1.000, 0.549, 0.000)
            else:                   # position mode
                glColor3f(0.000, 1.000, 0.000)

        def _RenderFigure(node:BVHNode):
            quadObj = None
            # print(node.site)
            
            glPushMatrix()
            if self.drawMode == 0:
                # Translate
                if node.nodeIndex == 0:     # ROOT
                    glTranslatef(self.motion[self.frameCount][0] * self.scale,
                                 self.motion[self.frameCount][1] * self.scale,
                                 self.motion[self.frameCount][2] * self.scale)
                    # glTranslatef(0,0,0)
                    # print(self.motion[self.frameCount][0] * self.scale)
                    # print(np.shape(self.motion))    

                # general key node  
                elif node.nodeIndex == 1:
                    glTranslatef(node.offset[0] * self.scale, node.offset[1] * self.scale, node.offset[2] * self.scale)
                elif node.nodeIndex == 2:
                    glTranslatef(node.offset[0] * self.scale, node.offset[1] * self.scale, node.offset[2] * self.scale)
                elif node.nodeIndex == 3:
                    glTranslatef(node.offset[0] * self.scale, node.offset[1] * self.scale, node.offset[2] * self.scale)
                elif node.nodeIndex == 4:
                    glTranslatef(node.offset[0] * self.scale, node.offset[1] * self.scale, node.offset[2] * self.scale)               
                
                # Head
                elif node.nodeIndex == 5:
                    glTranslatef(node.offset[0] * self.scale, node.offset[1] * self.scale, node.offset[2] * self.scale)
                    # print(node.offset[0] * self.scale, node.offset[1] * self.scale, node.offset[2] * self.scale)
                    _RenderJoint(quadObj)
                
                elif node.nodeIndex == 6:
                    glTranslatef(node.offset[0] * self.scale, node.offset[1] * self.scale, node.offset[2] * self.scale)
                elif node.nodeIndex == 7:
                    glTranslatef(node.offset[0] * self.scale, node.offset[1] * self.scale, node.offset[2] * self.scale)
                elif node.nodeIndex == 8:
                    glTranslatef(node.offset[0] * self.scale, node.offset[1] * self.scale, node.offset[2] * self.scale)                
                
                # Left hand
                elif node.nodeIndex == 9:
                    glTranslatef(node.offset[0] * self.scale, node.offset[1] * self.scale, node.offset[2] * self.scale)
                    _RenderJoint(quadObj)
                    # print(node.offset[0] * self.scale, node.offset[1] * self.scale, node.offset[2] * self.scale)

                elif node.nodeIndex == 10:
                    glTranslatef(node.offset[0] * self.scale, node.offset[1] * self.scale, node.offset[2] * self.scale)
                elif node.nodeIndex == 11:
                    glTranslatef(node.offset[0] * self.scale, node.offset[1] * self.scale, node.offset[2] * self.scale)
                elif node.nodeIndex == 12:
                    glTranslatef(node.offset[0] * self.scale, node.offset[1] * self.scale, node.offset[2] * self.scale)

                # Right hand 
                elif node.nodeIndex == 13:
                    glTranslatef(node.offset[0] * self.scale, node.offset[1] * self.scale, node.offset[2] * self.scale)
                    _RenderJoint(quadObj)
                
                elif node.nodeIndex == 14:
                    glTranslatef(node.offset[0] * self.scale, node.offset[1] * self.scale, node.offset[2] * self.scale)
                elif node.nodeIndex == 15:
                    glTranslatef(node.offset[0] * self.scale, node.offset[1] * self.scale, node.offset[2] * self.scale)

                # Left foot    
                elif node.nodeIndex == 16:
                    glTranslatef(node.offset[0] * self.scale, node.offset[1] * self.scale, node.offset[2] * self.scale)
                    _RenderJoint(quadObj)

                elif node.nodeIndex == 17:
                    glTranslatef(node.offset[0] * self.scale, node.offset[1] * self.scale, node.offset[2] * self.scale)
                elif node.nodeIndex == 18:
                    glTranslatef(node.offset[0] * self.scale, node.offset[1] * self.scale, node.offset[2] * self.scale)
                elif node.nodeIndex == 19:
                    glTranslatef(node.offset[0] * self.scale, node.offset[1] * self.scale, node.offset[2] * self.scale)
                        
                # Right foot
                elif node.nodeIndex == 20:
                    glTranslatef(node.offset[0] * self.scale, node.offset[1] * self.scale, node.offset[2] * self.scale) 
                    _RenderJoint(quadObj)
                
                elif node.nodeIndex == 21:
                    glTranslatef(node.offset[0] * self.scale, node.offset[1] * self.scale, node.offset[2] * self.scale)
                       
                '''  
                # general node     
                else:   
                    glTranslatef(node.offset[0] * self.scale, node.offset[1] * self.scale, node.offset[2] * self.scale)
                    # glTranslatef(1.0, 1.0, 1.0)
                    # print(node.offset[0])
                '''    

                    # _RenderJoint(quadObj)
                # Rotation
                
                for i, channel in enumerate(node.chLabel):
                    # print(node.chLabel)
                    if "Xrotation" in channel:
                        glRotatef(self.motion[self.frameCount][node.frameIndex + i], 1.0, 0.0, 0.0)
                        # print(self.motion[self.frameCount][node.frameIndex + i])
                        rot_matrix = self.rotate_mat(self.rotate_axisX, self.motion[self.frameCount][node.frameIndex + i])
                        pos = [node.offset[0] * self.scale, node.offset[1] * self.scale, node.offset[2] * self.scale]
                        self.rot_posx = np.dot(rot_matrix, pos)
                        # print(pos)
                        # print(rot_posx)

                        # print(self.motion[self.frameCount][node.frameIndex + i])

                        # print(self.frameCount, node.nodeIndex)
                    elif "Yrotation" in channel:
                        glRotatef(self.motion[self.frameCount][node.frameIndex + i], 0.0, 1.0, 0.0)
                        rot_matrix = self.rotate_mat(self.rotate_axisY, self.motion[self.frameCount][node.frameIndex + i])
                        self.rot_posy = np.dot(rot_matrix, self.rot_posx)
                        # print(self.frameCount, node.nodeIndex)
                    elif "Zrotation" in channel:
                        glRotatef(self.motion[self.frameCount][node.frameIndex + i], 0.0, 0.0, 1.0)
                        rot_matrix = self.rotate_mat(self.rotate_axisZ, self.motion[self.frameCount][node.frameIndex + i])
                        self.rot_posz = np.dot(rot_matrix, self.rot_posy)
                        print(self.rot_posz)

                        # print(self.frameCount, node.nodeIndex)
                    glColor3f(0.4,0.1,0.2)
                    glPointSize(5)
                    glBegin(GL_POINTS)
                    glVertex3f(self.rot_posz[0],self.rot_posz[1],self.rot_posz[2])
                    glEnd()
                # Drawing Links
                if node.fHaveSite:
                    _RenderBone(quadObj, 0.0, 0.0, 0.0, node.site[0] * self.scale, node.site[1] * self.scale, node.site[2] * self.scale)
                # for child in node.childNode:
                    # _RenderBone(quadObj, 0.0, 0.0, 0.0, child.offset[0] * self.scale, child.offset[1] * self.scale, child.offset[2] * self.scale)
                '''
                # draw trace
                if len(self.jointX) > 1:
                    glColor3f(0.4,0.1,0.2) 
                    glBegin(GL_LINES)
                    for i in range(len(self.jointX)):

                        glVertex3d(self.jointX[i],
                                   self.jointY[i], 
                                   self.jointZ[i])
                        glVertex3d(self.jointX[i-1], 
                                   self.jointX[i-1], 
                                   self.jointX[i-1])
                    glEnd()
                '''
                # Drawing Joint Sphere
                # _RenderJoint(quadObj)
                # print(quadObj)

                # Child drawing
                for child in node.childNode:
                    _RenderFigure(child)
            glPopMatrix()

        # drawSkeleton Main Codes
        if (self.root is not None) and (self.motion is not None):
            if self.drawMode == 0:  # rotation mode
                glColor3f(1.000, 0.549, 0.000)
            else:                   # position mode
                glColor3f(0.000, 1.000, 0.000)
            _RenderFigure(self.root)
        pass



    def makeFloorObject(self, height):
        size = 50
        num = 20
        genList = glGenLists(1)
        glNewList(genList, GL_COMPILE)
        glBegin(GL_QUADS)
        for j in range(-int(num/2), int(num/2)+1):
            glNormal(0.0, 1.0, 0.0)
            for i in range(-int(num/2), int(num/2)+1):
                if (i + j) % 2 == 0:
                    glColor3f(0.4, 0.4, 0.4)
                else:
                    glColor3f(0.2, 0.2, 0.2)
                glVertex3i(i*size, height, j*size)
                glVertex3i(i*size, height, j*size+size)
                glVertex3i(i*size+size, height, j*size+size)
                glVertex3i(i*size+size, height, j*size)
        glEnd()
        glEndList()
        return genList


    def drawStroke(self):
        if self.drawline == True:
            if self.mouPress == True:
                self.stroke_posX.append(self.lastPos.x())
                self.stroke_posY.append(self.lastPos.y())
                # print(self.stroke_posX, self.stroke_posY)

            # if self.pos_move == True:
            #     for i in range(len(self.stroke_posX)):

            #         self.last_stroke_pos.append((self.stroke_posX[i], self.stroke_posY[i]))
            #         print(self.last_stroke_pos)

            # if self.mouRelease == True:
            #     if len(self.stroke_posX) > 1:
            #         glColor3f(0.4,0.1,0.2) 
            #         glBegin(GL_LINES)
            #         for i in range(len(self.stroke_posX)):

            #             glVertex3d(self.stroke_posX[i],self.stroke_posY[i],self.camDist * np.sin(self.rotateXZ / 180.0)*0.3)
            #             glVertex3d(self.stroke_posX[i-1],self.stroke_posY[i-1],self.camDist * np.sin(self.rotateXZ / 180.0)*0.3)
            #         glEnd()
        if self.mouRelease == True:
                if len(self.stroke_posX) > 1:
                    glColor3f(0.4,0.1,0.2) 
                    glBegin(GL_LINES)
                    for i in range(len(self.stroke_posX)):

                        glVertex3d(self.camDist * np.sin(self.rotateXZ / 180.0)*0.5+100,
                                   500 - self.stroke_posY[i]-200, 
                                   500 - self.stroke_posX[i]-300)
                        glVertex3d(self.camDist * np.sin(self.rotateXZ / 180.0)*0.5+100, 
                                   500 - self.stroke_posY[i-1]-200, 
                                   500 - self.stroke_posX[i-1]-300)
                    glEnd()    
        # if len(self.last_stroke_pos):


    ## Mouse & Key Events
    def mousePressEvent(self, event:QMouseEvent):
        self.lastPos = event.pos()
        self.mouPress = True
        self.mouRelease = False

    def mouseReleaseEvent(self, event:QMouseEvent):
        self.mouRelease = True
        self.mouPress = False

    def mouseMoveEvent(self, event:QMouseEvent):
        dx = event.x() - self.lastPos.x()
        dy = event.y() - self.lastPos.y()

        # draw mode mouse movement
        mx = dx
        my = dy

        if mx != 0 and my !=0:
            self.pos_move = True
            mx = 0
            my = 0
        elif mx == 0 and my ==0:
            self.pos_move = False

        if self.drawline == False:
            if event.buttons() & Qt.LeftButton:
                self.rotateXZ += dx
                self.rotateY  += dy

        if event.buttons() & Qt.RightButton:
            self.translateX += dx
            self.translateY += dy
        self.lastPos = event.pos()
        self.drawStroke()
        self.update()

    def wheelEvent(self, event:QWheelEvent):
        angle = event.angleDelta()
        steps = angle.y() / 8.0

        self.camDist -= steps
        if self.camDist < 1:
            self.camDist = 1
        elif self.camDist > 750:
            self.camDist = 750
        self.drawStroke()
        self.update()

#    def keyPressEvent(self, event:QKeyEvent):
#        if event.key() == Qt.Key_Escape:
#            self.parent().quit()
#        elif event.key() == Qt.Key_S:
#            self.isPlaying = not self.isPlaying
#        elif event.key() == Qt.Key_F:
#            self.fastRatio *= 2.0
#        elif event.key() == Qt.Key_D:
#            self.fastRatio /= 2.0
#        elif event.key() == Qt.Key_Right:
#            self.frameCount += 1
#        elif event.key() == Qt.Key_Left:
#            self.frameCount -= 1
#        else:
#            None
#        self.update()