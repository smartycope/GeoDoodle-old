from Cope import todo, debug, untested, confidence, flattenList
from PyQt6.QtCore import QEvent, QFile, QLine, QLineF, QRect, QRectF, Qt
import numpy as np
from PyQt6.QtGui import QBrush, QColor, QPainter, QPainterPath, QPen, QTransform, QPolygon, QPolygonF
from PyQt6.QtWidgets import QFileDialog, QMainWindow, QWidget
from Line import Line
from Point import Point
from Singleton import Singleton as S


def createLine(self, linkAnother=False):
    # Create a new line
    if self.currentLine is None:
        # self.focusLoc used to be deepcopied, in case you're getting weird errors here
        self.currentLine = Line(self.focusLoc.copy(), pen=S.settings['paper/current_pen'])
    else:
        # Don't create Lines with no length
        if self.currentLine.start == self.focusLoc:
            self.currentLine = None
        # End the current line
        else:
            newLine = self.currentLine.finished(self.focusLoc.copy())
            self.lines += self.mirrorLine(newLine)
            # self.focusLoc used to be deepcopied, in case you're getting weird errors here
            self.currentLine = Line(self.focusLoc.copy(), pen=S.settings['paper/current_pen']) if linkAnother else None

def _mirrorTransforms(self):
    transforms = [np.identity(3)]
    # Mirror accross the x axis
    if self.MIRROR_STATES[self.currentMirrorState] in [1, 4]:
        transforms.append(np.array([
            [1,  0, 0],
            [0, -1, self.centerDot.y*2],
            [0,  0, 1],
        ]))
    # Mirror accross the y axis
    if self.MIRROR_STATES[self.currentMirrorState] >= 2:
        transforms.append(np.array([
            [-1, 0, self.centerDot.x*2],
            [ 0, 1, 0],
            [ 0, 0, 1],
        ]))
    # Mirror in the corner
    if self.MIRROR_STATES[self.currentMirrorState] >= 4:
        transforms.append(np.array([
            [-1,  0, self.centerDot.x*2],
            [ 0, -1, self.centerDot.y*2],
            [ 0,  0, 1],
    ]))
    return transforms

def mirrorLine(self, line):
    """ Returns the appropriate number of lines, transformed according to the
        current mirror state
    """
    return [line.transformed(t) for t in self._mirrorTransforms()]
