# from PIL import Image, ImageDraw, ImageColor
import json
import os
import pickle
from copy import deepcopy
from os.path import join
from typing import Any, Callable, Iterable, Optional, Union

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtCore import QEvent, QFile, QLine, QLineF, QRect, QRectF, Qt
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtWidgets import QFileDialog, QMainWindow, QWidget

from Cope import DIR, debug, debugged, displayAllLinks, getTime, timeFunc, todo
from Geometry import *
from Line import Line
from Point import Pointf, Pointi

# SAVES_FOLDER = DIR + 'saves/'
# DOT_SPREAD_LIMIT = 12
# MIRROR_LINE_COLOR = (87, 11, 13)

def toQPoint(p):
    return QPoint(p.x, p.y)


MOVEMENT_EVENTS  = (QEvent.MouseMove, QEvent.DragMove, QEvent.HoverMove)
# UPDATE_EVENTS    = (QEvent.MouseButtonPress,
#                     QEvent.Scroll)
#                  + MOVEMENT_EVENTS


#* Cool events worth looking into:
    # QEvent.MouseTrackingChange, QEvent.Move, QEvent.Paint, QEvent.Resize, QEvent.Scroll, QEvent.Show,
    # QEvent.Shortcut, QEvent.ShortcutOverride, QEvent.StyleChange, QEvent.UpdateRequest, QEvent.Wheel,
    # QEvent.DragEnter, QEvent.DragLeave, QEvent.DragMove, QEvent.Drop, QEvent.Enter, QEvent.FileOpen,
    # QEvent.Gesture, QEvent.GrabKeyboard, QEvent.GrabMouse, QEvent.HoverEnter, QEvent.HoverLeave,
    # QEvent.HoverMove, QEvent.Leave, QEvent.MouseButtonDblClick

class Paper(QOpenGLWidget):
    #* Settings
    backgroundColor = (200, 160, 100)
    offscreenAmount = 0
    dotSpread = 16
    dotColor = (0, 0, 0)
    dotSize = 1
    focusColor = (0, 0, 255)
    focusRadius = 10
    dragDelay = 7
    exportLineThickness = 2
    boundsColor = (30, 30, 30)
    boundsLineColor = mirrorLineColor = (32, 45, 57)
    aaSamples = 2

    includeHalfsies = True
    overlap = (0, 0)

    saveDir   = "~/GeoDoodle/saves/"
    exportDir = "~/GeoDoodle/images/"
    loadDir   = "~/GeoDoodle/saves/"


    def __init__(self, parent=None):
        super(Paper, self).__init__(parent)

        self.qp = QPainter(self)

        # self.setMinimumSize(100, 100)
        # self.width = self.window().width
        # self.height = self.window().height

        self.getSize = lambda: (self.window().width(), self.window().height())

        self.metaLines = []
        self.startingPoint = Pointi(self.getSize()[0] / 2, self.getSize()[1] / 2)
        self.dots = genDotArrayPoints(self.getSize(), self.offscreenAmount, self.dotSpread)
        self.focusLoc = self.mouseLoc = Pointi(0, 0)
        self.lines = []
        self.boundsMode = False
        self.setMouseTracking(True)
        self.currentLine = None
        self.dragButtons = [False] * 32
        self.lineBuffer = []
        self.currentDrawColor = QColor('black')
        self.mirroringStates = [0, 1, 2, 4] # 1 is horizontal line only
        self.specificErase = None
        self.boundsCircles = ()

        fmt = QSurfaceFormat()
        fmt.setSamples(self.aaSamples)
        self.setFormat(fmt)

        self.installEventFilter(self)


#* Update Functions
    @timeFunc
    def updateFocus(self):
        self.focusLoc = Pointi(min(self.dots, key=lambda i:abs(i.x - self.mouseLoc.x)).x + 1,
                               min(self.dots, key=lambda i:abs(i.y - self.mouseLoc.y)).y + 1)


    def updateMouse(self, event):
        self.mouseLoc = Pointi(event.pos())
        self.updateFocus()
        if self.currentLine is not None:
            self.currentLine.end = self.focusLoc


