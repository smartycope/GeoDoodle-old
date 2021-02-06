from Point import Pointi
from Line import Line
# from Geometry import scalePoint, scaleLines, scaleLines_ip
from math import ceil
from Cope import reprise, debug, timeFunc
from PyQt5.QtCore import QRect

@reprise
class Pattern:
    def __init__(self, lines, halfLines, dotSpread):
        if not len(lines) and not len(halfLines):
            raise UserWarning('No lines in this pattern!')

        self.lines = []
        self.halfLines = []
        allLines = lines + halfLines
        anchorPoint = Pointi(min([i.start for i in allLines] + [i.end for i in allLines], key=lambda l: l.x).x,
                             min([i.start for i in allLines] + [i.end for i in allLines], key=lambda l: l.y).y)


        for line in lines:
            self.lines.append(Line((line.start - anchorPoint) / dotSpread,
                                   (line.end   - anchorPoint) / dotSpread,
                                    line.color))

        for line in halfLines:
            self.halfLines.append(Line((line.start - anchorPoint) / dotSpread,
                                       (line.end   - anchorPoint) / dotSpread,
                                        line.color))


    def getRect(self, dotSpread, includeHalfsies=True):
        lines = self.lines
        if includeHalfsies:
            lines += self.halfLines

        return QRect(min([i.start for i in lines] + [i.end for i in lines], key=lambda l: l.x).x * dotSpread,
                     min([i.start for i in lines] + [i.end for i in lines], key=lambda l: l.y).y * dotSpread,
                     max([i.start for i in lines] + [i.end for i in lines], key=lambda l: l.x).x * dotSpread,
                     max([i.start for i in lines] + [i.end for i in lines], key=lambda l: l.y).y * dotSpread)

    @timeFunc
    def linesAtPos(self, pos, dotSpread, includeHalfsies=True):
        """ WARNING: This will not round to the nearest dot.
            Make sure the position is valid before it is passed in.
        """
        returnLines = []

        for line in self.lines + self.halfLines if includeHalfsies else []:
            returnLines.append(Line((line.start * dotSpread) + pos,
                                    (line.end   * dotSpread) + pos,
                                     line.color))

        return returnLines

    @timeFunc
    def repeat(self, areaSize, dotSpread, dotOffset, overlap=[0, 0], includeHalfsies=True):
        returnLines = []
        patternSize = self.getRect(dotSpread, includeHalfsies).size()

        for x in range(dotOffset[0] - dotSpread, areaSize.width(), patternSize.width() + (overlap[0] * dotSpread)):
            for y in range(dotOffset[1] - dotSpread, areaSize.height(), patternSize.height() + (overlap[1] * dotSpread)):
                returnLines += self.linesAtPos(Pointi(x, y), dotSpread, includeHalfsies)

        return returnLines


    def __str__(self):
        return f"Pattern[lines={self.lines}(len={len(self.lines)}), halfLines={self.halfLines}(len={len(self.halfLines)})]"