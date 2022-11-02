from Cope import todo, debug, untested, confidence, flattenList
from PyQt6.QtCore import QEvent, QFile, QLine, QLineF, QRect, QRectF, Qt
from PyQt6.QtGui import QBrush, QColor, QPainter, QPainterPath, QPen, QTransform, QPolygon, QPolygonF
from PyQt6.QtWidgets import QFileDialog, QMainWindow, QWidget
import Pattern
from Line import Line
from Point import Pair


def createLine(self, linkAnother=False):
    # Create a new line
    if self.currentLine is None:
        # self.focusLoc used to be deepcopied, in case you're getting weird errors here
        self.currentLine = Line(self.focusLoc.copy(), pen=self.currentPen)
    else:
        # Don't create Lines with no length
        if self.currentLine.start == self.focusLoc:
            self.currentLine = None
        else:
            newLine = self.currentLine.finished(self.focusLoc.copy())
            self.lines.append(newLine)
            self.lines += self.mirrorLine(newLine)
            # self.focusLoc used to be deepcopied, in case you're getting weird errors here
            self.currentLine = Line(self.focusLoc.copy(), pen=self.currentPen) if linkAnother else None
    # Make sure we update the pattern, cause it might have changed
    self.updatePattern()

def mirrorLine(self, line):
    #* Check if there's already a line there (so it doesn't get bolder (because of anti-aliasing))
    dontDraw = False
    for k in self.lines:
        if line == k or (line.start == k.end and line.end == k.start):
            dontDraw = True

    #* Check if the start and end are the same (no line would be drawn)
    # if line.start != line.end and not dontDraw:
        # self.lines.append(i)

    lines = []

    # Get the dots closest to halfway (this is not necissarily the position of any dot)
    halfway = Pair(min(self.dots, key=lambda p:abs(p[0] - self.width()/2))[0],
                    min(self.dots, key=lambda p:abs(p[1] - self.height()/2))[1])

    # Mirror accross the vertical axis
    if self.MIRROR_STATES[self.currentMirrorState] in [1, 4]:
        starty = halfway.height + (halfway.height - line.start.y) + 0
        endy   = halfway.height + (halfway.height - line.end.y)   + 0
        vertStart = Point(line.start.x, starty)
        vertEnd   = Point(line.end.x,   endy)
        lines.append(Line(vertStart, vertEnd, line.pen))

    # Mirror accross the horizontal axis
    if self.MIRROR_STATES[self.currentMirrorState] >= 2:
        startx = halfway.width + (halfway.width - line.start.x) + 0
        endx   = halfway.width + (halfway.width - line.end.x)   + 0
        horStart = Point(startx, line.start.y)
        horEnd   = Point(endx,   line.end.y)
        lines.append(Line(horStart, horEnd, line.pen))

        # Mirror in the corner
        if self.MIRROR_STATES[self.currentMirrorState] >= 4:
            corStart = Point(startx, starty)
            corEnd   = Point(endx,   endy)
            lines.append(Line(corStart, corEnd, line.pen))

    return lines

def deleteLine(self, at=None):
    if at is None:
        at = self.focusLoc

    #* Don't remove anything if there's a current line
    if self.currentLine is not None:
        self.currentLine = None
    #* If there's a bound there, don't delete all the lines under it as well
    # elif self.focusLoc + self.translation in self.bounds:
    elif self.focusLoc in self.bounds:
        # But remove all of them if there's duplicates there
        # while self.focusLoc + self.translation in self.bounds:
        while self.focusLoc in self.bounds:
            # self.bounds.remove(self.focusLoc + self.translation)
            self.bounds.remove(self.focusLoc)
    else:
        # This should not be nessicarry, I have no idea why the 3 lines don't work by themselves.
        linesStillAtFocus = True
        while linesStillAtFocus:
            linesStillAtFocus = False

            for i in self.lines:
                if i.start == at or i.end == at:
                    self.lines.remove(i)

            for i in self.lines:
                if i.start == at or i.end == at:
                    linesStillAtFocus = True

    self.updatePattern()

def specificErase(self):
    # If there's nothing there, don't do anything
    if self.focusLoc + self.translation in [i.end for i in self.lines] + [i.start for i in self.lines]:
        if self.specificEraseBuffer == None:
            self.specificEraseBuffer = self.focusLoc + self.translation
        else:
            assert(type(self.specificEraseBuffer) == Point)
            for index, i in enumerate(self.lines):
                if (i.start == self.focusLoc + self.translation and i.end == self.specificEraseBuffer) or \
                    (i.start == self.specificEraseBuffer        and i.end == self.focusLoc + self.translation):
                    del self.lines[index]
            self.specificEraseBuffer = None
    else:
        self.specificEraseBuffer = None
    self.updatePattern()
