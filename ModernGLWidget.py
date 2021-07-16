
  
import numpy as np
import moderngl

from utils.qtmoderngl import QModernGLWidget
from camera import Camera
from pyrr import Matrix44, Quaternion, Vector3, vector
import sys

from PyQt5 import QtWidgets
from PyQt5.Qt import pyqtSignal

from python_bvh import BVHNode, getNodeRoute

class HelloWorld2D:
    def __init__(self, ctx, reserve='4MB'):
        self.ctx = ctx
        self.camera = Camera(1)
        self.prog = self.ctx.program(
            vertex_shader='''
                #version 330

                uniform mat4 Mvp;

                in vec3 in_vert;

                void main() {
                    gl_Position = Mvp * vec4(in_vert, 1.0);
                }
            ''',
            fragment_shader='''
                #version 330

                out vec4 f_color;

                void main() {
                    f_color = vec4(0.1, 0.1, 0.1, 1.0);
                }
            ''',
        )
        self.mvp = self.prog['Mvp']

        self.vbo = ctx.buffer(reserve='4MB', dynamic=True)
        self.vao = ctx.simple_vertex_array(self.prog, self.vbo, 'in_vert')

    def pan(self, camera):
        self.prog['Mvp'].write((camera.mat_projection * camera.mat_lookat).astype('f4'))

    def clear(self, color=(0, 0, 0, 0)):
        self.ctx.clear(*color)

    def plot(self, points, type='line'):
        data = points.astype('f4').tobytes()
        self.ctx.clear(1.0, 1.0, 1.0)
        self.ctx.enable(moderngl.DEPTH_TEST)
        self.prog['Mvp'].write((self.camera.mat_projection * self.camera.mat_lookat).astype('f4'))
        self.vbo.orphan()
        self.vbo.write(data)
        if type == 'line':
            self.ctx.line_width = 1.0
            self.vao.render(moderngl.TRIANGLES, vertices=len(data) // 24)
        if type == 'points':
            self.ctx.point_size = 3.0
            self.vao.render(moderngl.POINTS, vertices=len(data) // 24)


class PanTool:
    def __init__(self):
        self.total_x = 0.0
        self.total_y = 0.0
        self.start_x = 0.0
        self.start_y = 0.0
        self.delta_x = 0.0
        self.delta_y = 0.0
        self.drag = False

    def start_drag(self, x, y):
        self.start_x = x
        self.start_y = y
        self.drag = True

    def dragging(self, x, y):
        if self.drag:
            self.delta_x = (x - self.start_x) * 2.0
            self.delta_y = (y - self.start_y) * 2.0

    def stop_drag(self, x, y):
        if self.drag:
            self.dragging(x, y)
            self.total_x -= self.delta_x
            self.total_y += self.delta_y
            self.delta_x = 0.0
            self.delta_y = 0.0
            self.drag = False

    @property
    def value(self):
        return (self.total_x - self.delta_x, self.total_y + self.delta_y)


def checker_board(size, num):
    x = np.linspace(-int(num/2) * size, int(num/2) * size, num)
    v = np.tile([-size, size], steps)
    w = np.zeros(steps * 2)
    return np.concatenate([np.dstack([u, v, w]), np.dstack([v, u, w])])


verts = grid(400, 20)
pan_tool = PanTool()


class GLWidget(QModernGLWidget):
    frameChanged = pyqtSignal(int)
    hParentWidget = None
    checkerBoardSize = 50
    camDist = 500
    floorObj = None
    rotateX = 45
    rotateY = 0
    rotateZ = 0
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
    camera = Camera(1)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(500, 500)
        self.scene = None

    def init(self):
        self.resize(500, 500)
        self.ctx.viewport = (0, 0, 500, 500)
        self.scene = HelloWorld2D(self.ctx)

    def resetCamera(self):
        pass

    def setMotion(self, root:BVHNode, motion, frames, frameTime):
        self.root = root
        self.motion = motion
        self.frames = frames
        self.frameTime = frameTime
        self.frameCount = 0
        self.isPlaying = True

    def render(self):
        self.screen.use()
        self.scene.clear()
        self.scene.plot(verts)

    def mousePressEvent(self, evt):
        pan_tool.start_drag(evt.x() / 512, evt.y() / 512)
        self.scene.pan(pan_tool.value)
        self.update()

    def mouseMoveEvent(self, evt):
        pan_tool.dragging(evt.x() / 512, evt.y() / 512)
        self.scene.pan(pan_tool.value)
        self.update()

    def mouseReleaseEvent(self, evt):
        pan_tool.stop_drag(evt.x() / 512, evt.y() / 512)
        self.scene.pan(pan_tool.value)
        self.update()

    def setMotion(self, root:BVHNode, motion, frames:int, frameTime:float):
        self.root = root
        self.motion = motion
        self.frames = frames
        self.frameTime = frameTime
        self.frameCount = 0
        self.isPlaying = True
