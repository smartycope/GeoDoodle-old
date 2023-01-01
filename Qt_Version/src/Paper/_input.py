from Cope import todo, debug, untested, confidence, flattenList
from Transformation import transform2Transformation
import numpy as np
from PyQt6.QtCore import QEvent, QFile, QLine, QLineF, QRect, QRectF, Qt, QTimer, QPointF, QPoint
from PyQt6.QtGui import QBrush, QColor, QPainter, QPainterPath, QPen, QTransform, QPolygon, QPolygonF
from PyQt6.QtWidgets import QFileDialog, QMainWindow, QWidget, QApplication
from Line import Line
from Point import Point
from Singleton import Singleton as S
from time import time as now


def moveFocus(self, axis, dots):
    amt = (self.transformation[0, 0] if axis == 'x' else self.transformation[1, 1]) * dots
    new = self.focusLoc + ((amt, 0) if axis == 'x' else (0, amt))
    # TODO: This has an off-by-1 error, but it works well enough
    if not self.rect().contains(new.toPoint()):
        self.loopFocus(new)
        return
    else:
        self.focusLoc = new
    # Only move the mouse cursor if we've manually moved the focus
    if S.settings['paper/use_custom_cursor']:
        self.cursor().setPos(self.mapToGlobal(self.focusLoc.copy().toPoint()))
    self.focusLocChanged()

def scaleControl(self, factor):
    # Scaling about a point is the same as scaling, then translating by that point
    scaleAboutPoint = np.array([
        [factor, 0, 0],
        [0, factor, 0],
        [0, 0, 1],
    ]) @ np.array([
        # Don't know why this is - and / factor, but it works, so I'll take it
        [1, 0, self.focusLoc.x if factor < 1 else (-self.focusLoc.x / factor)],
        [0, 1, self.focusLoc.y if factor < 1 else (-self.focusLoc.y / factor)],
        [0, 0, 1],
    ])
    self.transform(scaleAboutPoint, regenerate=True)

def createControl(self, addAnother):
    if self.copying is not None:
        self.paste(True)
    else:
        self.createLine(addAnother)

def deleteControl(self):
    # If we're holding stuff, just get rid of it
    if self.copying is not None:
        self.copying = None
    # If theres a bound there, delete all the bounds there
    elif self.focusLoc in self.bounds:
        while self.focusLoc in self.bounds:
            self.bounds.remove(self.focusLoc)
    else:
        self.deleteLine()
    self.repaint()

def clearSelectionControl(self):
    if self.copying is not None:
        self.copying = None
        self.repaint()
    else:
        if self.pattern is not None:
            self.destroySelection(False)
        else:
            self.deleteLine()

def clearAll(self):
    debug()
    self.lines.clear()
    self.bounds.clear()
    self.currentLine = None
    self.currentMirrorState = 0
    self.repaint()

def rotateControl(self):
    # This is the rotation matrix
    rot = np.radians(45)
    self.transform(np.array([
        [np.cos(rot), np.sin(rot),  0],
        [-np.sin(rot), np.cos(rot), 0],
        [0, 0, 1],
    ]), regenerate=True)

def rotateSelectionControl(self):
    if self.copying is None:
        return
    # This is the combinded transformation to rotate by 90°, and also translate by x, y
    self._selectionRotation += 1
    self._selectionTransformation = self._selectionTransformation @ np.array([
        [0,  1, 0],
        [-1, 0, 0],
        [0,  0,  1],
    ])
    self.repaint()

def selectAreaControl(self):
    self.selecting = None
    # If there's already a selection, delete it and make a new one
    self.bounds.clear()
    self.addBound(False)
    self.addBound(False)

