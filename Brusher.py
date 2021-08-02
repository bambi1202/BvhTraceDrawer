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

class brusherWidget(QGroupBox):
    fPlayMode = False
    hParentWidget = None

    def __init__(self, parent=None):
        super().__init__(parent)
        self.hParentWidget = parent
        self.pathResourceDir = os.path.join(parent.pathCurrentDir, "IconResource")
        self.setTitle("Paint Tool")

        canvas = QVBoxLayout()
        canvasName = QLabel()
        canvasName.setText('Select a Canvas')

        canvasCtlLayout = QHBoxLayout()
        self.frontViewButton = _createButton("Front View", 100 , 60, self.frontViewButtonAction)
        canvasCtlLayout.addWidget(self.frontViewButton)
        self.frontViewButton.setEnabled(True)
        self.frontViewButton.setFocusPolicy(Qt.NoFocus)

        self.sideViewButton = _createButton("Side View", 100 , 60, self.sideViewButtonAction)
        canvasCtlLayout.addWidget(self.sideViewButton)
        self.sideViewButton.setEnabled(True)
        self.sideViewButton.setFocusPolicy(Qt.NoFocus)

        self.topViewButton = _createButton("Top View", 100 , 60, self.topViewButtonAction)
        canvasCtlLayout.addWidget(self.topViewButton)
        self.topViewButton.setEnabled(False)
        self.topViewButton.setFocusPolicy(Qt.NoFocus)
        
        brusherLayout = QHBoxLayout()
        brusherName = QLabel()
        brusherName.setText('Brush')

        self.undoButton = _createButton("Undo", 60 , 60, self.undoAction)
        self.undoButton.setEnabled(True)
        self.undoButton.setFocusPolicy(Qt.NoFocus)

        self.redoButton = _createButton("Redo", 60 , 60, self.redoAction)
        self.redoButton.setEnabled(True)
        self.redoButton.setFocusPolicy(Qt.NoFocus)

        self.saveButton = _createButton("Save", 60 , 60, self.saveAction)
        self.saveButton.setEnabled(True)
        self.saveButton.setFocusPolicy(Qt.NoFocus)

        self.loadButton = _createButton("Load", 60 , 60, self.loadAction)
        self.loadButton.setEnabled(True)
        self.loadButton.setFocusPolicy(Qt.NoFocus)
        
        brusherLayout.addWidget(self.undoButton)
        brusherLayout.addWidget(self.redoButton)
        brusherLayout.addWidget(self.saveButton)
        brusherLayout.addWidget(self.loadButton)

        canvas.addWidget(brusherName)
        canvas.addLayout(brusherLayout)
        canvas.addWidget(canvasName)
        canvas.addLayout(canvasCtlLayout)
        mainLayout = QVBoxLayout()
        mainLayout.addLayout(canvas)
        self.setLayout(mainLayout)

    def frontViewButtonAction(self):
        self.frontViewButton.setEnabled(False)
        self.sideViewButton.setEnabled(True)
        self.topViewButton.setEnabled(True)
        self.hParentWidget.paintGlobalPanel.frontView()
        self.hParentWidget.infoPanel.loadFlag()

    def sideViewButtonAction(self):
        self.frontViewButton.setEnabled(True)
        self.sideViewButton.setEnabled(False)
        self.topViewButton.setEnabled(True)
        self.hParentWidget.paintGlobalPanel.sideView()
        self.hParentWidget.infoPanel.loadFlag()

    def topViewButtonAction(self):
        self.frontViewButton.setEnabled(True)
        self.sideViewButton.setEnabled(True)
        self.topViewButton.setEnabled(False)
        self.hParentWidget.paintGlobalPanel.topView()
        self.hParentWidget.infoPanel.loadFlag()     

    def undoAction(self):
        print('Undo')

    def redoAction(self):
        print('Redo')
        
    def saveAction(self):
        print('Saved')

    def loadAction(self):
        print('Loaded')

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