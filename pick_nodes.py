import csv
import numpy as np
import os
import pandas as pd
import pickle

from python_bvh import BVH

root_dir = "bvh/motion/"
csv_stroke = []
pick_globalTrace = []
l_hand_set = []
r_hand_set = []

def readBVH(bvhAbsPath):
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
        globalTraceX = []
        globalTraceZ = []
        globalTraceY = []

        globalTrace = []

        globalstroke = []

        normal = []
        rootMotion = []
        normalMotion = []

        newMotionSeries = []


        # 07.13
        l_sld_x = []
        l_sld_y = []
        l_sld_z = []
        l_arm_x = []
        l_arm_y = []
        l_arm_z = []
        l_hnd_x = []
        l_hnd_y = []
        l_hnd_z = []
        l_hand = np.zeros((100,9))

        r_sld_x = []
        r_sld_y = []
        r_sld_z = []
        r_arm_x = []
        r_arm_y = []
        r_arm_z = []
        r_hnd_x = []
        r_hnd_y = []
        r_hnd_z = []
        r_hand = np.zeros((100,9))

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
                # 1st frame
                # if f == 0:
                #     # normal.append(mif[i])
                #     if i < 3 and i != 1:
                #         normal.append(mif[i]) # normal x z position
                #         rootMotion.append(0.0) # init x z position
                #     if i == 1 :
                #         normal.append(0.0) # normal y position
                #         rootMotion.append(mif[i]) # init y position
                #     if i > 2:
                #         rootMotion.append(mif[i])
                # 2nd frame ~       
                # if i < 3 and f > 0:
                #     rootMotion.append(mif[i] - normal[i])
                # if i > 2 and f > 0:
                #     rootMotion.append(mif[i])
                if i==8*3:
                    r_sld_x.append(mif[i])
                if i==8*3+1:
                    r_sld_y.append(mif[i])
                if i==8*3+2:
                    r_sld_z.append(mif[i])
                if i==8*3+3:
                    r_arm_x.append(mif[i])
                if i==8*3+4:
                    r_arm_y.append(mif[i])
                if i==8*3+5:
                    r_arm_z.append(mif[i])
                if i==8*3+6:
                    r_hnd_x.append(mif[i])
                if i==8*3+7:
                    r_hnd_y.append(mif[i])
                if i==8*3+8:
                    r_hnd_z.append(mif[i])

                if i==22*3:
                    l_sld_x.append(mif[i])
                if i==22*3+1:
                    l_sld_y.append(mif[i])
                if i==22*3+2:
                    l_sld_z.append(mif[i])
                if i==22*3+3:
                    l_arm_x.append(mif[i])
                if i==22*3+4:
                    l_arm_y.append(mif[i])
                if i==22*3+5:
                    l_arm_z.append(mif[i])
                if i==22*3+6:
                    l_hnd_x.append(mif[i])
                if i==22*3+7:
                    l_hnd_y.append(mif[i])
                if i==22*3+8:
                    l_hnd_z.append(mif[i])
            # print(normal)        
            # print(rootMotion)
            newMotionSeries.append(rootMotion)
            # print(len(rootMotion))
            rootMotion = []
        # print(len(l_sld_x))
        r_hand[:,0] = r_sld_x[0:100]
        r_hand[:,1] = r_sld_y[0:100]
        r_hand[:,2] = r_sld_z[0:100]
        r_hand[:,3] = r_arm_x[0:100]
        r_hand[:,4] = r_arm_y[0:100]
        r_hand[:,5] = r_arm_z[0:100]
        r_hand[:,6] = r_hnd_x[0:100]
        r_hand[:,7] = r_hnd_y[0:100]
        r_hand[:,8] = r_hnd_z[0:100]

        l_hand[:,0] = l_sld_x[0:100]
        l_hand[:,1] = l_sld_y[0:100]
        l_hand[:,2] = l_sld_z[0:100]
        l_hand[:,3] = l_arm_x[0:100]
        l_hand[:,4] = l_arm_y[0:100]
        l_hand[:,5] = l_arm_z[0:100]
        l_hand[:,6] = l_hnd_x[0:100]
        l_hand[:,7] = l_hnd_y[0:100]
        l_hand[:,8] = l_hnd_z[0:100]
        
        r_hand_set.append(r_hand)
        l_hand_set.append(l_hand)
        print(len(r_hand_set))
        pickfile = open('bvh/pickle/lhand_rot_pick.pkl','wb')
        pickle.dump(l_hand_set, pickfile)
        pickfile.close()

        rpickfile = open('bvh/pickle/rhand_rot_pick.pkl','wb')
        pickle.dump(r_hand_set, rpickfile)
        rpickfile.close()

        # print(len(motionSeries))
        # print(motionInFrame)          
        
        # dstFilePath = os.path.join("0726_n/" + file.split(".")[0] + "_n" + ".bvh")
        # print(dstFilePath)

        # 07.13
        # BVH.writeBVH(dstFilePath, tmpNode, newMotionSeries, 100, frmTime)
        # BVH.writeBVH(dstFilePath, tmpNode, newMotionSeries[1:], frmNum-1, frmTime)

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

class BVHNode:
    u'''BVH Skeleton Joint Structure'''
    def __init__(self, nodeName, nodeIndex, frameIndex):
        self.nodeName = nodeName
        self.nodeIndex = nodeIndex
        self.frameIndex = frameIndex
        self.offset = []
        self.chLabel = []
        self.childNode = []
        self.fHaveSite = False
        self.site = []

    def addChild(self, childNode):
        u'''add child joint'''
        self.childNode.append(childNode)

    def getChannelIndex(self, channelName):
        u'''return non-negative index 0, 1, ..., or None(Error) '''
        try:
            return self.chLabel.index(channelName)
        except ValueError:
            return None

    def getNodeI(self, index):
        u'''return BVHNode instanse or None(Error)'''
        if index == self.nodeIndex:
            return self
        if self.fHaveSite:
            return None
        for node in self.childNode:
            retNode = node.getNode(index)
            if retNode != None:
                return retNode

    def getNodeN(self, name):
        u'''return BVHNode instanse or None(Error)'''
        node = None
        if name == self.nodeName:
            return self
        else:
            for child in self.childNode:
                node = child.getNodeN(name)
                if node is not None:
                    return node
        return None

    def getNodeList(self):
        u'''return list of BVHNode (element order : order of appearance in the BVH file)'''
        nodelist = [self]
        if self.fHaveSite:
            return nodelist
        for child in self.childNode:
            nodelist.extend(child.getNodeList())
        return nodelist

for file in os.listdir(root_dir):
    file_name = root_dir + file
    # print(file_name)
    filein = open(file_name,"r")
    readBVH(file_name)

# peng
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