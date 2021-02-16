from PyQt5 import QtGui, QtCore, QtOpenGL
from PyQt5.QtWidgets import *
# PyOpenGL imports
from OpenGL.GL import *
import OpenGL.arrays.vbo as glvbo

import sys

from PyQt5.QtWidgets import QApplication, QMainWindow

import numpy as np
import numpy.random as rdn

sys.path.insert(1, '/home/marvin/hello/python/boilerplate/Cope.py')

from random import randint
import math, re
from time import process_time
from typing import Callable, Any, Iterable, Optional, Union
import atexit



# Override the debug parameters and display the file/function for each debug call
#   (useful for finding debug calls you left laying around and forgot about)
debugCount = 0


timingData = {}

#* A function decorator that prints how long it takes for a function to run
def timeFunc(func, accuracy=5):
    def wrap(*params, **kwparams):
        global timingData

        t = process_time()

        returns = func(*params, **kwparams)

        t2 = process_time()

        elapsed_time = round(t2 - t, accuracy)
        name = func.__name__

        try:
            timingData[name] += (elapsed_time,)
        except KeyError:
            timingData[name] = (elapsed_time,)

        # print(name, ' ' * (10 - len(name)), 'took', elapsed_time if elapsed_time >= 0.00001 else 0.00000, '\ttime to run.')
        print(f'{name:<12} took {elapsed_time:.{accuracy}f} seconds to run.')
        #  ' ' * (15 - len(name)),
        return returns
    return wrap


#* I realized *after* I wrote this that this is a profiler. Oops.
def _printTimingData(accuracy=5):
    global timingData
    if len(timingData):
        print()

        maxName = len(max(timingData.keys(), key=len))
        maxNum  = len(str(len(max(timingData.values(), key=lambda x: len(str(len(x)))))))
        for name, times in reversed(sorted(timingData.items(), key=lambda x: sum(x[1]))):
            print(f'{name:<{maxName}} was called {len(times):<{maxNum}} times taking {sum(times)/len(times):.{accuracy}f} seconds on average for a total of {sum(times):.{accuracy}f} seconds.')

atexit.register(_printTimingData)




class GLPlotWidget(QOpenGLWidget):
    # default window size
    width, height = 600, 600

    def set_data(self, data):
        """Load 2D data as a Nx2 Numpy array.
        """
        self.data = data
        self.count = data.shape[0]

    def initializeGL(self):
        """Initialize OpenGL, VBOs, upload data on the GPU, etc.
        """
        # background color
        glClearColor(0,0,0,0)
        # create a Vertex Buffer Object with the specified data
        self.vbo = glvbo.VBO(self.data)

    @timeFunc
    def paintGL(self):
        """Paint the scene.
        """
        # clear the buffer
        glClear(GL_COLOR_BUFFER_BIT)
        # set yellow color for subsequent drawing rendering calls
        glColor(1,1,0)
        # bind the VBO
        self.vbo.bind()
        # tell OpenGL that the VBO contains an array of vertices
        glEnableClientState(GL_VERTEX_ARRAY)
        # these vertices contain 2 single precision coordinates
        glVertexPointer(2, GL_FLOAT, 0, self.vbo)
        # draw "count" points from the VBO
        glDrawArrays(GL_POINTS, 0, self.count)

#         glBegin(GL_LINES)

#         for x, y in self.data[:200]:
#             glVertex(x, y)

#         glEnd()
# 0.80219
# 0.00021
    def resizeGL(self, width, height):
        """Called upon window resizing: reinitialize the viewport.
        """
        # update the window size
        self.width, self.height = width, height
        # paint within the whole window
        glViewport(0, 0, width, height)
        # set orthographic projection (2D only)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        # the window corner OpenGL coordinates are (-+1, -+1)
        glOrtho(-1, 1, 1, -1, -1, 1)

if __name__ == '__main__':
    # define a Qt window with an OpenGL widget inside it
    class TestWindow(QMainWindow):
        def __init__(self):
            super(TestWindow, self).__init__()
            # generate random data points
            self.data = np.array(.2*rdn.randn(100000,2),dtype=np.float32)
            print(self.data)
            print(type(self.data))
            print(type(self.data[0]))
            # initialize the GL widget
            self.widget = GLPlotWidget()
            self.widget.set_data(self.data)
            # put the window at the screen position (100, 100)
            self.setGeometry(100, 100, self.widget.width, self.widget.height)
            self.setCentralWidget(self.widget)
            self.show()

    # create the Qt App and window
    app = QApplication(sys.argv)
    window = TestWindow()
    window.show()
    app.exec_()















'''
from PyQt5 import QtGui, QtCore, QtOpenGL
from PyQt5.QtWidgets import *
# PyOpenGL imports
from OpenGL.GL import *
import OpenGL.arrays.vbo as glvbo

import sys

from PyQt5.QtWidgets import QApplication, QMainWindow

import numpy as np
import numpy.random as rdn


class GLPlotWidget(QOpenGLWidget):
    # default window size
    width, height = 600, 600

    def set_data(self, data):
        """Load 2D data as a Nx2 Numpy array.
        """
        self.data = data
        self.count = data.shape[0]

    def initializeGL(self):
        """Initialize OpenGL, VBOs, upload data on the GPU, etc.
        """
        # background color
        glClearColor(0,0,0,0)
        # create a Vertex Buffer Object with the specified data
        self.vbo = glvbo.VBO(self.data)

    def paintGL(self):
        """Paint the scene.
        """
        # clear the buffer
        glClear(GL_COLOR_BUFFER_BIT)
        # set yellow color for subsequent drawing rendering calls
        glColor(1,1,0)
        # bind the VBO
        self.vbo.bind()
        # tell OpenGL that the VBO contains an array of vertices
        glEnableClientState(GL_VERTEX_ARRAY)
        # these vertices contain 2 single precision coordinates
        glVertexPointer(2, GL_FLOAT, 0, self.vbo)
        # draw "count" points from the VBO
        glDrawArrays(GL_POINTS, 0, self.count)

    def resizeGL(self, width, height):
        """Called upon window resizing: reinitialize the viewport.
        """
        # update the window size
        self.width, self.height = width, height
        # paint within the whole window
        glViewport(0, 0, width, height)
        # set orthographic projection (2D only)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        # the window corner OpenGL coordinates are (-+1, -+1)
        glOrtho(-1, 1, 1, -1, -1, 1)

if __name__ == '__main__':
    # define a Qt window with an OpenGL widget inside it
    class TestWindow(QMainWindow):
        def __init__(self):
            super(TestWindow, self).__init__()
            # generate random data points
            self.data = np.array(.2*rdn.randn(100000,2),dtype=np.float32)
            print(self.data)
            print(type(self.data))
            print(type(self.data[0]))
            # initialize the GL widget
            self.widget = GLPlotWidget()
            self.widget.set_data(self.data)
            # put the window at the screen position (100, 100)
            self.setGeometry(100, 100, self.widget.width, self.widget.height)
            self.setCentralWidget(self.widget)
            self.show()

    # create the Qt App and window
    app = QApplication(sys.argv)
    window = TestWindow()
    window.show()
    app.exec_()
'''
