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
from pickle import TRUE
import numpy as np
from PyQt5.Qt import *

class EditWidget(QGroupBox):
    fPlayMode = False
    hParentWidget = None

    def __init__(self, parent=None):
        super().__init__(parent)
        self.hParentWidget = parent
        self.pathResourceDir = os.path.join(parent.pathCurrentDir, "IconResource")
        self.setTitle("Local Motion Editor")

        headLayout = QHBoxLayout()
        self.headButton = _createButton("Head Node", 150, 100, self.headButtonAction)
        headLayout.addWidget(self.headButton)
        self.headButton.setEnabled(True)

        # LR Inverse?
        handLayout = QHBoxLayout()
        self.lhandButton = _createButton("Left Hand Node", 150, 100, self.lhandButtonAction)
        handLayout.addWidget(self.lhandButton)
        self.lhandButton.setEnabled(True)
        self.rhandButton = _createButton("Right Hand Node", 150, 100, self.rhandButtonAction)
        handLayout.addWidget(self.rhandButton)
        self.rhandButton.setEnabled(False)
        
        

        footLayout = QHBoxLayout()
        self.lfootButton = _createButton("Left foot Node", 150, 100, self.lfootButtonAction)
        footLayout.addWidget(self.lfootButton)
        self.lfootButton.setEnabled(True)
        self.rfootButton = _createButton("Right foot Node", 150, 100, self.rfootButtonAction)
        footLayout.addWidget(self.rfootButton)
        self.rfootButton.setEnabled(True)
        

        mainLayout = QVBoxLayout()
        mainLayout.addLayout(headLayout)
        mainLayout.addLayout(handLayout)
        mainLayout.addLayout(footLayout)
        # mainLayout.addLayout(camCtlLayout)
        # mainLayout.addLayout(canvasCtlLayout)
        self.setLayout(mainLayout)

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

    def frontViewButtonAction(self):
        self.frontViewButton.setEnabled(False)
        self.sideViewButton.setEnabled(True)
        self.topViewButton.setEnabled(True)
        self.hParentWidget.paintGloblaPanel.frontView()

    def sideViewButtonAction(self):
        self.frontViewButton.setEnabled(True)
        self.sideViewButton.setEnabled(False)
        self.topViewButton.setEnabled(True)
        self.hParentWidget.paintGloblaPanel.sideView()

    def topViewButtonAction(self):
        self.frontViewButton.setEnabled(True)
        self.sideViewButton.setEnabled(True)
        self.topViewButton.setEnabled(False)
        self.hParentWidget.paintGloblaPanel.topView()

    def headButtonAction(self):
        self.headButton.setEnabled(False)
        self.lhandButton.setEnabled(True)
        self.rhandButton.setEnabled(True)
        self.lfootButton.setEnabled(True)
        self.rfootButton.setEnabled(True)
        self.hParentWidget.setNodeFlag('head')
    
    def rhandButtonAction(self):
        self.headButton.setEnabled(True)
        self.lhandButton.setEnabled(True)
        self.rhandButton.setEnabled(False)
        self.lfootButton.setEnabled(True)
        self.rfootButton.setEnabled(True)
        self.hParentWidget.setNodeFlag('rHand')

    def lhandButtonAction(self):
        self.headButton.setEnabled(True)
        self.lhandButton.setEnabled(False)
        self.rhandButton.setEnabled(True)
        self.lfootButton.setEnabled(True)
        self.rfootButton.setEnabled(True)
        self.hParentWidget.setNodeFlag('lHand')

    def rfootButtonAction(self):
        self.headButton.setEnabled(True)
        self.lhandButton.setEnabled(True)
        self.rhandButton.setEnabled(True)
        self.lfootButton.setEnabled(True)
        self.rfootButton.setEnabled(False)
        self.hParentWidget.setNodeFlag('rFoot')

    def lfootButtonAction(self):
        self.headButton.setEnabled(True)
        self.lhandButton.setEnabled(True)
        self.rhandButton.setEnabled(True)
        self.lfootButton.setEnabled(False)
        self.rfootButton.setEnabled(True)   
        self.hParentWidget.setNodeFlag('lFoot')         


    def playButtonAction(self):
        self.fPlayMode = not self.fPlayMode
        self.hParentWidget.drawPanel.fastRatio = 1.0
        if self.fPlayMode:
            self.playButton.setVisible(False)
            self.pauseButton.setVisible(True)
            self.hParentWidget.drawPanel.isPlaying = True
            self.hParentWidget.localdrawPanel.isPlaying = True
        else:
            self.pauseButton.setVisible(False)
            self.playButton.setVisible(True)
            self.hParentWidget.drawPanel.isPlaying = False
            self.hParentWidget.localdrawPanel.isPlaying = False
    
    def stopButtonAction(self):
        self.fplayMode = False
        self.hParentWidget.drawPanel.isPlaying = False
        self.hParentWidget.localdrawPanel.isPlaying = False
        self.pauseButton.setVisible(False)
        self.playButton.setVisible(True)
        self.hParentWidget.drawPanel.frameCount = 0
        self.hParentWidget.drawPanel.fastRatio = 1.0
        self.hParentWidget.localdrawPanel.frameCount = 0
        self.hParentWidget.localdrawPanel.fastRatio = 1.0

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

## Support Functions
def _createButton(title, width, height ,func, iconPath = None):
    if iconPath is None:
        button = QPushButton(title)
    else:
        button = QPushButton()
        button.setIcon(QIcon(QPixmap(iconPath)))

    button.setFixedWidth(width)
    button.setFixedHeight(height)
    button.clicked.connect(func)
    return button