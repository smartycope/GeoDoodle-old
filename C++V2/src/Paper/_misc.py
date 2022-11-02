from Cope import todo, debug, untested, confidence, flattenList
from PyQt5.QtCore import QEvent, QFile, QLine, QLineF, QRect, QRectF, Qt, QSize
from PyQt5.QtGui import QBrush, QColor, QPainter, QPainterPath, QPen, QTransform, QPolygon, QPolygonF
from PyQt5.QtWidgets import QFileDialog, QMainWindow, QWidget
import Pattern
from Line import Line
from Point import Point, Pair


def moveFocus(self, axis, dots):
    # I would think you should divide this by self.width instead, but that doesn't seem to work
    # amt = (self.dotSpread / (self.width() / 2)) * dots
    amt = self.dotSpread * dots
    self.focusLoc += ((amt, 0) if axis == 'x' else (0, amt))

    # This is already done when moving the cursor triggers our mouseMoved function
    # if self.currentLine is not None:
    #     self.currentLine.end = self.focusLoc.copy()

    #* If the cursor is inside the window, move the cursor as well,
    #   That way, when you move it again, it goes from where it shows it is
    if self.window().rect().contains(self.focusLoc.toPoint(), proper=True):
        self.cursor().setPos(self.mapToGlobal(self.focusLoc.copy().toPoint()))

    self.repaint()

def updateMirror(self, setTo=None, setIndex=None, increment=None):
    # Don't specify both at the same time
    assert setTo is None or setIndex is None

    self.mirrorLines = []

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

    # Get the dots closest to halfway (this is not necissarily the position of any dot)
    halfway = Pair(min(self.dots, key=lambda p:abs(p[0] - self.width()/2))[0],
                    min(self.dots, key=lambda p:abs(p[1] - self.height()/2))[1])
    # halfway += self.translation % self.dotSpread

    # Add the horizontal line
    if self.MIRROR_STATES[self.currentMirrorState] in [1, 4]:
        starth = Point(0,            halfway.y)
        endh   = Point(self.width(), halfway.y)
        self.mirrorLines.append(Line(starth, endh, self.MIRROR_LINE_COLOR))

    # Add the veritcal line
    if self.MIRROR_STATES[self.currentMirrorState] >= 2:
        startv = Point(halfway.x, 0)
        endv   = Point(halfway.x, self.height())
        self.mirrorLines.append(Line(startv, endv, self.MIRROR_LINE_COLOR))

    self.repaint()

def clearAll(self):
    self.lines.clear()
    self.bounds.clear()
    self.currentLine = None
    self.mirrorLines.clear()
    self.currentMirrorState = 0
    self.updatePattern()

@untested
def updateSettings(self, settings):
    # keyRepeatDelay
    # keyIntervalDealy

    # shortcutBox
    # shortcutSelect
    # setShortcut

    self.dotSpread = settings.dotSpread.value()
    self.dotSpreadMeasure = settings.dotSpreadMeasure.value()
    self.dotSpreadUnit = settings.dotSpreadUnit.text()

    self.background = settings.backgroundColor.getColor()
    self.dotColor = settings.dotColor.getColor()
    self.focusColor = settings.focusColor.getColor()

    self.exportThickness = settings.exportThickness.value()
    self.savePath = settings.savePath.text()
    self.exportPath = settings.exportPath.text()

    self.doReset = True
    # glClearColor(*clampColor(*self.backgroundColor), 1)
    # debug(glGetFloatv(GL_COLOR_CLEAR_VALUE), name='background color', color=2)
    self.update()

@untested
def setShowLen(self, val):
    self.showLen = val
    self.update()

@untested
def scalePoint(point, originPoint, startDotSpread, newDotSpread):
    if startDotSpread == newDotSpread:
        return point

    scaleX = True
    scaleY = True

    if point.x == originPoint.x:
        scaleX = False
    if point.y == originPoint.y:
        scaleY = False

    returnPoint = point.copy()

    if scaleX:
        returnPoint.x -= ((originPoint.x - returnPoint.x) / startDotSpread) * (newDotSpread - startDotSpread)
    if scaleY:
        returnPoint.y -= ((originPoint.y - returnPoint.y) / startDotSpread) * (newDotSpread - startDotSpread)

    return returnPoint


    # return point - ((originPoint - point) / startDotSpread) * (newDotSpread - startDotSpread)

@untested
def scaleLines_ip(lines, originPoint, startDotSpread, newDotSpread):
    ''' Scales the lines appropriately in place '''
    if startDotSpread == newDotSpread:
        return

    for line in lines:
        line.start = scalePoint(line.start, originPoint, startDotSpread, newDotSpread)
        line.end   = scalePoint(line.end,   originPoint, startDotSpread, newDotSpread)

@untested
def scaleLines(lines, originPoint, startDotSpread, newDotSpread):
    ''' Scales the lines appropriately, and return them '''
    returnLines = []
    if startDotSpread == newDotSpread:
        return None

    for line in lines:
        start = scalePoint(line.start, originPoint, startDotSpread, newDotSpread)
        end   = scalePoint(line.end,   originPoint, startDotSpread, newDotSpread)
        returnLines.append(Line(start, end, line.color))

    return returnLines

@untested
def genOnionLayer(dist, spread, origin, drawX=True, drawY=True):
    points = []

    for i in range(-dist, dist + 1):
        if drawY:
            points.append(origin + (Pointi(i, dist) * spread))
            points.append(origin + (Pointi(i, -dist) * spread))
        if drawX:
            points.append(origin + (Pointi(dist, i) * spread))
            points.append(origin + (Pointi(-dist, i) * spread))

    return points

@untested
def genDotArrayPoints(size:QSize, dotSpread, startPoint=Point(0, 0), offScreenAmount=0):
    # debug(dotSpread, size, offScreenAmount, startPoint, color=-1)
    #* The top-left corner-centric way of generating dots
    dots = []
    # We don't actually need to start drawing from there, we only need to offset it a little so it *looks*
    #   like we started drawing from there
    for x in range(round(startPoint.x % dotSpread), round(size.width()), dotSpread):
        for y in range(round(startPoint.y % dotSpread), round(size.height()), dotSpread):
            dots.append(Point(x, y))
    return dots

    '''
    #* The center-centric way of generating dots
    points = []

    xDist = int(size.width / dotSpread)
    yDist = int(size.height / dotSpread)

    values = sorted([xDist, yDist])

    for i in range(values[1]):
        points += genOnionLayer(i, dotSpread, Sizef(size) / 2)

    drawX = values[0] == xDist
    drawY = values[0] == yDist

    for i in range(values[0]):
        points += genOnionLayer(i, dotSpread, Sizef(size) / 2, drawX=drawX, drawY=drawY)

    #* These 2 lines are because the algorithm is broken somehow, and I'm too lazy to fix it. Its a O(1) cost, anyway
    points[:] = [i for i in points if collidePoint(Pointi(0, 0), size, i)]
    return tuple(set(points))
    '''
