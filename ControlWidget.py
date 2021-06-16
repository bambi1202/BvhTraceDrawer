# -*- coding: utf-8 -*-

# "BVHPlayerPy" Player control components
# Author: T.Shuhei
# Last Modified: 2017/09/28

# Using these icon resource:
# https://vmware.github.io/clarity/icons/icon-sets#core-shapes
# 
# Clarity is licensed under the MIT License.  
# https://github.com/vmware/clarity/blob/master/LICENSE  
# 

import os
from PyQt5.QtWidgets import QHBoxLayout
import numpy as np
import pickle
from PyQt5.Qt import *

class ControlWidget(QGroupBox):
    fPlayMode = False
    hParentWidget = None

    def __init__(self, parent=None):
        super().__init__(parent)
        self.hParentWidget = parent
        self.pathResourceDir = os.path.join(parent.pathCurrentDir, "IconResource")
        self.setTitle("Control")
        self.setFixedSize(500,150)
        self.xy = 0
        self.zy = 0
        self.zx = 0

        playerLayout = QHBoxLayout()
        self.rewindButton = _createButton("rewind", 60, self.rewindButtonAction, os.path.join(self.pathResourceDir, "rewind-solid.svg"))
        playerLayout.addWidget(self.rewindButton)
        self.rewindButton.setEnabled(False)
        self.rewindButton.setFocusPolicy(Qt.NoFocus)


        self.playButton = _createButton("play", 60, self.playButtonAction, os.path.join(self.pathResourceDir, "play-solid.svg"))
        playerLayout.addWidget(self.playButton)
        self.playButton.setEnabled(False)
        self.playButton.setFocusPolicy(Qt.NoFocus)
        
        self.pauseButton = _createButton("pause", 60, self.playButtonAction, os.path.join(self.pathResourceDir, "pause-solid.svg"))
        playerLayout.addWidget(self.pauseButton)
        self.pauseButton.setVisible(False)
        self.pauseButton.setFocusPolicy(Qt.NoFocus)

        self.stopButton = _createButton("stop", 60, self.stopButtonAction, os.path.join(self.pathResourceDir, "stop-solid.svg"))
        playerLayout.addWidget(self.stopButton)
        self.stopButton.setEnabled(False)
        self.stopButton.setFocusPolicy(Qt.NoFocus)

        self.forwardButton = _createButton("forward", 60, self.forwardButtonAction, os.path.join(self.pathResourceDir, "fast-forward-solid.svg"))
        playerLayout.addWidget(self.forwardButton)
        self.forwardButton.setEnabled(False)
        self.forwardButton.setFocusPolicy(Qt.NoFocus)

        # draw mode
        self.drawButton = _createButton("draw", 60, self.drawButtonAction, os.path.join(self.pathResourceDir, "curve-chart-line.svg"))
        playerLayout.addWidget(self.drawButton)
        self.drawButton.setEnabled(True)
        self.drawButton.setFocusPolicy(Qt.NoFocus)
        

        # view mode
        self.viewButton = _createButton("view", 60, self.viewButtonAction, os.path.join(self.pathResourceDir, "cursor-move-line.svg"))
        playerLayout.addWidget(self.viewButton)
        self.viewButton.setEnabled(False)
        self.viewButton.setFocusPolicy(Qt.NoFocus)




        camCtlLayout = QHBoxLayout()
        self.camResetButton = _createButton("Camera Reset", 200, self.hParentWidget.drawPanel.resetCamera)
        camCtlLayout.addWidget(self.camResetButton)
        self.camResetButton.setFocusPolicy(Qt.NoFocus)
        # slider 06.16
        self.canvasButton = _createButton("showCanvas", 200, self.hParentWidget.drawPanel.canvasShow)
        camCtlLayout.addWidget(self.canvasButton)
        self.canvasButton.setFocusPolicy(Qt.NoFocus)

        sliderLayout = QHBoxLayout()
        self.initrotationxy = QSlider(Qt.Horizontal)
        sliderLayout.addWidget(self.initrotationxy)
        self.initrotationxy.setRange(-250,250)
        self.initrotationxy.setFocusPolicy(Qt.NoFocus)
        self.initrotationxy.valueChanged.connect(self.initrotationxyUpdate)

        self.initrotationzy = QSlider(Qt.Horizontal)
        sliderLayout.addWidget(self.initrotationzy)
        self.initrotationzy.setRange(-250,250)
        self.initrotationzy.setFocusPolicy(Qt.NoFocus)
        self.initrotationzy.valueChanged.connect(self.initrotationzyUpdate)

        self.initrotationzx = QSlider(Qt.Horizontal)
        sliderLayout.addWidget(self.initrotationzx)
        self.initrotationzx.setRange(50,150)
        self.initrotationzx.setFocusPolicy(Qt.NoFocus)
        self.initrotationzx.valueChanged.connect(self.initrotationzxUpdate)
        
        switchLayout = QHBoxLayout()
        self.zxButton = _createButton("zxCanvas", 150, self.hParentWidget.drawPanel.zxSwitch)
        switchLayout.addWidget(self.zxButton)
        self.zxButton.setFocusPolicy(Qt.NoFocus)

        self.zyButton = _createButton("zyCanvas", 150, self.hParentWidget.drawPanel.zySwitch)
        switchLayout.addWidget(self.zyButton)
        self.zyButton.setFocusPolicy(Qt.NoFocus)

        self.xyButton = _createButton("xyCanvas", 150, self.hParentWidget.drawPanel.xySwitch)
        switchLayout.addWidget(self.xyButton)
        self.xyButton.setFocusPolicy(Qt.NoFocus)
        

        mainLayout = QVBoxLayout()
        mainLayout.addLayout(playerLayout)
        mainLayout.addLayout(camCtlLayout)
        mainLayout.addLayout(sliderLayout)
        mainLayout.addLayout(switchLayout)
        self.setLayout(mainLayout)

    def initrotationxyUpdate(self,value):
        self.xy = value
        xy = self.xy
        pickfile = open('csv/xy.pkl','wb')
        pickle.dump(xy, pickfile)
        pickfile.close()    

    def initrotationzyUpdate(self,value):
        self.zy = value
        zy = self.zy
        pickfile = open('csv/zy.pkl','wb')
        pickle.dump(zy, pickfile)
        pickfile.close()    

    def initrotationzxUpdate(self,value):
        self.zx = value
        zx = self.zx
        pickfile = open('csv/zx.pkl','wb')
        pickle.dump(zx, pickfile)
        pickfile.close()   

        

    def setPlayMode(self, fPlay):
        self.setActive()
        self.fPlayMode = fPlay
        if self.fPlayMode:
            self.playButton.setVisible(False)
            self.pauseButton.setVisible(True)
        else:
            self.pauseButton.setVisible(False)
            self.playButton.setVisible(True)
        
    def setActive(self):
        self.forwardButton.setEnabled(True)
        self.rewindButton.setEnabled(True)
        self.playButton.setEnabled(True)
        self.pauseButton.setEnabled(True)
        self.stopButton.setEnabled(True)
        
        

    def playButtonAction(self):
        self.fPlayMode = not self.fPlayMode
        self.hParentWidget.drawPanel.fastRatio = 1.0
        if self.fPlayMode:
            self.playButton.setVisible(False)
            self.pauseButton.setVisible(True)
            self.hParentWidget.drawPanel.isPlaying = True
        else:
            self.pauseButton.setVisible(False)
            self.playButton.setVisible(True)
            self.hParentWidget.drawPanel.isPlaying = False
            self.hParentWidget.drawPanel.InitisPlaying = True
    
    def stopButtonAction(self):
        self.fplayMode = False
        self.hParentWidget.drawPanel.isPlaying = False
        self.pauseButton.setVisible(False)
        self.playButton.setVisible(True)
        self.hParentWidget.drawPanel.frameCount = 0
        self.hParentWidget.drawPanel.fastRatio = 1.0

    def rewindButtonAction(self):
        if self.fPlayMode:
            if self.hParentWidget.drawPanel.fastRatio > 0:
                self.hParentWidget.drawPanel.fastRatio = -1.0
            else:
                self.hParentWidget.drawPanel.fastRatio *= 2.0
        else:
            self.hParentWidget.drawPanel.frameCount -= 1

    def forwardButtonAction(self):
        if self.fPlayMode:
            if self.hParentWidget.drawPanel.fastRatio < 0:
                self.hParentWidget.drawPanel.fastRatio = 1.0
            else:
                self.hParentWidget.drawPanel.fastRatio *= 2.0
        else:
            self.hParentWidget.drawPanel.frameCount += 1

    # draw mode
    def drawButtonAction(self):
        self.hParentWidget.drawPanel.drawline = True
        self.hParentWidget.drawPanel.viewmode = False
        self.viewButton.setEnabled(True)

    def viewButtonAction(self):
        self.hParentWidget.drawPanel.viewmode = True
        self.hParentWidget.drawPanel.drawline = False
        # self.drawButton.setEnabled(False)

    def canvasButtonAction(self):
        self.canvasButton.setEnabled(False)

## Support Functions
def _createButton(title, width, func, iconPath = None):
    if iconPath is None:
        button = QPushButton(title)
    else:
        button = QPushButton()
        button.setIcon(QIcon(QPixmap(iconPath)))

    button.setFixedWidth(width)
    button.clicked.connect(func)
    return button