#* Event Functions
    def eventFilter(self, target, event):
        if target == self:
            if event.type() in MOVEMENT_EVENTS:
                self.updateMouse(event)
                self.dragButtons[int(event.buttons())] = True
                self.update()

            if event.type() == QEvent.MouseButtonPress:
                if int(event.buttons()) == Qt.LeftButton:
                    self.createLine()

                elif int(event.buttons()) == Qt.RightButton:
                    self.createLine(True)

                elif int(event.buttons()) == Qt.MiddleButton:
                    self.deleteLine()
                    debug(self.mouseLoc, color=2)

            if event.type() == QEvent.MouseButtonRelease:
                if self.dragButtons[int(event.button())]:
                    self.dragButtons[int(event.button())] = False
                    self.createLine(linkAnother=int(event.button()) == Qt.RightButton)

        return super().eventFilter(target, event)


    def keyPressed(self, event):
        if   event.key() == Qt.Key_Up or event.key() == Qt.Key_W:
            self.moveY(-1)

        elif event.key() == Qt.Key_Down or event.key() == Qt.Key_S:
            self.moveY(1)

        elif event.key() == Qt.Key_Left or event.key() == Qt.Key_A:
            self.moveX(-1)

        elif event.key() == Qt.Key_Right or event.key() == Qt.Key_D:
            self.moveX(1)

        elif event.key() == Qt.Key_Space:
            self.createLine()
            # self.update()

        elif event.key() == Qt.Key_C:
            self.createLine(True)
            # self.update()

        elif event.key() == Qt.Key_B:
            self.update()

        elif event.key() == Qt.Key_Q:
            self.deleteLine()

        else:
            event.ignore()
            return

        event.accept()


         # if event.key == 264 or event.key == pygame.K_HOME: # numpad up
        #     DOTSPREAD += 1
        #     self.dots = genDotArrayPoints(self.getSize(), OFFSCREEN_AMOUNT, DOTSPREAD)
        # if event.key == 258 or event.key == pygame.K_END: # numpad down
        #     DOTSPREAD -= 1
            # self.dots = genDotArrayPoints(self.getSize(), OFFSCREEN_AMOUNT, DOTSPREAD)


    def specificErase(self):
        todo('specificErase')
        # If there's nothing there, don't do anything
        if self.focusLoc in [i.end for i in self.lines] + [i.start for i in self.lines]:
            if self.specificErase == None:
                self.specificErase = self.focusLoc
            else:
                assert(type(self.specificErase) == Pointi)
                for index, i in enumerate(self.lines):
                    if (i.start == self.focusLoc and i.end == self.specificErase) or \
                    (i.start == self.specificErase and i.end == self.focusLoc):
                        del self.lines[index]
                self.specificErase = None
        else:
            self.specificErase = None


    def fileDropped(self, event):
        with open(event.file, 'r') as f:
            self.lines = pickle.load(f)


    def moveX(self, dots):
        self.focusLoc.x += self.dotSpread * dots
        if self.currentLine is not None:
            self.currentLine.end = self.focusLoc
        if self.window().rect().contains(toQPoint(self.focusLoc), proper=True):
            self.cursor().setPos(self.mapToGlobal(toQPoint(self.focusLoc)))
        # self.update()


    def moveY(self, dots):
        self.focusLoc.y += self.dotSpread * dots
        if self.currentLine is not None:
            self.currentLine.end = self.focusLoc
        if self.window().rect().contains(toQPoint(self.focusLoc), proper=True):
            self.cursor().setPos(self.mapToGlobal(toQPoint(self.focusLoc)))
        # self.update()



