# -*- coding: utf-8 -*-
 
# "BVHPlayerPy" Startup Scripts
# Author: T.Shuhei
# Last Modified: 2017/09/28

import sys
import os
# from ctypes import windll
from PyQt5.Qt import *
from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout
from numpy.lib.arraysetops import ediff1d

from GLWidget import GLWidget
from LocalGLWidget import LocalGLWidget
from InfoWidget import InfoWidget
from ControlWidget import ControlWidget
from Brusher import brusherWidget
# from SplitWidget import SplitWidget
from EditWidget import EditWidget
from paintWidget import PaintWidget
from paintWidgetGlobal import PaintWidgetGlobal
from python_bvh import BVH

import glm
import pandas as pd
import pickle

class BVHPlayerPy(QMainWindow):
    def __init__(self, pathCD):
        super().__init__()
        self.setMaximumSize(800, 600)

        self.infoFont = QFont()
        self.infoFont.setFamily("Times New Rome")
        self.infoFont.setPointSize(12)

        self.uiFont = QFont()
        self.uiFont.setFamily("Arial")
        self.uiFont.setPointSize(12)

        self.bvh_dir = 'bvh/motion/'
        self.csv_pds = []
        self.abspath_list = []
        self.loadDatabase('bvh/from0_worldpos/')
        self.loadHandRotation('bvh/pickle')
        
        self.pathCurrentDir = pathCD
        self.pathMotionFileDir = pathCD.rstrip(os.path.basename(pathCD))
        self.nodeFlag = 'rHand'

        self.setCentralWidget(self.initComponent())
        menuBar = self.menuBar()
        menuBar.setNativeMenuBar(False)

        fileMenu = menuBar.addMenu("&File")
        loadAction = QAction("&Open...", self)
        loadAction.triggered.connect(self.loadFile)
        loadAction.setShortcut("Ctrl+l")
        fileMenu.addAction(loadAction)
        quitAction = QAction("&Quit...", self)
        quitAction.triggered.connect(self.quit)
        quitAction.setShortcut("Ctrl+q")
        fileMenu.addAction(quitAction)
        playAction = QAction("&Play...", self)
        playAction.triggered.connect(self.playFile)
        playAction.setShortcut("Ctrl+b")
        fileMenu.addAction(playAction)
        self.setMenuBar(menuBar)
        self.setWindowTitle("BVH Player")

    def loadHandRotation(self, dir_path):
        self.lhand_rot = pickle.load(open(os.path.join(dir_path, 'lhand_rot_pick.pkl'),'rb'))
        self.rhand_rot = pickle.load(open(os.path.join(dir_path, 'rhand_rot_pick.pkl'),'rb'))

    def loadDatabase(self, dir_path):
        for file in os.listdir(dir_path):
            file_name = os.path.join(dir_path, file)
            self.readMyCsv(file_name)
            motion_file_name = file.split('_')[0] + '.bvh'
            self.abspath_list.append(os.path.join(self.bvh_dir, motion_file_name))
            # rename PENG
            # os.rename(file_name, (path + str(fileid) + '.csv'))
            # fileid = fileid + 1
    
    def readMyCsv(self, path):
        print(path)
        csv_input = pd.read_csv(filepath_or_buffer=path, sep=",")
        self.csv_pds.append(csv_input)

    def initComponent(self):
        self.drawPanel = GLWidget(self)
        self.paintPanel = PaintWidget(self)
        self.paintGlobalPanel = PaintWidgetGlobal(self)
        self.localdrawPanel = LocalGLWidget(self)
        self.infoPanel = InfoWidget(self)
        self.controlPanel = ControlWidget(self)
        self.brusherPanel = brusherWidget(self)
        # self.splitterPanel = SplitWidget(self)
        self.editerPanel = EditWidget(self)

        self.infoPanel.setFont(self.infoFont)
        self.controlPanel.setFont(self.uiFont)
        self.brusherPanel.setFont(self.uiFont)
        self.editerPanel.setFont(self.uiFont)

        # peng 07.21
        editLayout = QVBoxLayout()
        self.globalNameLabel = QLabel()
        self.globalNameLabel.setText(" Global Editing Stage  -----------------------------------")
        editLayout.addWidget(self.globalNameLabel)
        editLayout.addWidget(self.paintGlobalPanel)
        self.localNameLabel = QLabel()
        self.localNameLabel.setText(" Local Editing Stage  ----------------------------------")
        editLayout.addWidget(self.localNameLabel)
        editLayout.addWidget(self.paintPanel)

        viewLayout = QVBoxLayout()
        self.worldNameLabel = QLabel()
        self.worldNameLabel.setText(" World View  ----------------------------------")
        viewLayout.addWidget(self.worldNameLabel)
        viewLayout.addWidget(self.drawPanel)
        self.relativeNameLabel = QLabel()
        self.relativeNameLabel.setText(" Relative View  ----------------------------------")
        viewLayout.addWidget(self.relativeNameLabel)
        viewLayout.addWidget(self.localdrawPanel)

        controlLayout = QVBoxLayout()
        controlLayout.addWidget(self.infoPanel)
        controlLayout.addWidget(self.controlPanel)
        controlLayout.addWidget(self.brusherPanel)
        # controlLayout.addWidget(self.splitterPanel)
        controlLayout.addWidget(self.editerPanel)

        mainLayout = QHBoxLayout()
        mainLayout.addLayout(editLayout)
        mainLayout.addLayout(viewLayout)
        mainLayout.addLayout(controlLayout)
        
        # mainLayout = QHBoxLayout()
        # mainLayout.addWidget(self.paintPanel)
        # mainLayout.addWidget(self.drawPanel)
        # mainLayout.addWidget(self.localdrawPanel)
        # mainLayout.addLayout(controlLayout)

        mainWidget = QWidget()
        mainWidget.setLayout(mainLayout)

        return mainWidget

    def quit(self):
        sys.exit()

    def loadFile(self):
        filePath = QFileDialog.getOpenFileName(self, "Choose Motion File...", self.pathMotionFileDir, "Biovision Hierarchy (*.bvh)")
        if filePath[0] == "":
