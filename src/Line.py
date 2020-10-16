from Color import Color, namedColor
from Point import Point
import pygame, json

import os; DIR = os.path.dirname(__file__) + '/../'

class Line:
    def __init__(self, start, end=None, color=None):
        self.start = start
        if end == None:
            self.end = start
        else:
            self.end = end
        
        # if color is None:
        #     with open(DIR + 'settings.jsonc') as f:
        #         tmp = json.load(f)
        #         self.color = tuple(tmp['defaultLineColor'])
        #         # self._width = tmp['lineThickness']
        # else:
        self.color = color

    def finish(self, loc, color=None):
        self.end = loc
        if self.color is None:
            self.color = color

    def isFinished(self):
        return self.end != None

    def draw(self, display):
        if self.color is None:
            assert(not 'No color was specified for a line')
        pygame.draw.aaline(display, self.color, self.start.data(), self.end.data())
        # pygame.draw.line(display, self.color, self.start.data(), self.end.data(), width=self._width)

    def __str__(self):
        return f'[{self.start}, {self.end}]'

    def __eq__(self, a):
        try:
            return self.start == a.start and self.end == a.end
        except:
            return False