import numpy as np
# from Transformation import Transformation
from Cope import todo, debug, untested, confidence, flattenList, frange
from PyQt6.QtCore import QEvent, QFile, QLine, QLineF, QRect, QRectF, Qt
from PyQt6.QtGui import QBrush, QColor, QPainter, QPainterPath, QPen, QTransform, QPolygon, QPolygonF
from PyQt6.QtWidgets import QFileDialog, QMainWindow, QWidget
from Transformation import transform2Transformation
from Line import Line
from Point import Point
from Singleton import Singleton as S
from math import floor, ceil

"""
def regenerateDots(self, start=Point(0, 0), size:'QSize'=None):
    if size is None:
        size = self.size()
    xarr = []
    yarr = []
    amt = round(((Point(size)) / 2) / self.scale)
    for x in range(-amt.x + int(start.x), amt.x - int(start.x)):
        for y in range(-amt.y + int(start.y), amt.y - int(start.y)):
            xarr.append(x)
            yarr.append(y)
    self.pureDots = np.array([xarr, yarr, [1] * len(xarr)])
    self.dots = self.relativeTransformation @ self.pureDots
    debug(f'Made {len(self.pureDots[0])} new dots')
"""

def regenerateDots(self, start=Point(0, 0), size:'QSize'=None):
    if size is None:
        size = self.size()
    xarr = []
    yarr = []
    amt = ((Point(size)) / 2) / self.scale
    for x in frange(-amt.x + start.x, amt.x - start.x):
        for y in frange(-amt.y + start.y, amt.y - start.y):
            xarr.append(x)
            yarr.append(y)
    self.pureDots = np.array([xarr, yarr, [1] * len(xarr)])
    self.dots = self.relativeTransformation @ self.pureDots
    debug(f'Made {len(self.pureDots[0])} new dots')

def transform(self, transformation:np.ndarray, regenerate=False, resizing=False):
    """ Applies the given transformation to the self.transformation matrix and
        to all the relevant points """

    # Before we actually allow the transformation, first check that it's acceptable
    newTransformation = transformation @ self.transformation
    # Ensure that we can only zoom in and out so far
    if newTransformation[0, 0] < S.settings['min_scale'] or \
       newTransformation[1, 1] < S.settings['min_scale'] or \
       newTransformation[0, 0] > S.settings['max_scale'] or \
       newTransformation[1, 1] > S.settings['max_scale']:
        return
    # We only need to make new dots if we're changing the scale factor
    regenerate = (newTransformation[0, 0] != self.transformation[0, 0]) or (newTransformation[1, 1] != self.transformation[1, 1]) or regenerate
    self.transformation = newTransformation

    size = Point(self.size())

    self.relativeTransformation = self.transformation.copy()
    # Restrict the dot transformation to within the screen area
    # debug((self.relativeTransformation[0, 2] % self.relativeTransformation[0, 0]), 'x')
    # This is wrong, this just aligns to the relative center of the screen, not the center dot.
    # BUT IT WORKS SO DONT TOUCH IT
    translationOffset = Point(self.relativeTransformation[0, 2] % self.relativeTransformation[0, 0],
                              self.relativeTransformation[1, 2] % self.relativeTransformation[1, 1])
    self.centerDot = ((size - (size % self.scale)) /2) + translationOffset
    self.relativeTransformation[0, 2] = translationOffset.x + (self.size().width()  / 2)# + ((self.size().width() / 2) % self.relativeTransformation[0, 0]))
    # self.relativeTransformation[0, 2] = self.centerDot.x# + (self.size().width()  / 2)# + ((self.size().width() / 2) % self.relativeTransformation[0, 0]))
    # self.relativeTransformation[0, 2] = (self.size().width() % self.relativeTransformation[0, 2]) + (self.size().width()  / 2)
    self.relativeTransformation[1, 2] = translationOffset.y + (self.size().height() / 2)# + ((self.size().height() / 2) % self.relativeTransformation[1, 1]))
    # self.relativeTransformation[1, 2] = self.centerDot.y# + (self.size().height() / 2)# + ((self.size().height() / 2) % self.relativeTransformation[1, 1]))
    # self.relativeTransformation[1, 2] = (self.size().height() % self.relativeTransformation[1, 2]) + (self.size().height() / 2)

    # debug(size % self.scale, 'offset')
    # self.centerDot = (size - (size % self.scale)) / 2

    # If we've changed the scale factor, then regenerate the dots so we always
    # have the right amount on screen
    if regenerate:
        self.regenerateDots()
    else:
        self.dots = self.relativeTransformation @ self.pureDots

    # Since this is how we resize the window, don't touch the mouse if we're resizing
    if not resizing:
        # This is copied from moveFocus()
        #* If the cursor is inside the window, move the cursor as well,
        #   That way, when you move it again, it goes from where it shows it is
        self.focusLoc.transform(transformation)
        # This moves the cursor so its aligned with the focus
        if S.settings['paper/use_custom_cursor']:
            self.cursor().setPos(self.mapToGlobal(self.focusLoc.copy().toPoint()))
        # This loops the focus
        self.focusLocChanged()

    # Translate the lines
    self.lines = [line.transformed(transformation) for line in self.lines]

    # Translate the currentLine
    if self.currentLine is not None:
        # Because the currentLine is immutable for some reason??
        self.currentLine = Line(self.currentLine.start.transformed(transformation), self.focusLoc)
        # self.currentLine.transform(transformation)

    # Translate the bounds
    for bound in self.bounds:
        bound.transform(transformation)

    self.repaint()

def copyTransform(self):
    trans = self.transformation.copy() @ self._selectionTransformation
    x = ((self.copying.size.width()  // 2) * trans[0, 0])
    y = ((self.copying.size.height() // 2) * trans[1, 1])
    horizontal = self._selectionRotation % 2
    trans[0, 2] = self.focusLoc.x
    trans[1, 2] = self.focusLoc.y
    if horizontal:
        trans[0, 2] -= y * 2
        trans[1, 2] -= x * 2
        if self._selectionRotation % 3:
            pass
    else:
        trans[0, 2] -= x
        trans[1, 2] -= y
        if self._selectionRotation % 4:
            pass
            # trans[0, 2] *= -1
            # trans[1, 2] *= -1

    return trans
