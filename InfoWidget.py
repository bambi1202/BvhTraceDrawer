# -*- coding: utf-8 -*-

# "BVHPlayerPy" Current BVH file info & Playing frame info
# Author: T.Shuhei
# Last Modified: 2017/09/28

import numpy as np
from PyQt5.Qt import *

class InfoWidget(QGroupBox):
    def __init__(self, parent = None):
        super().__init__(parent)
        self.hParentWidget = parent
        # self.font = QFont()
        # self.font.setFamily("Arial")
        # self.font.setPointSize(18)

        mainLayout = QVBoxLayout()
        self.fileNameLabel = QLabel()
        self.frameRateLabel = QLabel()
        
        tipsInfoLayout = QVBoxLayout()
        tipsRow = QLabel()
        tipsRow.setText("Please start from drawing root motion.")
        tipsInfoLayout.addWidget(tipsRow)

        worldCamInfoLayout = QHBoxLayout()
        worldCamName = QLabel()
        worldCamName.setText("Global Canvas View :")
        worldCamInfoLayout.addWidget(worldCamName)
        self.worldCamMod = QLabel()
        worldCamInfoLayout.addWidget(self.worldCamMod)

        relativeCamInfoLayout = QHBoxLayout()
        relativeCamName = QLabel()
        relativeCamName.setText("Local Canvas View :")
        relativeCamInfoLayout.addWidget(relativeCamName)
        self.relativeCamMod = QLabel()
        relativeCamInfoLayout.addWidget(self.relativeCamMod)

        frameInfoLayout = QHBoxLayout()
        frameRowName = QLabel()
        frameRowName.setText("Frame :")
        frameInfoLayout.addWidget(frameRowName)
        self.frameCounter = QLabel()
        frameInfoLayout.addWidget(self.frameCounter)
        self.framesLabel = QLabel()
        frameInfoLayout.addWidget(self.framesLabel)

        mainLayout.addLayout(tipsInfoLayout)
        mainLayout.addLayout(worldCamInfoLayout)
        mainLayout.addLayout(relativeCamInfoLayout)
        mainLayout.addLayout(frameInfoLayout)
        mainLayout.addWidget(self.fileNameLabel)
        mainLayout.addWidget(self.frameRateLabel)
        
        self.initInfo("-  [Empty]", 0, 1)
        self.loadFlag()

        self.setLayout(mainLayout)

    def loadFlag(self):
        self.Flag = self.hParentWidget.paintPanel.viewFlag
        self.worldCamMod.setText(self.Flag)
        self.relativeCamMod.setText(self.Flag)

    def initInfo(self, fileName, frameTime, frames):
        if frameTime == 0:
            frameRate = 0
        else:
            frameRate = np.round(1.0 / frameTime, 2)

        self.fileNameLabel.setText("Best Matched Skeleton File : " + fileName)
        self.frameRateLabel.setText("Frame Rate : " + str(frameRate) + " fps.") 
        self.framesLabel.setText(" / " + str(frames - 1))
        self.resetFrameCount()

    def updateFrameCount(self, frameCount):
        self.frameCounter.setText(str(frameCount))
    
    def resetFrameCount(self):
        self.frameCount = 0
        self.frameCounter.setText(str(0))
