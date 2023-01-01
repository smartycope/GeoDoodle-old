from Cope import todo, debug, untested, confidence, flattenList, depricated, unreachableState, frange
from PyQt6.QtCore import QEvent, QFile, QLine, QLineF, QRect, QRectF, Qt, QSize
from PyQt6.QtGui import QBrush, QColor, QPainter, QPainterPath, QPen, QTransform, QPolygon, QPolygonF
from PyQt6.QtWidgets import QFileDialog, QMainWindow, QWidget
from Line import Line
from Point import Point
from Singleton import Singleton as S

def loopFocus(self, current):
    if S.settings['paper/loop_focus']:
        xTolerance = self.transformation[0, 0] * 2
        yTolerance = self.transformation[1, 1] * 2
        # Looping to the left
        if current.x >= self.rect().right() - xTolerance:
            current.x = self.rect().left()
        # Looping to the right
        elif current.x <= self.rect().left() + xTolerance:
            current.x = self.rect().right()
        # Looping to the top
        elif current.y >= self.rect().bottom() - yTolerance:
            current.y = self.rect().top()
        # Looping to the bottom
        elif current.y <= self.rect().top() + yTolerance:
            current.y = self.rect().bottom()

def focusLocChanged(self):
    # If we're not within the window, and we put it there (i.e. this function
    # got called), then shift it to the opposite side of the window
    if self.currentLine is not None:
        # WHY DOES THE CURRENT LINE ACT IMMUTABLE???
        l = self.currentLine.copy()
        l.end = self.focusLoc.copy()
        self.currentLine = l

    # self.loopFocus(self.focusLoc)

def alignFocus(self, mouseLoc):
    """ Moves the focus to align the mouse with the dots after the mouse has been moved """
    # "inflate" the rectangle just a little so it covers off-by-one errors
    area = self.rect().adjusted(-5, -5, 5, 5)
    if not area.contains(mouseLoc.toPoint()):
        return
    self.focusLoc = self._getClosestDot(mouseLoc)
    # I think we have to check bounds here because I think this is called before keyReleased() is
    if self.selecting and len(self.bounds):
        self.bounds[-1] = self.focusLoc

    self.focusLocChanged()

def updateMouse(self, event):
    """ Called when the mouse moves """
    if S.settings['paper/use_custom_cursor']:
        self.alignFocus(Point(event.pos()))
    else:
        self._updateFocusTimer.start()

def _getClosestDot(self, point:Point):
    T = self.dots.T
    return Point(min(T, key=lambda p:abs(p[0] - point.x))[0],
                 min(T, key=lambda p:abs(p[1] - point.y))[1])

def updateMirror(self, setTo=None, setIndex=None, increment=None):
    # Don't specify both at the same time
    assert setTo is None or setIndex is None

    if setIndex is not None:
        assert setIndex in range(len(self.MIRROR_STATES))
        self.currentMirrorState = setIndex
    elif setTo is not None:
        assert setTo in self.MIRROR_STATES
        self.currentMirrorState = self.MIRROR_STATES.index(setTo)
    elif increment is not None:
        # Increment what state we're in
        self.currentMirrorState += increment
        if self.currentMirrorState >= len(self.MIRROR_STATES):
            self.currentMirrorState = 0
    self.repaint()

@untested
def setShowLen(self, val):
    self.showLen = val
    self.update()
