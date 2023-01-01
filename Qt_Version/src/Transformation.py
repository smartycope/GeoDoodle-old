from PyQt6.QtGui import QTransform
from Cope import debug
from copy import copy, deepcopy
import numpy as np
from Point import Point

class Transformation(QTransform):
    def scaled(self):
        return Point(self.m11(), self.m22())
    def scaledx(self):
        return self.m11()
    def scaledy(self):
        return self.m22()
    def translated(self):
        return Point(self.m31(), self.m32())
    def translatedx(self):
        return self.m31()
    def translatedy(self):
        return self.m32()
    def copy(self):
        return Transformation(self.m11(), self.m12(), self.m13(), self.m21(), self.m22(), self.m23(), self.m31(), self.m32(), self.m33())
    def __getitem__(self, keys):
        # I'm too lazy to do this by hand at the moment
        # return self.asnp()[keys]
        if len(keys) != 2:
            raise IndexError('Transformation only supports 2 index array indecies')
        x, y = keys
        return getattr(self, f'm{x+1}{y+1}')()
    def __setitem__(self, keys, value):
        # This fuction is ridiculous, but it's probably more efficient than converting to and from an np array
        if len(keys) != 2:
            raise IndexError('Transformation only supports 2 index array indecies')
        x, y = keys
        if x == 0:
            if y == 0:
                self.setMatrix(value, self.m12(), self.m13(), self.m21(), self.m22(), self.m23(), self.m31(), self.m32(), self.m33())
            if y == 1:
                self.setMatrix(self.m11(), value, self.m13(), self.m21(), self.m22(), self.m23(), self.m31(), self.m32(), self.m33())
            if y == 2:
                self.setMatrix(self.m11(), self.m12(), value, self.m21(), self.m22(), self.m23(), self.m31(), self.m32(), self.m33())
            else:
                raise IndexError(f"Invalid index {keys} for a Transformation")
        if x == 1:
            if y == 0:
                self.setMatrix(self.m11(), self.m12(), self.m13(), value, self.m22(), self.m23(), self.m31(), self.m32(), self.m33())
            if y == 1:
                self.setMatrix(self.m11(), self.m12(), self.m13(), self.m21(), value, self.m23(), self.m31(), self.m32(), self.m33())
            if y == 2:
                self.setMatrix(self.m11(), self.m12(), self.m13(), self.m21(), self.m22(), value, self.m31(), self.m32(), self.m33())
            else:
                raise IndexError(f"Invalid index {keys} for a Transformation")
        if x == 2:
            if y == 0:
                self.setMatrix(self.m11(), self.m12(), self.m13(), self.m21(), self.m22(), self.m23(), value, self.m32(), self.m33())
            if y == 1:
                self.setMatrix(self.m11(), self.m12(), self.m13(), self.m21(), self.m22(), self.m23(), self.m31(), value, self.m33())
            if y == 2:
                self.setMatrix(self.m11(), self.m12(), self.m13(), self.m21(), self.m22(), self.m23(), self.m31(), self.m32(), value)
            else:
                raise IndexError(f"Invalid index {keys} for a Transformation")
    def asnp(self):
        return np.array([
            [self.m11(), self.m12(), self.m13()],
            [self.m21(), self.m22(), self.m23()],
            [self.m31(), self.m32(), self.m33()],
        ])
    @staticmethod
    def fromnp(mat:np.ndarray):
        return Transformation(*mat.astype(float).flatten())
    def __matmul__(self, mat):
        # if isinstance(mat, np.ndarray):
        #     mat = Transformation.fromnp(mat)
        if isinstance(mat, Transformation):
            mat = mat.asnp()
        if np.shape(mat) != (3, 3):
            raise TypeError(f'Cannot transform Transformation by {mat}, which has the wrong shape')
        # This is already overloaded properly
        # return Transformation(self * mat)
        return Transformation.fromnp(self.asnp() @ mat)
    def __str__(self):
        return str(self.asnp())

def transform2Transformation(current, goal):
    """ Returns the transformation needed to transform current into goal """
    # This took FOREVER to figure out
    delta = np.linalg.solve(current, goal)
    d = (current @ delta) @ np.linalg.inv(delta @ current)
    return d @ delta
