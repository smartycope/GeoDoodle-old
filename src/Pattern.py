from Color import Color, namedColor
from Point import Point
from Line import Line
from Geometry import scalePoint, scaleLines, scaleLines_ip
from math import ceil
from copy import deepcopy
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame

import os; DIR = os.path.dirname(os.path.dirname(__file__)); DIR += '\\main\\' if os.name == 'nt' else '/'


class Pattern:
    def __init__(self, lines, halfLines, rect, dotSpread, startPoint=Point(0, 0)):
        self.rect = rect

        self.halfsies = False
        self.overlap = [0, 0]

        anchorPoint =  Point(self.rect.topleft)
        self.startPoint = startPoint
        self.lines = []
        self.halfLines = []
        self.dotSpread = dotSpread

        #* Now loop through and get the relative points of all the lines to the anchor point
        #* There is no concept of dotSpread here; they are related to each other via how many boxes seperate them
        # self.lines     = scaleLines(lines,     Point(0, 0), self.dotSpread, 1)
        # self.halfLines = scaleLines(halfLines, Point(0, 0), self.dotSpread, 1)

        # self.lines = lines

        # for line in self.lines:
        #     for point in [line.start, line.end]:
        #         scaleX = True
        #         scaleY = True

        #         if point.x == 0:
        #             scaleX = False
        #         if point.y == 0:
        #             scaleY = False

        #         # returnPoint = Point(point)


        #         # if scaleX:
        #         #     point.x -= ((originPoint.x - returnPoint.x) / startDotSpread) * (newDotSpread - startDotSpread)
        #         # if scaleY:
        #         #     point.y -= ((originPoint.y - returnPoint.y) / startDotSpread) * (newDotSpread - startDotSpread)


        #         if scaleX:
        #             point.x -= (point.x / dotSpread)
        #         if scaleY:
        #             point.y -= (point.y / dotSpread)

        # + startPoint - anchorPoint
        # + startPoint - anchorPoint
        # + startPoint - anchorPoint
        # + startPoint - anchorPoint

        for line in lines:
            self.lines.append(Line((line.start - anchorPoint) / dotSpread,
                                   (line.end   - anchorPoint) / dotSpread,
                                   line.color))

        for line in halfLines:
            self.lines.append(Line((line.start - anchorPoint) / dotSpread,
                                   (line.end   - anchorPoint) / dotSpread,
                                   line.color))

        # for i in self.lines:
        #     print(i)

        self.size = (Point(self.rect.bottomright) + startPoint - anchorPoint) / self.dotSpread

    def getSize(self, scale=None, overlap=None, halfsies=None):
        if scale is None:
            scale = self.dotSpread

        s = Point(self.size)

        if overlap is not None:
            s += Point(overlap)

        if halfsies is not None:
            print('Warning: Pattern.getSize(includeHalfsies=True) has not been implemented yet.')

        return s * scale

    #* WARNING: This will not round to the nearest dot; make sure the position is valid before it is passed
    def getPatternAtLoc(self, pos, scale=None, halfsies=False):
        if scale is None:
            scale = self.dotSpread

        returnWholes = []
        returnHalfs  = []

        for line in self.lines:
            returnWholes.append(Line((line.start * scale) + pos,
                                     (line.end   * scale) + pos,
                                      line.color))

        if halfsies:
            for line in self.halfLines:
                returnHalfs.append(Line((line.start * scale) + pos,
                                        (line.end   * scale) + pos,
                                         line.color))

            return returnWholes + returnHalfs
        else:
            return returnWholes

    #* Note: size is the size of the thing we're drawing for, not the size of the pattern
    # TODO This works great normally, but doesn't work for the repeat preview for some reason.
    def repeat(self, size, offScreenAmount, overlap=None, startPoint=None, halfsies=None, dotSpread=None):
        print('startPoint:', startPoint)
        if startPoint is None:
            startPoint = self.startPoint
        if halfsies is None:
            halfsies = self.halfsies
        if overlap is None:
            overlap = self.overlap
        if dotSpread is None:
            dotSpread = self.dotSpread

        returnLines = []
        patternSize = self.getSize(dotSpread, overlap=overlap)
        print('patternSize:', Point(patternSize) / dotSpread)

        #* The size of the thing we're drawing onto
        surfaceSize = [size[0] + (overlap[0] * dotSpread), size[1] + (overlap[1] * dotSpread)]

        #* Determine how many patterns can fit in each direction
        xAmount = ceil((surfaceSize[0] + offScreenAmount) / patternSize[0])
        yAmount = ceil((surfaceSize[1] + offScreenAmount) / patternSize[1])

        for x in range(xAmount):
            for y in range(yAmount): 
                X = (x * patternSize[0]) + startPoint.x - (offScreenAmount / 2)
                Y = (y * patternSize[1]) + startPoint.y - (offScreenAmount / 2)
                returnLines += self.getPatternAtLoc(Point(X, Y), scale=dotSpread, halfsies=halfsies)

        return returnLines