import sys
from PyQt5.QtWidgets import QMainWindow,QApplication,QWidget,QMessageBox,QLineEdit,QInputDialog,QFileDialog,QColorDialog,QFontDialog,QLabel,QPushButton,QVBoxLayout,QStyle,QAction
from PyQt5.QtGui import QIcon,QPixmap,QPainter,QPen,QColor,QBrush,QFont
from PyQt5.QtCore import Qt,QRect


# from PyQt5.Qt import *
import math
import numpy as np
import csv
import pandas as pd
import pickle
import similaritymeasures

sys.setrecursionlimit(3000)

class mylable(QLabel):
    fPlayMode = False
    hParentWidget = None
    def __init__(self,parent=None):
        super().__init__(parent)
        self.hParentWidget = parent
        self.pixmap = QPixmap(500, 498)#考虑边框的间距 减去px
        self.pixmap.fill(Qt.white)
        self.setStyleSheet("border: 2px solid red")
        self.Color=Qt.blue#pen color: defult:blue
        self.penwidth=4#pen width : default:4

        self.x0 = 0
        self.y0 = 0
        self.x1 = 0
        self.y1 = 0
        self.flag = False

        self.queryx = []
        self.queryy = []
        self.point = []
        self.query_stroke = []
        

        self.csvfile = open("csv/global.csv")
        self.reader = csv.reader(self.csvfile)
        self.csv_stroke = []
        self.dictio = {}

        self.pkl_stroke = []
        self.one_stroke = []
        with open('csv/test_pick.pkl','rb') as file:
            self.pkl_stroke = pickle.load(file)
        # print(self.pkl_stroke[2])

        # self.df = pd.read_csv('csv/global.csv', skiprows = 1, header = None)
        # print(self.df)
    def paintEvent(self,event):
        super().paintEvent(event)
        # self.pixmap.fill(Qt.white)
        painter=QPainter(self.pixmap)
        painter.setPen(QPen(self.Color,self.penwidth,Qt.SolidLine))
        painter.drawLine(self.x0, self.y0, self.x1, self.y1)

        Label_painter=QPainter(self)
        Label_painter.drawPixmap(2,2,self.pixmap)

    def mousePressEvent(self, event):
        self.x1=event.x()
        self.y1=event.y()
        self.flag=True

    def mouseMoveEvent(self, event):
        if self.flag:
            self.x0 = self.x1
            self.y0 = self.y1
            self.x1 = event.x()
            self.y1 = event.y()

            # 06.16
            self.queryx.append(self.x1)
            self.queryy.append(self.y1)
            

            self.point = (self.x1-250, self.y1-250)
            self.query_stroke.append(self.point)
            self.update()
        # print(self.query_stroke)
    def mouseReleaseEvent(self, event):
        self.flag=False
        # 06.16
    
        self.test_stroke =- np.zeros((len(self.queryx),3))
        self.test_stroke[:,0] = self.queryx
        self.test_stroke[:,1] = self.queryy
        # print(self.test_stroke)        

        pickfile = open('csv/teststk_pick.pkl','wb')
        pickle.dump(self.test_stroke, pickfile)
        pickfile.close()

        with open('csv/test_pick.pkl','rb') as file:
            pkl_stroke = pickle.load(file)
        for i in range(len(pkl_stroke)):
            df = similaritymeasures.frechet_dist(self.test_stroke, pkl_stroke[i])
            print(df)


        ''' 
        for row in self.reader:
            if self.reader.line_num == 1:
                continue
            for col in row:
                if col:
                    self.csv_stroke.append(col)
            self.dictio[self.reader.line_num - 1] = self.csv_stroke
            self.csv_stroke = []
        '''    
        # print(type(self.dictio[32])
        # for row in self.df:
        #     # for i in range(len(row)):
        #     #     self.csv_stroke.append(row[i])
        #     print(row)
        # for i in range(len(self.dictio)):
        #     self.dictio[i+1].remove(str(i))
        #     similarity_res = self.frechet_distance(self.query_stroke, self.dictio[i+1])
        #     print(similarity_res)

        res_ttl = []
        res_rank = []
        num_rank = []
        '''
        for i in range(len(self.pkl_stroke)):
            similarity_res = self.frechet_distance(self.query_stroke, self.pkl_stroke[i])
            # print(similarity_res)
            res_ttl.append(similarity_res)
        res_rank = sorted(res_ttl)
        print(res_rank)
        for i in range(len(res_ttl)):
            if res_rank[0] == res_ttl[i]:
                num_rank.append(i+1)
            if res_rank[1] == res_ttl[i]:
                num_rank.append(i+1)
            if res_rank[2] == res_ttl[i]:
                num_rank.append(i+1)
            if res_rank[3] == res_ttl[i]:
                num_rank.append(i+1)
            if res_rank[4] == res_ttl[i]:
                num_rank.append(i+1)
        print(num_rank)
        pickfile = open('csv/rank_fln.pkl','wb')
        pickle.dump(num_rank, pickfile)
        pickfile.close()
        '''
        # print(self.query_stroke)
        # self.query_stroke = []

    def euc_dist(self, pt1, pt2):
        return math.sqrt((pt2[0]-pt1[0])*(pt2[0]-pt1[0])+(pt2[1]-pt1[1])*(pt2[1]-pt1[1]))

    def calculation(self, ca,i,j,P,Q):
        if ca[i,j] > -1:
            return ca[i,j]
        elif i == 0 and j == 0:
            ca[i,j] = self.euc_dist(P[0],Q[0])
        elif i > 0 and j == 0:
            ca[i,j] = max(self.calculation(ca,i-1,0,P,Q),self.euc_dist(P[i],Q[0]))
        elif i == 0 and j > 0:
            ca[i,j] = max(self.calculation(ca,0,j-1,P,Q),self.euc_dist(P[0],Q[j]))
        elif i > 0 and j > 0:
            ca[i,j] = max(min(self.calculation(ca,i-1,j,P,Q),self.calculation(ca,i-1,j-1,P,Q),self.calculation(ca,i,j-1,P,Q)),self.euc_dist(P[i],Q[j]))
        else:
            ca[i,j] = float("inf")
        return ca[i,j]

    def frechet_distance(self, P,Q):
        ca = np.ones((len(P),len(Q)))
        ca = np.multiply(ca,-1)
        return self.calculation(ca, len(P) - 1, len(Q) - 1, P, Q)



