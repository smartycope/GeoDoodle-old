from Color import Color, namedColor
from Point import Point
import pygame
import os; DIR = os.path.dirname(__file__) + '/'

class Pattern:
    # halfsies = False
    # overlap = 0

    def __init__(self, lines, halfLines):
        # self.lines = lines

        self.anchorPoint = Point(10000, 10000)

        #* First get the top left corner
        for line in lines:
            for p in [line.start, line.end]:
                if p.x < self.anchorPoint.x:
                    self.anchorPoint.x = p.x
                if p.y < self.anchorPoint.y:
                    self.anchorPoint.y = p.y

        #* Now loop through and get the relative points of all the lines to the anchor point
        for line in lines:
            for p in [line.start, line.end]:
                p.x = p.x - self.anchorPoint.x
                p.y = p.y - self.anchorPoint.y

        for line in halfLines:
            for p in [line.start, line.end]:
                p.x = p.x - self.anchorPoint.x
                p.y = p.y - self.anchorPoint.y
        
        self.halfLines = halfLines
        self.lines = lines

    def getSize(self):
        #* get the bottom right corner
        bottomRight = Point(-10000, -10000)
        for line in lines:
            for p in [line.start, line.end]:
                if p.x > self.anchorPoint.x:
                    bottomRight.x = p.x
                if p.y > self.anchorPoint.y:
                    bottomRight.y = p.y
        
        return bottomRight.data()

    #* WARNING: This will not round to the nearest dot; make sure the position is valid before it is passed
    def getPatternAtLoc(self, pos, halfsies=False):
        for line in self.lines:
            for p in [line.start, line.end]:
                p.x += pos.x
                p.y += pos.y

        if halfsies:
            for line in self.halfLines:
                for p in [line.start, line.end]:
                    p.x += pos.x
                    p.y += pos.y

            return self.lines + self.halfLines
        else:
            return self.lines


        