def deleteLine(self, at=None):
    if at is None:
        at = self.focusLoc

    #* Don't remove anything if there's a current line
    if self.currentLine is not None:
        self.currentLine = None
        return
    #* If there's a bound there, don't delete all the lines under it as well
    if self.focusLoc in self.bounds:
        # But remove all of them if there's duplicates there
        while self.focusLoc in self.bounds:
            self.bounds.remove(self.focusLoc)
    else:
        all = [at.transformed(t) for t in self._mirrorTransforms()]
        # This should not be nessicarry, I have no idea why the 3 lines don't work by themselves.
        linesStillAtFocus = True
        while linesStillAtFocus:
            linesStillAtFocus = False

            for i in self.lines:
                if i.start in all or i.end in all:
                    self.lines.remove(i)

            for i in self.lines:
                if i.start in all or i.end in all:
                    linesStillAtFocus = True

def specificErase(self):
    # If there's nothing there, don't do anything
    if self.focusLoc in [i.end for i in self.lines] + [i.start for i in self.lines]:
        if self.specificEraseBuffer == None:
            self.specificEraseBuffer = self.focusLoc.copy()
        else:
            assert type(self.specificEraseBuffer) is Point
            for index, i in enumerate(self.lines):
                if (i.start == self.focusLoc and i.end == self.specificEraseBuffer) or \
                   (i.end == self.focusLoc   and i.start == self.specificEraseBuffer):
                    del self.lines[index]
            self.specificEraseBuffer = None
    else:
        self.specificEraseBuffer = None

def addBound(self, remove=True):
    # If there's already a bound there, just remove it instead
    # If selecting is None, then do add it, becuase it'll move around
    # if self.focusLoc in self.bounds and self.selecting is not None:
    if remove:
        while self.focusLoc in self.bounds:
            debug('removing bound')
            # self.bounds.remove(self.focusLoc + self.translation)
            self.bounds.remove(self.focusLoc)
    else:
        # self.bounds.append(self.focusLoc.copy() + self.translation)
        self.bounds.append(self.focusLoc.copy())
    self.repaint()

def goHome(self):
    """ Resets the transformation back to 0 """
    self.transform(transform2Transformation(self.transformation, self.home), regenerate=True)

def cancelControl(self):
    if self.copying is not None:
        self.copying = None
        self.repaint()
    else:
        if S.settings.value('window/esc_quits'):
            self.window().close()
        else:
            event.ignore()
            return

def undo(self):
    thisUndo = []
    # Always remove the currentLine
    self.currentLine = None
    if self.currentLine == None and len(self.lines) > 0:
        # del self.lines[-1]
        thisUndo.append(self.lines.pop())
        if self.MIRROR_STATES[self.currentMirrorState] >= 2 and len(self.lines) > 0:
            thisUndo.append(self.lines.pop())
            if self.MIRROR_STATES[self.currentMirrorState] >= 4 and len(self.lines) > 0:
                thisUndo.append(self.lines.pop())
                if len(self.lines) > 1:
                    thisUndo.append(self.lines.pop())
        self.redoBuffer.append(thisUndo)

def redo(self):
    if len(self.redoBuffer):
        self.lines += self.redoBuffer.pop()

def cut(self):
    self.copy()
    self.destroySelection()
    self.repaint()

def copy(self):
    self.clipboard = self.pattern
    self.copying = self.clipboard
    if self.copying is not None:
        self.currentLine = None
    # We need to repaint the new pattern
    self.repaint()

def paste(self, keep=True):
    if self.copying is not None:
        # Pattern.transformed() gives us a QPainterPath, so we have to translate the Lines ourself
        for line in self.copying.allLines():
            self.lines.append(line.transformed(self.copyTransform()))

        if not keep:
            self.copying = None
            self._selectionTransformation = np.identity(3)
            self._selectionRotation = 0
    else:
        self.copying = self.clipboard
    self.repaint()

def debugControl(self):
    if S.debugging:
        debug('debug key pressed')
        # print('\n'.join(map(str, self.lines)))
        # with open(self.getFile(save=False), 'r') as f:
            # self.deserialze(f.read())
        # print(self.actions())
        debug(S.settings['pattern/include_halfsies'], 'include halfsies')
