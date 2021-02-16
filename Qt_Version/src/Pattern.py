from Point import CoordPoint, TLPoint, GLPoint, InfPoint, Sizef
from Line import Line
from copy import deepcopy
# from Geometry import scalePoint, scaleLines, scaleLines_ip
from math import ceil
from Cope import reprise, debug, timeFunc, debugged, frange
from PyQt5.QtCore import QRectF


# try:
#     from OpenGL.GL import *
#     from OpenGL.GLU import *
#     from OpenGL.GLUT import *
# except ImportError:
#     app = QApplication(sys.argv)
#     QMessageBox.critical(None, "OpenGL hellogl", "PyOpenGL must be installed to run this example.")
#     exit(1)


@reprise
class Pattern:
    def __init__(self, lines, halfLines, dotSpread, centerPoint, rect):
        if not len(lines) and not len(halfLines):
            raise UserWarning('No lines in this pattern!')

        self.ds = dotSpread
        self.cp = centerPoint

        self.lines = []
        self.halfLines = []
        # allLines = lines + halfLines
        self.size = (round(rect.width() / dotSpread), round(rect.height() / dotSpread))
        # anchorPoint = InfPoint(rect.topLeft(), None, dotSpread, centerPoint)
        # anchorPoint = Pointf(min([i.start for i in allLines] + [i.end for i in allLines], key=lambda l: l.x).x,
                            #  min([i.start for i in allLines] + [i.end for i in allLines], key=lambda l: l.y).y)

        for line in lines:
            self.lines.append(Line(None, line.start.asInf(self.cp, self.ds),
                                         line.end.asInf(self.cp, self.ds),
                                         line.color))

        for line in halfLines:
            self.halfLines.append(Line(None, line.start.asInf(self.cp, self.ds),
                                             line.end.asInf(self.cp, self.ds),
                                             line.color))

        debug(self.lines, self.halfLines)

    def getSize(self, dotSpread):
        return Sizef(self.size) * dotSpread
        # lines = self.lines
        # if includeHalfsies:
        #     lines += self.halfLines

        # return QRectF(min([i.start for i in lines] + [i.end for i in lines], key=lambda l: l.x).x * dotSpread,
        #               min([i.start for i in lines] + [i.end for i in lines], key=lambda l: l.y).y * dotSpread,
        #               max([i.start for i in lines] + [i.end for i in lines], key=lambda l: l.x).x * dotSpread,
        #               max([i.start for i in lines] + [i.end for i in lines], key=lambda l: l.y).y * dotSpread)

    def linesAtPos(self, pos, centerPoint, dotSpread, includeHalfsies=True):
        returnLines = ()

        for line in self.lines + self.halfLines if includeHalfsies else []:
            returnLines += (Line(None, line.start.asInf(centerPoint, None) + pos.asInf(centerPoint, dotSpread),
                                       line.end.asInf(centerPoint, None)   + pos.asInf(centerPoint, dotSpread),
                                       line.color),)

        return returnLines

    def repeat(self, areaSize, centerPoint, dotSpread, overlap=[0, 0], includeHalfsies=True):
        returnLines = ()
        # debug(dotOffset[0] - dotSpread, areaSize.width(), patternSize.width() + (overlap[0] * dotSpread), name=('start', 'stop', 'skip'), color=4, showFunc=True)

        # for x in frange(dotOffset[0] - dotSpread, areaSize.width(), patternSize.width() + (overlap[0] * dotSpread)):
        #     for y in frange(dotOffset[1] - dotSpread, areaSize.height(), patternSize.height() + (overlap[1] * dotSpread)):
        #         raise StopIteration(x, y)
        #         returnLines += self.linesAtPos(Pointf(x, y), dotSpread, includeHalfsies)

        # for x in frange(-1, 1, self.getSize(dotSpread)[0] + (overlap[0] * dotSpread) + (dotSpread / (areaSize[1] / 2))):
            # for y in frange(-1, 1, self.getSize(dotSpread)[1] + (overlap[1] * dotSpread) + (dotSpread / (areaSize[1] / 2))):
                # returnLines += self.linesAtPos(InfPoint(x, y, self.ds, self.cp), dotSpread, centerPoint, includeHalfsies)

        # debug(areaSize, centerPoint, dotSpread, overlap)

        for x in range(int(-(areaSize[0] / 2)), int(areaSize[0] / 2), self.size[0]):
            for y in range(int(-(areaSize[1] / 2)), int(areaSize[1] / 2), self.size[1]):
                returnLines += self.linesAtPos(InfPoint(x, y, centerPoint, dotSpread), centerPoint, dotSpread, includeHalfsies)


        return debugged(list(returnLines))

    def __str__(self):
        return f"Pattern[lines={self.lines}(len={len(self.lines)}), halfLines={self.halfLines}(len={len(self.halfLines)})]"