#* Draw Functions
    @timeFunc
    def paintEvent(self, event):
        # debug('Drawing!')

        # debug()

        #* Just putting this out there....
        # Qt::NoPen	0	no line at all. For example, QPainter::drawRect() fills but does not draw any boundary line.
        # Qt::SolidLine	1	A plain line.
        # Qt::DashLine	2	Dashes separated by a few pixels.
        # Qt::DotLine	3	Dots separated by a few pixels.
        # Qt::DashDotLine	4	Alternate dots and dashes.
        # Qt::DashDotDotLine	5	One dash, two dots, one dash, two dots.
        # Qt::CustomDashLine



        # if not self.qp.isActive():
        self.qp.begin(self)

        self.qp.setRenderHint(QPainter.Antialiasing)
        self.qp.setRenderHint(QPainter.HighQualityAntialiasing)

        # debug(self.qp.Antialiasing)
        # self.qp.Antialiasing = True
        # debug(self.qp.HighQualityAntialiasing)
        # self.qp.HighQualityAntialiasing = True

        #* Fill the background
        self.qp.fillRect(self.rect(), QColor(*self.backgroundColor))

        # debug(self.dots)
        self.drawDots()
        self.drawLines()
        self.drawFocus()
        self.drawBounds()

        self.qp.end()

    @timeFunc
    def drawLines(self):
        for line in self.lines + self.metaLines + ([self.currentLine] if self.currentLine is not None else []):
            line.draw(self.qp)

    @timeFunc
    def drawDots(self):
        self.qp.setPen(QColor(*self.dotColor))

        for i in self.dots:
            self.qp.drawRect(QRect(*i.datai(), self.dotSize, self.dotSize))
            # self.qp.drawPoint(*i.datai())
            # self.qp.drawPoint(*i.datai())


    def drawFocus(self):
        self.qp.setPen(QColor(*self.focusColor))
        self.qp.drawEllipse(*(self.focusLoc-6).datai(), self.focusRadius, self.focusRadius)


    def drawBounds(self):
        # Just for optimization's sake
        if len(self.boundsCircles):
            self.qp.setPen(QColor(*self.boundsColor))
            for i in self.boundsCircles:
                self.qp.drawEllipse(*(i-5).datai(), self.focusRadius-2, self.focusRadius-2)

            if len(self.boundsCircles) >= 2:
                self.qp.setPen(QColor(*self.boundsLineColor))
                bounds = getLargestRect(self.boundsCircles)
                self.qp.drawRect(bounds)


    def drawMirroring(self):
        todo('mirroring')
        #* Add mirroring
        for i in self.lineBuffer:
            #* Check if there's already a line there (so it doesn't get bolder (because of anti-aliasing))
            dontDraw = False
            for k in self.lines:
                if i == k or (i.start == k.end and i.end == k.start):
                    dontDraw = True

            #* Check if the start and end are the same (no line would be drawn)
            if i.start != i.end and not dontDraw:
                self.lines.append(i)

            if self.mirroringStates[self.currentMirrorState] in [1, 4]:
                starty = self.startingPoint.y + (self.startingPoint.y - i.start.y) + 2
                endy   = self.startingPoint.y + (self.startingPoint.y - i.end.y) + 2
                vertStart = Pointi(i.start.x, starty)
                vertEnd   = Pointi(i.end.x,   endy)
                self.lines.append(Line(vertStart, vertEnd, i.color))


            if self.mirroringStates[self.currentMirrorState] >= 2:
                # self.startingPoint = Point(min(self.dots, key=lambda i:abs(i.x - (self.getSize()[0] / 2))).x + 1, min(self.dots, key=lambda i:abs(i.y - (self.getSize()[1] / 2))).y + 1)

                startx = self.startingPoint.x + (self.startingPoint.x - i.start.x) + 2
                endx   = self.startingPoint.x + (self.startingPoint.x - i.end.x) + 2
                horStart = Pointi(startx, i.start.y)
                horEnd   = Pointi(endx,   i.end.y)
                self.lines.append(Line(horStart, horEnd, i.color))

                if self.mirroringStates[self.currentMirrorState] >= 4:
                    corStart = Pointi(startx, starty)
                    corEnd   = Pointi(endx,   endy)
                    self.lines.append(Line(corStart, corEnd, i.color))

        self.lineBuffer = []

        #* Add mirrored current line
        if self.currentLine is not None and self.mirroringStates[self.currentMirrorState] in [1, 4]:
            curStarty = self.startingPoint.y + (self.startingPoint.y - self.currentLine.start.y) + 2
            curEndy   = self.startingPoint.y + (self.startingPoint.y - self.currentLine.end.y) + 2
            Line(Pointi(self.currentLine.start.x, curStarty), Pointi(self.currentLine.end.x, curEndy), self.currentLine.color).draw(self.mainSurface)

        if self.currentLine is not None and self.mirroringStates[self.currentMirrorState] >= 2:
            curStartx = self.startingPoint.x + (self.startingPoint.x - self.currentLine.start.x) + 2
            curEndx   = self.startingPoint.x + (self.startingPoint.x - self.currentLine.end.x) + 2
            Line(Pointi(curStartx, self.currentLine.start.y), Pointi(curEndx, self.currentLine.end.y), self.currentLine.color).draw(self.mainSurface)

            if self.currentLine is not None and self.mirroringStates[self.currentMirrorState] >= 4:
                Line(Pointi(curStartx, curStarty), Pointi(curEndx, curEndy), self.currentLine.color).draw(self.mainSurface)



