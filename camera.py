import numpy as np
from pyrr import Matrix44, Quaternion, Vector3, vector

import moderngl

class Camera():

    def __init__(self, ratio):
        self._field_of_view_degrees = 60.0
        self._z_near = 0.1
        self._z_far = 1000
        self._ratio = ratio
        self.build_projection()

        self._camera_position = Vector3([0.0, 0.0, -800.0])
        self._camera_front = Vector3([0.0, 0.0, 1.0])
        self._camera_up = Vector3([0.0, 1.0, 0.0])
        self._cameras_target = (self._camera_position + self._camera_front)
        self.build_look_at()

    def update_position(self, new_camera_position:Vector3):
        self._camera_position = new_camera_position
        self.build_look_at()

    def build_look_at(self):
        self._cameras_target = (self._camera_position + self._camera_front)
        self.mat_lookat = Matrix44.look_at(
            self._camera_position,
            self._cameras_target,
            self._camera_up)

    def build_projection(self):
        self.mat_projection = Matrix44.perspective_projection(
            self._field_of_view_degrees,
            self._ratio,
            self._z_near,
            self._z_far)