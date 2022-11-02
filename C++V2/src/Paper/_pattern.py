from Cope import todo, debug, untested, confidence, flattenList
from PyQt5.QtCore import QEvent, QFile, QLine, QLineF, QRect, QRectF, Qt
from PyQt5.QtGui import QBrush, QColor, QPainter, QPainterPath, QPen, QTransform, QPolygon, QPolygonF
from PyQt5.QtWidgets import QFileDialog, QMainWindow, QWidget
import Pattern
from Line import Line
from Point import Point, Pair
import math
from copy import copy, deepcopy


def getBoundsRect(self) -> QRectF:
    if len(self.bounds) < 2:
        return QRectF()
    highest = min(self.bounds, key=lambda p: p.y).y # - finagle
    lowest  = max(self.bounds, key=lambda p: p.y).y # + finagle
    left    = min(self.bounds, key=lambda p: p.x).x # - finagle
    right   = max(self.bounds, key=lambda p: p.x).x # + finagle

    return QRectF(left, highest, right - left, lowest - highest).normalized()

def updatePattern(self):
    self.repaint()
    if len(self.bounds) < 2:
        self.pattern = None
        return

    rect = self.getBoundsRect()
    if not (rect.width() and rect.height()):
        self.pattern = None
        return

    # If you're optimizing this later, don't forget to regenerate the pattern here
    self.pattern = Pattern.Pattern(*self.getLinesWithinRect(rect, True), self.dotSpread, rect, self.translation)

    # Generate the flipped patterns, if applicable
    if Pattern.params.flipRowOrient == 'Vertically' or Pattern.params.flipColumnOrient == 'Vertically':
        self.vertPattern = self.pattern.flippedVert()
    if Pattern.params.flipRowOrient == 'Horizontally' or Pattern.params.flipColumnOrient == 'Horizontally':
        self.horzPattern = self.pattern.flippedHorz()
    if (Pattern.params.flipRowOrient == 'Vertically' or Pattern.params.flipColumnOrient == 'Vertically') and \
        (Pattern.params.flipRowOrient == 'Horizontally' or Pattern.params.flipColumnOrient == 'Horizontally'):
        self.fullFlippedPattern = self.horzPattern.flippedVert()

    if self.AUTO_IMPRINT_PATTERN:
        self.getLinesFromPattern()

def getLinesWithinRect(self, bounds:QRectF, includeCurrentline=False) -> ['lines', 'halfLines']:
    lines = []
    halfLines = []

    # Include the current line
    # for line in self.lines:
    for line in self.lines + ([self.currentLine] if self.currentLine is not None and includeCurrentline else []):
        # "inflate" the rectangle just a little so it covers off-by-one errors
        # .adjusted(-1, -1, 1, 1)
        # And translate back, because the bounds are translated so they can be drawn easier, but the lines aren't translated directly
        within = line.within(bounds.translated(self.translation * -1))
        if within:
            lines.append(line)
        elif within is not None:
            halfLines.append(line)

    return lines, halfLines

def toggleRepeat(self):
    self.repeating = not self.repeating
    if self.repeating:
        self.rememberedMirrorState = self.currentMirrorState
        self.updateMirror(setIndex=0)
    else:
        self.updateMirror(setIndex=self.rememberedMirrorState)
    self.updatePattern()

# Because scopes are inconsistent
# _lines = []
def _addLines(self, pattern):
    self.patternLines += pattern.copy().allLines()

def getLinesFromPattern(self):
    # global _lines
    if self.pattern is None:
        return []

    self.patternLines = []

    # _lines = []
    # def addLines(pattern):
    #     global _lines
    #     _lines += debug(pattern.allLines())

    self._repeatPatternLoop(self._addLines, self.pattern.translateLines)
    # I don't know why shifting it like this is nesicarry
    return [l + (Pair(self.size())/2 + (-self.pattern.rect.width()*2, 0)) for l in self.patternLines]
    # return _lines

def imprintLines(self):
    hold = self.AUTO_IMPRINT_PATTERN
    self.AUTO_IMPRINT_PATTERN = True
    self.updatePattern()
    self.AUTO_IMPRINT_PATTERN = hold

    self.lines += self.patternLines

def destroySelection(self, andBounds=True):
    lines, halfLines = self.getLinesWithinRect(self.getBoundsRect())
    for line in lines + halfLines if Pattern.params.includeHalfsies else lines:
        self.lines.remove(line)
    if andBounds:
        self.bounds.clear()
    self.updatePattern()

