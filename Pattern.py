from Color import Color, namedColor
from Point import Point
from Line import Line
from Geometry import scalePoint
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame
DIR = os.path.dirname(__file__) + '/'

class Pattern:
    halfsies = None
    overlap = None

    def __init__(self, lines, halfLines, rect, dotSpread):
        # self.lines = lines
        self.rect = rect

        self.anchorPoint =  Point(*self.rect.topleft) # Point(10000, 10000)
        self.lines = []
        self.halfLines = []
        self.dotSpread = dotSpread

        #// First get the top left corner
        # for line in lines:
        #     for p in [line.start, line.end]:
        #         if p.x < self.anchorPoint.x:
        #             self.anchorPoint.x = p.x
        #         if p.y < self.anchorPoint.y:
        #             self.anchorPoint.y = p.y

        #* Now loop through and get the relative points of all the lines to the anchor point
        for line in lines:
            self.lines.append(Line(Point(line.start.x - self.anchorPoint.x, line.start.y - self.anchorPoint.y), 
                                   Point(line.end.x   - self.anchorPoint.x, line.end.y   - self.anchorPoint.y)))

        for line in halfLines:
            self.halfLines.append(Line(Point(line.start.x - self.anchorPoint.x, line.start.y - self.anchorPoint.y), 
                                       Point(line.end.x   - self.anchorPoint.x, line.end.y   - self.anchorPoint.y)))

        # self.halfLines = halfLines
        # self.lines = lines

    def getSize(self, scale=None):
        if scale is None:
            scale = self.dotSpread
        # #* get the bottom right corner
        # bottomRight = Point(-10000, -10000)
        # for line in self.lines:
        #     for p in [line.start, line.end]:
        #         if p.x > bottomRight.x:
        #             bottomRight.x = p.x
        #         if p.y > bottomRight.y:
        #             bottomRight.y = p.y
        
        return scalePoint(Point(*self.rect.size), self.dotSpread, scale).data()

    #* WARNING: This will not round to the nearest dot; make sure the position is valid before it is passed
    def getPatternAtLoc(self, pos, halfsies=False):
        # print(f'halfsies: {len(self.halfLines)}')
        # print(f'wholsies: {len(self.lines)}')

        returnWholes = []
        returnHalfs  = []

        for line in self.lines:
            # for p in [line.start, line.end]:
            returnWholes.append(Line(Point(line.start.x + pos.x, line.start.y + pos.y),
                                     Point(line.end.x   + pos.x, line.end.y   + pos.y)))
                # p.x += pos.x
                # p.y += pos.y

        if halfsies:
            for line in self.halfLines:
                # for p in [line.start, line.end]:
                returnHalfs.append(Line(Point(line.start.x + pos.x, line.start.y + pos.y),
                                        Point(line.end.x   + pos.x, line.end.y   + pos.y)))
                    # p.x += pos.x
                    # p.y += pos.y

            # return self.lines + self.halfLines
            return returnWholes + returnHalfs
        else:
            # return self.lines
            return returnWholes
