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
        self.size = (round(rect.width() / dotSpread), round(rect.height() / dotSpread))


        for line in lines:
            self.lines.append(Line(None, line.start.asInf(self.cp, self.ds),
                                         line.end.asInf(self.cp, self.ds),
                                         line.color))

        for line in halfLines:
            self.halfLines.append(Line(None, line.start.asInf(self.cp, self.ds),
                                             line.end.asInf(self.cp, self.ds),
                                             line.color))


    def getSize(self, dotSpread):
        return Sizef(self.size) * dotSpread
        # lines = self.lines
        # if includeHalfsies:
        #     lines += self.halfLines

        # return QRectF(min([i.start for i in lines] + [i.end for i in lines], key=lambda l: l.x).x * dotSpread,
        #               min([i.start for i in lines] + [i.end for i in lines], key=lambda l: l.y).y * dotSpread,
        #               max([i.start for i in lines] + [i.end for i in lines], key=lambda l: l.x).x * dotSpread,
        #               max([i.start for i in lines] + [i.end for i in lines], key=lambda l: l.y).y * dotSpread)


    def flippedLines(self, vert, horz, includeHalfsies=True):
        allLines = deepcopy(self.lines + (self.halfLines if includeHalfsies else []))

        if vert:
            center = min([i.start for i in self.lines] + [i.end for i in self.lines], key=lambda l: l.y).y + (self.size[1] / 2)

            for i in allLines:
                i.start.y -= (i.start.y - center) * 2
                i.end.y -= (i.end.y - center) * 2

        if horz:
            center = min([i.start for i in self.lines] + [i.end for i in self.lines], key=lambda l: l.x).x + (self.size[0] / 2)

            for i in allLines:
                i.start.x -= (i.start.x - center) * 2
                i.end.x -= (i.end.x - center) * 2

        return allLines



    def linesAtPos(self, pos, centerPoint, dotSpread, includeHalfsies=True, vert=False, horz=False):
        returnLines = ()

        for line in self.flippedLines(vert, horz, includeHalfsies):
            returnLines += (Line(None, line.start.asInf(centerPoint, dotSpread) - pos.asInf(centerPoint, dotSpread),
                                       line.end.asInf(centerPoint, dotSpread)   - pos.asInf(centerPoint, dotSpread),
                                       line.color),)

        return returnLines

    def repeat(self, areaSize, centerPoint, dotSpread, overlap,
               rowSkip, rowSkipAmt, colSkip, colSkipAmt,
               rowFlip, rowFlipDir, colFlip, colFlipDir,
               includeHalfsies=True):

        returnLines = ()
        row = col = 0

        for x in range(int(-(areaSize[0] / 1)), int(areaSize[0] / 1), self.size[0] + overlap[0]):
            row = 0
            col += 1
            for y in range(int(-(areaSize[1] / 1)), int(areaSize[1] / 1), self.size[1] + overlap[1]):
                row += 1
                returnLines += self.linesAtPos(InfPoint(x + (rowSkipAmt if not row % rowSkip else 0),
                                                        y + (colSkipAmt if not col % colSkip else 0),
                                                        centerPoint, dotSpread),
                                               centerPoint, dotSpread, includeHalfsies,
                                               vert=(rowFlipDir=='Vertically'   and not row % rowFlip) or \
                                                    (colFlipDir=='Vertically'   and not row % rowFlip),
                                               horz=(rowFlipDir=='Horizontally' and not col % colFlip) or \
                                                    (colFlipDir=='Horizontally' and not col % colFlip))

        return list(returnLines)

    def __str__(self):
        return f"Pattern[lines={self.lines}(len={len(self.lines)}), halfLines={self.halfLines}(len={len(self.halfLines)})]"
