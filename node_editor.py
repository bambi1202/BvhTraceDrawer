import csv
import numpy as np
import os
import pandas as pd
import pickle

from python_bvh import BVH, BVHNode

# root_dir = "testbvh/"
# csv_stroke = []
# pick_globalTrace = []

# with open('bvh/pickle/lhand_rot_pick.pkl','rb') as file:
#     lhand_rot = pickle.load(file)
# with open('bvh/pickle/rhand_rot_pick.pkl','rb') as file:
#     rhand_rot = pickle.load(file)
# print(jointrot[18][0][1])

# rhand_rank = 2
# lhand_rank = 18

class NodeEditor:
    def __init__(self, lhand_rot, rhand_rot):
        self.lhand_rot = lhand_rot
        self.rhand_rot = rhand_rot

    def editBVH(self, bvhAbsPath, lhand_rank, rhand_rank):
        u'''Read BVH file and parse to each parts
        return tuple of (RootNode, MotionSeries, Frames, FrameTime)
        '''

        with open(bvhAbsPath) as bvhFile:
            # "HIERARCHY"part
            hierarchyStack = []
            nodeIndex = 0
            frameIndex = 0
            tmpNode = None

            motionInFrame = []
            motionSeries = []
            rootMotion = []
            newMotionSeries = []

            for line in bvhFile:
                # cutting line terminator
                line = line.rstrip("\n")
                line = line.rstrip("\r")

                # parse BVH Hierarcy
                if "{" in line:
                    hierarchyStack.append(tmpNode)
                    tmpNode = newNode
                    continue
                if "}" in line:
                    tmpNode = hierarchyStack.pop()
                    continue
                if ("JOINT" in line) or ("ROOT" in line):
                    newNode = BVHNode(line.rsplit(None, 1)[1], nodeIndex, frameIndex)
                    nodeIndex += 1
                    if tmpNode != None:
                        tmpNode.addChild(newNode)
                    else:
                        tmpNode = newNode
                    continue
                if "OFFSET" in line:
                    if tmpNode.fHaveSite == True:
                        tmpNode.site.extend([float(data) for data in line.split(None, 3)[1:]])
                    else:
                        tmpNode.offset.extend([float(data) for data in line.split(None, 3)[1:]])
                    continue
                if "CHANNELS" in line:
                    tmpNode.chLabel.extend(line.split(None, 7)[2:])
                    frameIndex += len(tmpNode.chLabel)
                    # print(frameIndex)
                    continue
                if "End Site" in line:
                    tmpNode.fHaveSite = True
                    continue
                if "MOTION" in line:
                    break
            else:
                raise ValueError("This File is not BVH Motion File.")

            isNewLine = lambda string: not string.rstrip("\n").rstrip("\r")
            
            # get frames "Frames: xxx"
            line = bvhFile.readline()
            while isNewLine(line):
                line = bvhFile.readline()
            frmNum = int(line.rsplit(None, 1)[1])
            len_frame = frmNum
            globalTrace = np.zeros((len_frame,3))

            # get frameTime "Frame Time: x.xx"
            line = bvhFile.readline()
            while isNewLine(line):
                line = bvhFile.readline()
            frmTime = float(line.rsplit(None, 1)[1])

            # get "MOTION"part (List of List)
            # peng
            for line in bvhFile: 
                if not isNewLine(line):
                    motionInFrame = []
                    for data in line.split():
                        # print(line.split())
                        motionInFrame.append(float(data))
                    # print(motionInFrame)
                    motionSeries.append(motionInFrame)
                # print(len(motionSeries)) 

            for f in range(len(motionSeries)):
                # print(len(motionSeries))
                mif = motionSeries[f]
                for i in range(len(mif)):
                    # 07.13
                    # 727
                    # if rhand_rank == 0:
                    #     if i < 8*3:
                    #         rootMotion.append(mif[i])
                        
                    #     if i == 8*3:
                    #         rootMotion.append(self.rhand_rot[rhand_rank][f][0])
                    #     elif i == 8*3+1:
                    #         rootMotion.append(self.rhand_rot[rhand_rank][f][1])
                    #     elif i == 8*3+2:
                    #         rootMotion.append(self.rhand_rot[rhand_rank][f][2])
                    #     elif i == 8*3+3:
                    #         rootMotion.append(self.rhand_rot[rhand_rank][f][3])
                    #     elif i == 8*3+4:
                    #         rootMotion.append(self.rhand_rot[rhand_rank][f][4])
                    #     elif i == 8*3+5:
                    #         rootMotion.append(self.rhand_rot[rhand_rank][f][5])
                    #     elif i == 8*3+6:
                    #         rootMotion.append(self.rhand_rot[rhand_rank][f][6])
                    #     elif i == 8*3+7:
                    #         rootMotion.append(self.rhand_rot[rhand_rank][f][7])
                    #     elif i == 8*3+8:
                    #         rootMotion.append(self.rhand_rot[rhand_rank][f][8])

                    #     if i > 8*3+8 and i < 22*3:
                    #         rootMotion.append(mif[i])
                    #     if i > 22*3 - 1 and i < 22*3 + 9:
                    #         rootMotion.append(0.0)
                    #     if i > 22*3+8:
                    #         rootMotion.append(mif[i])
                    # else:        
                        ####
                    if i < 8*3:
                        rootMotion.append(mif[i])
                        
                    if i == 8*3:
                        rootMotion.append(self.rhand_rot[rhand_rank][f][0])
                    elif i == 8*3+1:
                        rootMotion.append(self.rhand_rot[rhand_rank][f][1])
                    elif i == 8*3+2:
                        rootMotion.append(self.rhand_rot[rhand_rank][f][2])
                    elif i == 8*3+3:
                        rootMotion.append(self.rhand_rot[rhand_rank][f][3])
                    elif i == 8*3+4:
                        rootMotion.append(self.rhand_rot[rhand_rank][f][4])
                    elif i == 8*3+5:
                        rootMotion.append(self.rhand_rot[rhand_rank][f][5])
                    elif i == 8*3+6:
                        rootMotion.append(self.rhand_rot[rhand_rank][f][6])
                    elif i == 8*3+7:
                        rootMotion.append(self.rhand_rot[rhand_rank][f][7])
                    elif i == 8*3+8:
                        rootMotion.append(self.rhand_rot[rhand_rank][f][8])

                    if i > 8*3+8 and i < 22*3:
                        rootMotion.append(mif[i])

                    if i == 22*3:
                        rootMotion.append(self.lhand_rot[lhand_rank][f][0])
                    elif i == 22*3+1:
                        rootMotion.append(self.lhand_rot[lhand_rank][f][1])
                    elif i == 22*3+2:
                        rootMotion.append(self.lhand_rot[lhand_rank][f][2])
                    elif i == 22*3+3:
                        rootMotion.append(self.lhand_rot[lhand_rank][f][3])
                    elif i == 22*3+4:
                        rootMotion.append(self.lhand_rot[lhand_rank][f][4])
                    elif i == 22*3+5:
                        rootMotion.append(self.lhand_rot[lhand_rank][f][5])
                    elif i == 22*3+6:
                        rootMotion.append(self.lhand_rot[lhand_rank][f][6])
                    elif i == 22*3+7:
                        rootMotion.append(self.lhand_rot[lhand_rank][f][7])
                    elif i == 22*3+8:
                        rootMotion.append(self.lhand_rot[lhand_rank][f][8])
                       
                    if i > 22*3+8:
                        rootMotion.append(mif[i])
                    
                newMotionSeries.append(rootMotion)
                # print(len(rootMotion))
                rootMotion = []
            # print(len(motionSeries))
            # print(motionInFrame)          
            
            dstFilePath = os.path.join("bvh/output/" + os.path.basename(bvhAbsPath).split(".")[0] + "_edited" + ".bvh")
            # print(dstFilePath)
            BVH.writeBVH(dstFilePath, tmpNode, newMotionSeries, frmNum, frmTime)

            '''
                    motionSeries.append(motionInFrame)
                    globalTraceX.append(motionInFrame[0])
                    globalTraceY.append(motionInFrame[1])
                    globalTraceZ.append(motionInFrame[2])
                    print(len(motionInFrame))
                    motionInFrame = []
            globalTrace[:, 0] = globalTraceX
            globalTrace[:, 1] = globalTraceY
            globalTrace[:, 2] = globalTraceZ
            pick_globalTrace.append(globalTrace)
            '''
                
            # motionSeries = [([float(data) for data in line.split()] if not isNewLine(line) else None) for line in bvhFile]
            
            try:
                while True:
                    motionSeries.remove(None)
                    # motionSeries.remove([])
            except ValueError:
                pass

        return tmpNode, motionSeries, frmNum, frmTime

