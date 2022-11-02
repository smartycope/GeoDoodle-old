import numpy as np
from Cope import todo, debug, untested, confidence, flattenList
from PyQt5.QtCore import QEvent, QFile, QLine, QLineF, QRect, QRectF, Qt
from PyQt5.QtGui import QBrush, QColor, QPainter, QPainterPath, QPen, QTransform, QPolygon, QPolygonF
from PyQt5.QtWidgets import QFileDialog, QMainWindow, QWidget
import Pattern
from Line import Line
from Point import Point, Pair

#* Dots
def regenerateDots(self, size:'QSize'):
    #* The top-left corner-centric way of generating dots
    # self.dots = np.arange(start, stop)
    # self.dots = []
    # We don't actually need to start drawing from there, we only need to offset it a little so it *looks*
    #   like we started drawing from there
    # for x in range(round(self.translation.x % self.dotSpread), round(size.width()), self.dotSpread):
    #     for y in range(round(self.translation.y % self.dotSpread), round(size.height()), self.dotSpread):
    #         self.dots.append(Point(x, y))
    #Reshapes 1d array in to 2d, containing 10 rows and 5 columns.
    # self.dots = np.arange(self.translation.x % self.dotSpread, size.width(), self.dotSpread).reshape(10,5)
    # self.dots = np.arange(0, size.width()-self.dotSpread, self.dotSpread).reshape(10,5)
    # np.atleast_2d()

    # This creates an array of the x coordinates, then an array filled with the current y coordinate, then
    #   merges them together
    # These 2 lines are the same as...
    x = np.arange(self.translation.x % self.dotSpread, size.width(), self.dotSpread, int)
    self.dots = np.column_stack([x, np.repeat(0, len(x))])

    for y in range(round(self.translation.y % self.dotSpread), round(size.height()), self.dotSpread):
        # ...these 2 lines (dang python doesn't have any do-while loops)
        x = np.arange(self.translation.x % self.dotSpread, size.width(), self.dotSpread, int)
        self.dots = np.concatenate((self.dots, np.column_stack([x, np.repeat(y, len(x))])))

    # self.untranslatedDots = self.dots

def translate(self, amt:'Point'):
    if self.SMOOTH_TRANSLATION:
        self.translation += amt
    else:
        self.translationBuffer += amt
        # These 2 lines are equivalent
        amt = self.dotSpread * (self.translationBuffer // self.dotSpread)
        # amt = self.translationBuffer - (self.translationBuffer % self.dotSpread)
        # This is kinda cool, actually: a * (b // a) == b - (b % a)

        self.translationBuffer -= amt
        self.translation += amt

        if not amt.x and not amt.y:
            return


    # Update the dots
    if self.SMOOTH_TRANSLATION:
        self.regenerateDots(self.size())
        #* You should be able to update the dots instead of regenerating them, but I can't get it to work,
        #   and it doesn't actually seem any faster
        # self.dots = (round(abs(self.translation)).data() % self.untranslatedDots)

    self.updateMirror()
    # for line in self.mirrorLines:
        # line.translate(*amt.data())

    # Translate the lines
    for line in self.lines:
        line.translate(*amt.data())

    # if self.AUTO_IMPRINT_PATTERN:
        # for line in self.patternLines:
            # line.translate(*amt.data())

    # Translate the currentLine (just the start)
    if self.currentLine is not None:
        # Because the currentLine is immutable for some reason??
        self.currentLine = Line(self.currentLine.start + amt, self.focusLoc)

    #// Actually don't translate bounds, because lines are translated, so we want bounds to be global
    # Actually do translate bounds, because the lines ARE translated, so we want bounds to translate with them
    # Translate the bounds
    for bound in self.bounds:
        bound += amt

    self.repaint()
    # Focus may be off because we have a new dot array
    if self.SMOOTH_TRANSLATION:
        self.updateFocus()

def goHome(self):
    """ Just resets the translation back to 0 """
    # self.translation = Point(0, 0)
    self.translate(self.translation*-1)