'''
class cb(QMainWindow):
    def __init__(self):
        super(cb,self).__init__()
        self.initUi()
        
    def initUi(self):
        self.resize(800,600)
        vbox=QVBoxLayout()
        #选择绘画文件 按钮
        self.button_file=QPushButton(self)
        self.button_file.setGeometry(660,80,100,50)
        self.button_file.setText("File")
        self.button_file.setFont(QFont("Chiller",20))
        vbox.addWidget(self.button_file)
        vbox.addStretch()
        #选择画笔颜色 按钮
        self.button_color=QPushButton(self)
        self.button_color.setGeometry(660,270,100,50)
        self.button_color.setText("Color")
        self.button_color.setFont(QFont("Chiller",20))
        vbox.addWidget(self.button_color)
        vbox.addStretch()
        #选择画笔粗细 按钮
        self.button_width=QPushButton(self)
        self.button_width.setGeometry(660,460,100,50)
        self.button_width.setText("Width")
        self.button_width.setFont(QFont("Chiller",20))
        vbox.addWidget(self.button_width)
        vbox.addStretch()
        #设置画板
        self.lb=mylable(self)
        self.lb.setGeometry(20, 40, 601, 501)
        #橡皮
        eraser=QAction(QIcon("1239616.png"),"Eraser",self)
        eraser.setToolTip("Eraser")
        #工具栏
        self.menubar=self.addToolBar("ToolBar")
        self.menubar.addAction(eraser)
        #主页面
        self.setWindowIcon(QIcon("1216867.png"))
        self.setWindowTitle("Drawing Board")
        
        self.button_file.clicked.connect(self.openfile)
        self.button_color.clicked.connect(self.choose_color)
        eraser.triggered.connect(self.erase)
        self.button_width.clicked.connect(self.choose_width)

    def openfile(self):
        fname=QFileDialog.getOpenFileName(self,"选择图片文件",".")
        if fname[0]:
            self.lb.pixmap=QPixmap(fname[0])

    def choose_color(self):
        Color=QColorDialog.getColor()#color是Qcolor
        if Color.isValid():
            self.lb.Color=Color

    def erase(self):
        self.lb.Color=Qt.white
        self.lb.setCursor(Qt.CrossCursor)
        self.lb.penwidth=self.lb.penwidth+2

    def choose_width(self):
        width, ok = QInputDialog.getInt(self, '选择画笔粗细', '请输入粗细：',min=1,step=1)
        if ok:
            self.lb.penwidth=width

if __name__ == '__main__':
    app=QApplication(sys.argv)
    mainwindow=cb()
    mainwindow.show()
    sys.exit(app.exec_())
'''