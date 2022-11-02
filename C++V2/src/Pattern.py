from Point import Point
from Line import Line
from copy import deepcopy
from math import ceil
from Cope import reprise, debug, timeFunc, frange, todo
from PyQt5.QtCore import QRectF, QSize
from PyQt5.QtGui import QPainterPath, QPainterPathStroker
# The supirior version of namedtuple (literally just namedtuple, but mutable)
from namedlist import namedlist
import json_fix

todo('file extensions arent automattic')


# This is here for consistency's sake, not because this file needs it
_PatternParams = namedlist('PatternParams', 'xOverlap, yOverlap, includeHalfsies, '
                                           'skipRows, skipColumns, skipRowAmt, skipColumnAmt, '
                                           'flipRows, flipColumns, flipRowOrient, flipColumnOrient')
params = _PatternParams(
    xOverlap=0,
    yOverlap=0,
    includeHalfsies=False,
    skipRows=1,
    skipColumns=1,
    skipRowAmt=0,
    skipColumnAmt=0,
    flipRows=1,
    flipColumns=1,
    flipRowOrient=None,
    flipColumnOrient=None
)


# Note the .simplified() function, which removes doubled lines

@reprise
class Pattern(QPainterPath):
    def __init__(self, lines, halfLines, dotSpread, rect, translation):
        # overlap = Point(params.xOverlap, params.yOverlap)
        # Don't just adjust the lines to the top left corner, adjust them so that they'll line up with where the current pattern already is
        self.lines     = [l - rect.topLeft() + translation - (translation % rect.size()) for l in lines]
        self.halfLines = [l - rect.topLeft() + translation - (translation % rect.size()) for l in halfLines]
        self.dotSize = QSize(round(rect.width() / dotSpread), round(rect.height() / dotSpread))
        self.rect = rect
        self._dotSpread = dotSpread
        self._translation = translation

        super().__init__()
        self.generate()
        # if len(self.lines):
            # self = QPainterPathStroker(self.lines[0].pen).createStroke(self)

    def generate(self):
        lines = self.lines + (self.halfLines if params.includeHalfsies else [])
        for line in lines:
            self.moveTo(line.start)
            self.lineTo(line.end)

    def flippedVert(self):
        # center = min([i.start for i in self.lines] + [i.end for i in self.lines], key=lambda l: l.y).y + (self.rect.height() / 2)
        center = self.rect.center()

        flippedLines = self.deepcopy(self.lines)
        for i in flippedLines:
            i.start.y -= (i.start.y - center) * 2
            i.end.y   -= (i.end.y   - center) * 2

        flippedHalfLines = self.deepcopy(self.halfLines)
        for i in flippedHalfLines:
            i.start.y -= (i.start.y - center) * 2
            i.end.y   -= (i.end.y   - center) * 2
        return Pattern(params, flippedLines, flippedHalfLines, self._dotSpread, self.rect, self._translation)

    def flippedHorz(self):
        # center = min([i.start for i in self.lines] + [i.end for i in self.lines], key=lambda l: l.x).x + (self.rect.size.width() / 2)
        center = self.rect.center()

        flippedLines = self.deepcopy(self.lines)
        for i in flippedLines:
            i.start.x -= (i.start.x - center) * 2
            i.end.x   -= (i.end.x   - center) * 2

        flippedHalfLines = self.deepcopy(self.halfLines)
        for i in flippedHalfLines:
            i.start.x -= (i.start.x - center) * 2
            i.end.x   -= (i.end.x   - center) * 2
        return Pattern(params, flippedLines, flippedHalfLines, self._dotSpread, self.rect, self._translation)

    def translateLines(self, dx, dy):
        # debug(self.lines, 'before')
        # self.lines = list(map(lambda x: x + Point(dx, dy), self.lines))
        # self.halfLines = list(map(lambda x: x + Point(dx, dy), self.halfLines))
        for line in self.lines:
            line += Point(dx, dy)
        for line in self.halfLines:
            line += Point(dx, dy)
        # debug(self.lines, 'after')
        return self

    def translatedLines(self, dx, dy, halfLines):
        rtn = []
        for line in self.lines:
            rtn.append(line + Point(dx, dy))
        if halfLines:
            for line in self.halfLines:
                rtn.append(line + Point(dx, dy))
        return rtn

    def allLines(self, halfLines=params.includeHalfsies):
        return self.lines + (self.halfLines if halfLines else [])

    def copy(self):
        return Pattern(self.lines, self.halfLines, self._dotSpread, self.rect, self._translation)

    def __json__(self, **options):
        return [
            self.lines,
            self.halfLines,
            self.dotSpread,
            [ self.rect.x(), self.rect.y(), self.rect.width(), self.rect.height() ]
        ]

    @staticmethod
    def fromJson(j):
        return Pattern([Line.fromJson(l) for l in j[0]], [Line.fromJson(l) for l in j[1]], j[2], QRectF(*j[3]), 0)

    def __str__(self):
        return f"Pattern[lines={self.lines}, halfLines={self.halfLines}]"


# p = Pattern([Line(Point(0, 0), Point(20, 20)), Line(Point(10, 15))], [], 5, QRectF(0, 0, 20, 20), Point(0, 0))
# debug(p)
# p.translateLines(300, 300)
# debug(p)
# debug(p.translated(Point(-100, -100)))
# debug(p)

'''
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
'''


"""
PAPER PANTOGRAPHS are usually printed with one or two full rows, and with partial rows for the next row line-up.

DIGITAL (computerized quilting systems): Zip file includes:
BQM, CQP, DXF, GPF, HQF, IQP, PAT, PDF, QLI, SSD, TXT, WMF and 4QB or PLT.
Some designs also include a DWG, PNG and SVG.

NOTE:
E2E (edge to edge) designs are continuous line pantograph / border / sashing designs.
P2P (point to point) are E2E designs that have the start and stop points at the outer most edges of the design. There is no interlock side to side on P2P designs, but there may be an interlock top to bottom.
B2B (border to border) are E2E designs that have the start and stop points at the outer most edges of the design, AND the design will completely fill the space top to bottom. There is no interlock side to side OR top to bottom on B2B designs.

SELF PRINT designs are intended for longarm quilters, and are set up to be printed on 8.5" x 11" paper on any home printer.

TEAR AWAY designs are intended for both domestic and longarm quilters.  Just place, quilt and Tear Away.
 """
