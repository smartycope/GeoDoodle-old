from Color import Color, namedColor
from Point import Point
from Line import Line
from Geometry import scalePoint
from math import ceil
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame
DIR = os.path.dirname(__file__) + '/../'

class Pattern:
    def __init__(self, lines, halfLines, rect, dotSpread, startPoint=Point(0, 0)):
        self.rect = rect

        self.halfsies = False
        self.overlap = [0, 0]

        anchorPoint =  Point(*self.rect.topleft)
        # self.anchorPoint = Point(0, 0)
        self.startPoint = startPoint
        self.lines = []
        self.halfLines = []
        self.dotSpread = dotSpread

        #* Now loop through and get the relative points of all the lines to the anchor point
        #* There is no concept of dotSpread here; they are related to each other via how many boxes seperate them
        for line in lines:
            self.lines.append(Line((line.start + startPoint - anchorPoint) / dotSpread,
                                   (line.end   + startPoint - anchorPoint) / dotSpread) )

        for line in halfLines:
            self.lines.append(Line((line.start + startPoint - anchorPoint) / dotSpread,
                                   (line.end   + startPoint - anchorPoint) / dotSpread) )

        self.size = (Point(*self.rect.bottomright) + startPoint - anchorPoint) / self.dotSpread

    def getSize(self, scale=None, includeOverlap=False, includeHalfsies=False):
        if scale is None:
            scale = self.dotSpread

        s = self.size

        if includeOverlap:
            s[0] += self.overlap[0]
            s[1] += self.overlap[1]

        if includeHalfsies:
            print('Warning: Pattern.getSize(includeHalfsies=True) has not been implemented yet.')

        return s * scale

        #* get the bottom right corner
        #   i.e. The largest x and the largest y
        # return [ max(max(self.lines, key=lambda l:l.start.x).start.x,
        #               max(self.lines, key=lambda l:l.end.x  ).end.x) * scale,
        #          max(max(self.lines, key=lambda l:l.start.y).start.y,
        #               max(self.lines, key=lambda l:l.end.y  ).end.y) * scale
        #        ]

    #* WARNING: This will not round to the nearest dot; make sure the position is valid before it is passed
    def getPatternAtLoc(self, pos, scale=None, halfsies=False):
        if scale is None:
            scale = self.dotSpread

        returnWholes = []
        returnHalfs  = []

        for line in self.lines:
            returnWholes.append(Line(Point((line.start.x * scale) + pos.x, (line.start.y * scale) + pos.y),
                                     Point((line.end.x   * scale) + pos.x, (line.end.y   * scale) + pos.y)))

        if halfsies:
            for line in self.halfLines:
                returnHalfs.append(Line(Point((line.start.x * scale) + pos.x, (line.start.y * scale) + pos.y),
                                        Point((line.end.x   * scale) + pos.x, (line.end.y   * scale) + pos.y)))

            return returnWholes + returnHalfs
        else:
            return returnWholes

    #* Note: size is the size of the thing we're drawing for, not the size of the pattern
    # TODO This works great normally, but doesn't work for the repeat preview for some reason.
    def repeat(self, size, offScreenAmount, overlap=None, startPoint=None, halfsies=None, dotSpread=None, preview=False):
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
        patternSize = self.getSize(dotSpread, includeOverlap=True)

        size = [size[0] + (overlap[0] * dotSpread), size[1] + (overlap[1] * dotSpread)]
        
        # patternSize[0] /= 2
        # patternSize[1] /= 2

        #* First determine how many patterns can fit in the x and y
        width = (patternSize[0] - (overlap[0] * dotSpread))
        height = (patternSize[1] - (overlap[1] * dotSpread))
        if not width:
            width += 1
        if not height:
            height += 1
        xAmount = ceil((size[0] + offScreenAmount + overlap[0]) / width)
        yAmount = ceil((size[1] + offScreenAmount + overlap[1]) / height)

        # print('xAmount:', xAmount)
        # print('yAmount:', yAmount)
        # print('size of the pattern:', patternSize)
        # print('overlap:', overlap)
        # print('startPoint:', startPoint)
        # print('objective pattern size:', self.getSize(1))

        for x in range(xAmount):
            for y in range(yAmount): # I do not know why "- (self.getSize(1)[] * 2)" is nessicary
                #* This works at size 16 on the pattern preview surface
                # p = Point( (x * 2 * (patternSize[0] - (self.getSize(1)[0] * 2) + (overlap[0] * (dotSpread - 2)) ) ) - offScreenAmount + startPoint.x, 
                        #    (y * 2 * (patternSize[1] - (self.getSize(1)[1] * 2) + (overlap[1] * (dotSpread - 2)) ) ) - offScreenAmount + startPoint.y )
                if preview and False:
                    # p = Point( (x * 2 * (patternSize[0] + (overlap[0] * (dotSpread - 1)) ) ) - offScreenAmount + startPoint.x, 
                    #            (y * 2 * (patternSize[1] + (overlap[1] * (dotSpread - 1)) ) ) - offScreenAmount + startPoint.y )
                    p = Point( (x * 2 * (patternSize[0] - (self.getSize(1)[0]) + (overlap[0] * (dotSpread - 1)) ) ) - offScreenAmount + startPoint.x, 
                               (y * 2 * (patternSize[1] - (self.getSize(1)[1]) + (overlap[1] * (dotSpread - 1)) ) ) - offScreenAmount + startPoint.y )
                else:
                    p = Point( (x * (patternSize[0] + (overlap[0] * dotSpread) ) ) - offScreenAmount + startPoint.x, 
                               (y * (patternSize[1] + (overlap[1] * dotSpread) ) ) - offScreenAmount + startPoint.y )
                returnLines += self.getPatternAtLoc(p, halfsies=halfsies)

        # print('length of return lines:', len(returnLines))
        # for i in range(6):
        #     print('return lines', i, returnLines[i + 50])

        return returnLines