#* File Functions
    def save(self):
        with open(self.getFile(True), 'wb') as f:
            pickle.dump(self.lines, f)
        print('File Saved!')


    def saveAs(self):
        todo('saveAs')


    def open(self):
        with open(self.getFile(False), 'rb') as f:
            self.lines = pickle.load(f)


    def export(self):
        image = Image.new('RGB', self.getSize(), color=tuple(self.backgroundColor))
        draw = ImageDraw.Draw(image)
        for line in self.lines:
            draw.line(line.start.data() + line.end.data(), fill=tuple(line.color), width=self.exportLineThickness)

        image.save(self.getFile(True))
        print('File Saved!')


    def _new(self):
        todo('_new')


    def getFile(self, save: bool):
        return QFileDialog.getSaveFileName()[0] if save else QFileDialog.getOpenFileName()[0]



#* Repeat Functions
    def repeatPattern(self, pattern):
        self.lines = pattern.repeat(QSize(self.getSize()[0] + self.dotSpread + self.offscreenAmount,
                                          self.getSize()[1] + self.dotSpread + self.offscreenAmount),
                                     self.dotSpread,
                                     self.dots[0] % self.dotSpread,
                                     self.overlap,
                                     self.includeHalfsies)

        self.boundsCircles = []



#* Other Functions
    def createLine(self, linkAnother=False):
        if self.currentLine is None:
            self.currentLine = Line(self.focusLoc, color=self.currentDrawColor)
        else:
            self.currentLine.finish(self.focusLoc)
            # self.lineBuffer.append(self.currentLine)
            self.lines.append(self.currentLine)
            self.currentLine = Line(self.focusLoc, color=self.currentDrawColor) if linkAnother else None


    def deleteLine(self, at=None):
        if at is None:
            at = self.focusLoc

        #* This should not be nessicarry, I have no idea why the 3 lines don't work by themselves.
        linesStillAtFocus = True
        while linesStillAtFocus:
            linesStillAtFocus = False

            for i in self.lines:
                if i.start == at or i.end == at:
                    self.lines.remove(i)

            for i in self.lines:
                if i.start == at or i.end == at:
                    linesStillAtFocus = True

        for i in self.boundsCircles:
            if i == at:
                self.boundsCircles.remove(i)

        self.currentLine = None

        self.update()


    def mirror(self):
        self.metaLines = []

        self.currentMirrorState += 1
        if self.currentMirrorState >= len(self.mirroringStates):
            self.currentMirrorState = 0

        # print(self.mirroringStates[self.currentMirrorState])

        if self.mirroringStates[self.currentMirrorState] in [1, 4]:
            starth = Pointi(-self.offScreenAmount, self.startingPoint.y)
            endh   = Pointi(self.getSize()[0] + self.offScreenAmount, self.startingPoint.y)
            self.metaLines.append(Line(starth, endh, MIRROR_LINE_COLOR))

        if self.mirroringStates[self.currentMirrorState] >= 2:
            startv = Pointi(self.startingPoint.x, -self.offScreenAmount)
            endv   = Pointi(self.startingPoint.x, self.getSize()[1] + self.offScreenAmount)
            self.metaLines.append(Line(startv, endv, MIRROR_LINE_COLOR))


    def toggleBoundsMode(self):
        # todo('toggleBoundsMode')
        # self.boundsMode = not self.boundsMode
        self.addBound()


    def getLinesWithinRect(self, bounds):
        lines = []

        for l in self.lines:
            if bounds.contains(*l.start.datai()) and bounds.contains(*l.end.datai()):
                lines.append(l)

        return lines


    def getHalfLinesWithinRect(self, bounds):
        lines = []

        for l in self.lines:
            if bounds.contains(*l.start.datai()) or bounds.contains(*l.end.datai()):
                lines.append(l)

        return lines


    def undo(self):
        todo('undo')
        if self.currentLine == None and len(self.lines) > 0:
            del self.lines[-1]
            if self.mirroringStates[self.currentMirrorState] >= 2 and len(self.lines) > 0:
                self.lines.pop()
                if self.mirroringStates[self.currentMirrorState] >= 4 and len(self.lines) > 0:
                    self.lines.pop()
                    if len(self.lines) > 1:
                        self.lines.pop()
        elif self.currentLine != None:
            self.currentLine = None


    def redo(self):
        todo('redo')


    def clearAll(self):
        self.lines = []
        self.boundsCircles = []
        self.lineBuffer = []
        self.currentLine = None
        self.metaLines = []


    def addBound(self):
        self.boundsCircles += (Pointi(self.focusLoc),)
        self.update()


    def updateSettings(self, dialog):
        debug(showFunc=True)
        # self.dotSpread =


    def exit(self):
        self.close()
