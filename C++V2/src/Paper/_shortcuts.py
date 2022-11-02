from Cope import todo, debug, untested, confidence, flattenList
from PyQt5.QtCore import QEvent, QFile, QLine, QLineF, QRect, QRectF, Qt
from PyQt5.QtGui import QBrush, QColor, QPainter, QPainterPath, QPen, QTransform, QPolygon, QPolygonF
from PyQt5.QtWidgets import QFileDialog, QMainWindow, QWidget
import Pattern
from Line import Line
from Point import Point, Pair


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
    self.updatePattern()

def redo(self):
    if len(self.redoBuffer):
        self.lines += self.redoBuffer.pop()
        self.updatePattern()

def cut(self):
    self.copy()
    self.destroySelection()
    self.repaint()

def copy(self):
    self.updatePattern()
    self.clipboard = self.pattern
    self.copying = self.clipboard
    if self.copying is not None:
        self.currentLine = None
    # We need to repaint the new pattern
    self.repaint()

def paste(self, keep=True):
    if self.copying is not None:
        self.lines += self.copying.translatedLines(*self.focusLoc.data(), Pattern.params.includeHalfsies)
        if not keep:
            self.copying = None
    else:
        self.copying = self.clipboard
        self.repaint()