# class BVHNode:
#     u'''BVH Skeleton Joint Structure'''
#     def __init__(self, nodeName, nodeIndex, frameIndex):
#         self.nodeName = nodeName
#         self.nodeIndex = nodeIndex
#         self.frameIndex = frameIndex
#         self.offset = []
#         self.chLabel = []
#         self.childNode = []
#         self.fHaveSite = False
#         self.site = []

#     def addChild(self, childNode):
#         u'''add child joint'''
#         self.childNode.append(childNode)

#     def getChannelIndex(self, channelName):
#         u'''return non-negative index 0, 1, ..., or None(Error) '''
#         try:
#             return self.chLabel.index(channelName)
#         except ValueError:
#             return None

#     def getNodeI(self, index):
#         u'''return BVHNode instanse or None(Error)'''
#         if index == self.nodeIndex:
#             return self
#         if self.fHaveSite:
#             return None
#         for node in self.childNode:
#             retNode = node.getNode(index)
#             if retNode != None:
#                 return retNode

#     def getNodeN(self, name):
#         u'''return BVHNode instanse or None(Error)'''
#         node = None
#         if name == self.nodeName:
#             return self
#         else:
#             for child in self.childNode:
#                 node = child.getNodeN(name)
#                 if node is not None:
#                     return node
#         return None

#     def getNodeList(self):
#         u'''return list of BVHNode (element order : order of appearance in the BVH file)'''
#         nodelist = [self]
#         if self.fHaveSite:
#             return nodelist
#         for child in self.childNode:
#             nodelist.extend(child.getNodeList())
#         return nodelist

# for file in os.listdir(root_dir):
#     file_name = root_dir + file
#     # print(file_name)
#     filein = open(file_name,"r")
#     readBVH(file_name)

# # peng
# tocsv = pd.DataFrame(csv_stroke)
# tocsv.to_csv("csv/global.csv")

# pickfile = open('csv/test_pick.pkl','wb')
# pickle.dump(csv_stroke, pickfile)
# pickfile.close()
'''
# 06.16
pickfile = open('csv/test_pick.pkl','wb')
pickle.dump(pick_globalTrace, pickfile)
pickfile.close()
'''

# with open('csv/test_pick.pkl','rb') as file:
#     pkl_stroke = pickle.load(file)
# print(pkl_stroke[0])