from Point import Pointi
# import pygame, json
from PyQt5.QtGui import QColor
from PyQt5.QtCore import QLine

from Cope import DIR, reprise, getTime, timeFunc
# import os; DIR = os.path.dirname(__file__) + '/../'

@reprise
class Line:
    def __init__(self, start, end=None, color=None):
        self.start = start
        if end == None:
            self.end = start
        else:
            self.end = end

        self.color = color

    def finish(self, loc, color=None):
        self.end = loc
        if self.color is None:
            self.color = color

    def isFinished(self):
        return self.end != None

    def draw(self, display):
        """ This must be run from within glBegin/glEnd
        """
        # if self.color is None:
            # assert(not 'No color was specified for a line')
        # display.setPen(self.color)
        # display.drawLine(self.QLine())
        glColor(*self.color)
        glVertex(*self.start.datai())
        glVertex(*self.end.datai())

    def QLine(self):
        return QLine(*self.start.datai(), *self.end.datai())

    def __str__(self):
        return f'Line[{self.start}, {self.end}]'

    def __eq__(self, a):
        try:
            return self.start == a.start and self.end == a.end
        except:
            return False