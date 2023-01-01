from math import ceil

from Cope import debug, frange, reprise, timeFunc, todo, depricated
from PyQt6.QtCore import QRectF, QSize
from PyQt6.QtGui import QPainterPath, QPainterPathStroker
import numpy as np
from Line import Line
from Point import Point
from Transformation import transform2Transformation

from Singleton import Singleton as S
# What does support look like to you right now?
# This must be hard to talk about
# What is helping you to get through this?
# I'm glad you told me about this
# What has this been like for you?
# I want to understand

# self = QPainterPathStroker(self.lines[0].pen).createStroke(self)

@reprise
class Pattern():
    """ A Pattern consisting of a set of lines, and a set of half lines (lines
        which have one end in and one end out of the set boundary).

        Patterns are transformation agnostic, meaning that you must give it a
        transformation upon construction so it can "nullify" itself. Then in order
        to be usable, you have to use the transformed() function to put it somewhere

        Note the simplified() function, which removes doubled lines
    """
    def __init__(self, lines, halfLines, rect, transformation):
        # Reset all lines back to a "pure" transformation

        # THIS SHOULD WORK
        # I have no idea why this doesn't work, I swear it should
        # trans = np.array([
        #     [1, 0, rect.topLeft().x() / transformation[0, 0]],
        #     [0, 1, rect.topLeft().y() / transformation[1, 1]],
        #     [0, 0, 1],
        # ])
        # delta = trans @ transform2Transformation(transformation, np.identity(3))

        # This "translates" to the top left corner of the given rect, then divides
        # by the scale
        self.lines = []
        self.halfLines = []
        for line in lines:
            tmp = (line - rect.topLeft())
            tmp.start /= transformation[0, 0]
            tmp.end /= transformation[0, 0]
            self.lines.append(tmp)
        for line in halfLines:
            tmp = (line - rect.topLeft())
            tmp.start /= transformation[1, 1]
            tmp.end /= transformation[1, 1]
            self.halfLines.append(tmp)

        # I can't think of a case where this wouldn't work...
        # But maybe it'll break later when I start messing with rotation
        self.size = QSize(int(rect.size().width() / transformation[0, 0]), int(rect.size().height() / transformation[1, 1]))

    def transformed(self, mat:np.ndarray, halfsies=S.settings['pattern/include_halfsies']):
        """ Creates a new QPainterPath and fills it with the translated lines of the pattern """
        new = QPainterPath()
        for line in self.allLines(halfsies):
            new.moveTo(line.start.transformed(mat))
            if line.curve:
                if line.curve == Line.CURVEA:
                    new.cubicTo(ctrlPt1, ctrlPt2, line.end.transformed(mat))
                else:
                    new.cubicTo(ctrlPt1, ctrlPt2, line.end.transformed(mat))
            else:
                new.lineTo(line.end.transformed(mat))

            if S.settings['pattern/simplify_patterns']:
                new.simplified()
        return new

    def allLines(self, halfsies=S.settings.value('pattern/include_halfsies')):
        return self.lines + (self.halfLines if halfsies else [])

    def copy(self):
        # return Pattern(self.lines, self.halfLines, S.settings['dotSpread'], self.rect, self._translation)
        return Pattern(self.lines, self.halfLines, QRect(QPoint(), self.size), np.identity(3))

    def serialize(self):
        return [
            self.lines,
            self.halfLines,
            self.dotSpread,
            [self.rect.x(), self.rect.y(), self.rect.width(), self.rect.height()]
        ]

    @staticmethod
    def deserialize(j):
        return Pattern([Line.fromJson(l) for l in j[0]], [Line.fromJson(l) for l in j[1]], j[2], QRectF(*j[3]), 0)

    def __str__(self):
        return f"Pattern[lines=[\n{self.lines}\n], halfLines=[\n{self.halfLines}\n]]"
