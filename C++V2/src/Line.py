import sys
from typing import Unionp

import numpy as np
from Cope import debug, getMidPoint, invertColor, reprise, untested, confidence
from PyQt5.QtCore import QLine, QLineF, QPoint, QPointF
from PyQt5.QtGui import QColor, QFont, QPen
from PyQt5.QtWidgets import QApplication, QLabel

from Point import Point
import json_fix


@reprise
class Line(QLineF):
    def __init__(self, start, end=None, pen: QPen = QPen(), label=None):
        self.start = start
        self.end = end if end else start
        self.pen = pen
        self.label = label
        super().__init__(self.start, self.end)

    def finish(self, end):
        self.end = end

    def finished(self, end):
        """ An inline version of finish """
        self.end = end
        return self.copy()

    def copy(self):
        return Line(self.start, self.end, self.pen, self.label)

    def isFinished(self):
        return self.end != None

    def within(self, rect) -> 'None, True, False':
        """ Returns None if the line is not within rect
            Returns False if the line is only partially within rect
            Returns True if the line is entirely within rect
        """
        start = rect.contains(self.start)
        end = rect.contains(self.end)
        if start and end:
            return True
        elif start or end:
            return False
        else:
            return None

    @untested
    def createLabel(self, parent, dotSpread, dotSpreadMeasure, dotSpreadUnit, backgroundColor):
        if self.label is None:
            self.label = QLabel(
                f'{round(self.getLen(dotSpread, dotSpreadMeasure), 1)} {dotSpreadUnit}', parent)
            self.label.font().setBold(False)
            self.label.font().setFamily('Times')
            # self.label.setStyleSheet(f"color:rgba{invertColor(backgroundColor)}")
            self.label.setStyleSheet(f"color:rgba{self.color}")
            self.label.setGeometry(
                *self.getLenLoc().asTL().data(), self.label.width(), self.label.height())
        return self.label

    @untested
    def getDist(self):
        # Qt undoubtedly has a function built into QPoint that does this
        return dist(self.start, self.end)

    @untested
    def getLen(self, dotSpread, multiplier):
        return (self.getDist() / dotSpread) * multiplier

    @untested
    def getLenLoc(self):
        return getMidPoint(self.start, self.end)

    def __str__(self):
        return f'Line[{self.start}, {self.end}, penColor={self.pen.color().getRgb()}]'

    def __eq__(self, a):
        """ Note that this does *not* compare color """
        try:
            return self.start == a.start and self.end == a.end
        except:
            return False

    def __sub__(self, point):
        assert isinstance(point, (QPoint, QPointF)
                          ), f"Can't add types of Line and {type(point)}"
        return Line(self.start - point, self.end - point, self.pen, self.label)

    def __add__(self, point):
        assert isinstance(point, (QPoint, QPointF)
                          ), f"Can't add types of Line and {type(point)}"
        return Line(self.start + point, self.end + point, self.pen, self.label)

    def __isub__(self, point):
        assert isinstance(point, (QPoint, QPointF)
                          ), f"Can't add types of Line and {type(point)}"
        self.start -= point
        self.end -= point

    def __iadd__(self, point):
        assert isinstance(point, (QPoint, QPointF)
                          ), f"Can't add types of Line and {type(point)}"
        self.start += point
        self.end += point

    def __json__(self, **options):
        return [
            self.start,
            self.end,
            self.pen.color().getRgb(),
            self.label
        ]

    @staticmethod
    def fromJson(j):
        return Line(Point(j[0]), Point(j[1]), QPen(QColor(*j[2])), j[3], j[4])