#            print("Error: Motion file is not given")
            pass
        else:
            root, motion, frames, frameTime = BVH.readBVH(filePath[0])
            self.pathMotionFileDir = os.path.dirname(filePath[0])
            self.drawPanel.setMotion(root, motion, frames, frameTime)
            self.localdrawPanel.setMotion(root, motion, frames, frameTime)
            self.infoPanel.initInfo(os.path.basename(filePath[0]), frameTime, frames)
            self.controlPanel.setPlayMode(True)
            # self.splitterPanel.setActive()
            # self.splitterPanel.initMotionData(os.path.basename(filePath[0]), root, motion, frameTime)

    # PENG
    def playFile(self, filePath):
        # fileNum = self.paintGloblaPanel.callbk()
        # filePath = 'bvh/motion/'+ str(fileNum) + '.bvh' 
        root, motion, frames, frameTime = BVH.readBVH(filePath)
        self.pathMotionFileDir = os.path.dirname(filePath)
        self.drawPanel.setMotion(root, motion, frames, frameTime)
        self.localdrawPanel.setMotion(root, motion, frames, frameTime)
        self.infoPanel.initInfo(os.path.basename(filePath), frameTime, frames)
        self.controlPanel.setPlayMode(True)
        # self.splitterPanel.setActive()
        # self.splitterPanel.initMotionData(os.path.basename(filePath), root, motion, frameTime)

    def setNodeFlag(self, flag):
        assert flag in ['head', 'lHand', 'rHand', 'lFoot', 'rFoot']
        self.nodeFlag = flag

        

    def keyPressEvent(self, event:QKeyEvent):
        if event.key() == Qt.Key_Escape:
            self.quit()
        elif event.key() == Qt.Key_S:
            if self.drawPanel.motion is not None:
                self.drawPanel.isPlaying = not self.drawPanel.isPlaying
                self.controlPanel.setPlayMode(self.drawPanel.isPlaying)
        elif event.key() == Qt.Key_F:
            self.drawPanel.fastRatio *= 2.0
        elif event.key() == Qt.Key_D:
            self.drawPanel.fastRatio /= 2.0
        elif event.key() == Qt.Key_Right:
            if self.drawPanel.frames is not None:
                self.drawPanel.frameCount += 1
                if self.drawPanel.frameCount >= self.drawPanel.frames:
                    self.drawPanel.frameCount = 0
        elif event.key() == Qt.Key_Left:
            if self.drawPanel.frames is not None:
                self.drawPanel.frameCount -= 1
                if self.drawPanel.frameCount < 0:
                    self.drawPanel.frameCount = self.drawPanel.frames - 1
        else:
            pass
        

if __name__ == "__main__":
    if getattr(sys, "frozen", False):
        pathCD = os.path.dirname(sys.executable)
    else:
        pathCD = os.path.dirname(__file__)

    # user32 = windll.user32
    # user32.SetProcessDPIAware()
    app = QApplication(sys.argv)
    player = BVHPlayerPy(pathCD)
    player.show()
    sys.exit(app.exec_())