def addBound(self, remove=True):
    # If there's already a bound there, just remove it instead
    # If selecting is None, then do add it, becuase it'll move around
    # if self.focusLoc in self.bounds and self.selecting is not None:
    if remove:
        while self.focusLoc in self.bounds:
            debug('removing bound')
            # self.bounds.remove(self.focusLoc + self.translation)
            self.bounds.remove(self.focusLoc)
    else:
        # self.bounds.append(self.focusLoc.copy() + self.translation)
        self.bounds.append(self.focusLoc.copy())

    # if self.repeating:
    self.updatePattern()

def _repeatPatternLoop(self, drawFunc:'func(Pattern)', translateFunc:'func(dx, dy)'):
    """ This is the main engine of the pattern repeating
        drawFunc is given a Pattern parameter, and is called whenever a pattern needs to be placed
        translateFunc takes dx and dy parameters, and is called whenever we need to translate the pattern
        This is useful so that we don't have to rewrite this whole function for getting lines from a pattern.
    """
    if self.repeating and self.pattern:
        DEBUG = False
        # The size of the area we want to cover
        area = Pair(self.size())
        if DEBUG:
            area /= 4
        # The dimentions of the pattern
        size = Pair(self.pattern.rect.size())
        patternStart = Point(self.pattern.rect.topLeft())
        # Every <skip> rows/columns, we add <amt> spaces
        skip = Pair(Pattern.params.skipRows, Pattern.params.skipColumns)
        amt  = Pair(Pattern.params.skipRowAmt, Pattern.params.skipColumnAmt)
        flip = Pair(Pattern.params.flipRows, Pattern.params.flipColumns)
        # How much space we add between each pattern
        overlap = Pair(Pattern.params.xOverlap, Pattern.params.yOverlap)
        # Keeps track of the current translations
        current = Pair(0, 0)

        # Draw outside a little so it looks good
        area += size*2
        # Don't know why this is here
        area.y += self.dotSpread

        # How much we need to translate to draw the next pattern
        shift = size + (overlap * self.dotSpread)

        # This fixes the bug where if overlap is too small it doesn't draw enough patterns
        # fit.x -= overlap.x if overlap.x < 0 else 0
        # fit.y -= overlap.y if overlap.y < 0 else 0

        # We don't want to actually start from the translation, we just want to offset it enough so that it looks like we did
        translationOffset = self.translation % shift
        # Because the we want to align the overarching pattern with the selected pattern
        currentPatternPosOffset = patternStart % shift
        # So that when we change overlap, it still lines up with the selected pattern
        # I don't know why -size*2 is here.
        # overlapOffset = ((patternStart // shift) * self.dotSpread) - shift*2
        # debug(overlapOffset)
        overlapOffset = ((patternStart // size) * overlap * self.dotSpread) - size*2
        debug(overlapOffset)
        # Where we start drawing the overarching pattern from
        start = -size + translationOffset + currentPatternPosOffset# - overlapOffset

        # Don't know why this needs set to True to start, but it makes it work, so don't question it.
        downShift = True
        start.y -= size.y * 2

        # How many patterns will fit in the area
        fit = (area - start) / shift

        if DEBUG:
            start += Pair(self.size()) / 2
            # Draw a debugging box to show the simulated area
            debugBox = QPainterPath()
            debugBox.addRect(*start.data(), *area.data())
            drawFunc(debugBox)
            # drawFunc = lambda p: drawFunc(p.scale)

        def translate(x, y, current):
            translateFunc(x, y)
            return current + (x, y)

        # This just moves where we're drawing the pattern
        current = translate(start.x, start.y, current)
        # translate() compounds on itself, that's why this is weird.
        for y in range(math.ceil(fit.y)):
            for x in range(math.ceil(fit.x)):
                todo('flipping goes somewhere in here?')
                if not downShift:
                    if not x % skip.x:
                        shiftAmt = amt.x * self.dotSpread + size.x
                    else:
                        shiftAmt = size.x
                    current = translate(shiftAmt + (overlap.x * self.dotSpread), 0, current)
                    # current = translate(shiftAmt, 0, current)
                else:
                    if not y % skip.y:
                        shiftAmt = amt.y * self.dotSpread + size.y
                    else:
                        shiftAmt = size.y
                    # current = translate(-xAtEndOfRow, shiftAmt, current)
                    current = translate(start.x - current.x - size.x, shiftAmt + (overlap.y * self.dotSpread), current)
                    # current = translate(start.x - current.x - size.x, shiftAmt, current)

                drawFunc(self.pattern)

                downShift = False
                # If we're outside of the pattern, don't draw anymore
                #   Really, these are just for optimization. There's a couple bugs here,
                #   but they don't really matter that much, QPainterPath is pretty fast.
                # if current.x > area.x - size.x:
                if current.x > area.x + start.x - size.x:
                    break

            downShift = True
            # if current.y > area.y - size.y:
            if current.y > area.y + start.y - size.y:
                break
