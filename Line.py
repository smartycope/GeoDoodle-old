from Color import Color, namedColor
from Point import Point
import pygame, json

import os; DIR = os.path.dirname(__file__) + '/'

class Line:
    def __init__(self, start, end = None, color = None):
        self.start = start
        if end == None:
            self.end = start
        else:
            self.end = end
        
        if color is None:
            with open(DIR + 'settings.json') as f:
                tmp = json.load(f)
                self.color = tuple(tmp['defaultLineColor'])
                # self._width = tmp['lineThickness']
        else:
            self.color = color

    def finish(self, loc):
        self.end = loc

    def isFinished(self):
        return self.end != None

    def draw(self, display):
        pygame.draw.aaline(display, self.color, self.start.data(), self.end.data())
        # pygame.draw.line(display, self.color, self.start.data(), self.end.data(), width=self._width)
