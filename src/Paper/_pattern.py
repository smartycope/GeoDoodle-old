from Cope import todo, debug, untested, confidence, flattenList, depricated, frange
import numpy as np
from Transformation import transform2Transformation
from PyQt6.QtCore import QEvent, QFile, QLine, QLineF, QRect, QRectF, Qt
from PyQt6.QtGui import QBrush, QColor, QPainter, QPainterPath, QPen, QTransform, QPolygon, QPolygonF
from PyQt6.QtWidgets import QFileDialog, QMainWindow, QWidget
from Pattern import Pattern
from Line import Line
from Point import Point
# import math
from math import ceil, floor, sin, cos, tan, radians, sqrt
from copy import copy, deepcopy
from Singleton import Singleton as S


def getBoundsRect(self) -> QRectF:
    if len(self.bounds) < 2:
        return QRectF()
    highest = min(self.bounds, key=lambda p: p.y).y # - finagle
    lowest  = max(self.bounds, key=lambda p: p.y).y # + finagle
    left    = min(self.bounds, key=lambda p: p.x).x # - finagle
    right   = max(self.bounds, key=lambda p: p.x).x # + finagle

    return QRectF(left, highest, right - left, lowest - highest).normalized()

def getLinesWithinRect(self, bounds:QRectF, includeCurrentline=False) -> ['lines', 'halfLines']:
    lines = []
    halfLines = []
    # "inflate" the rectangle just a little so it covers off-by-one errors
    bounds = bounds.adjusted(-1, -1, 1, 1)

    # Include the current line
    for line in self.lines + ([self.currentLine] if self.currentLine is not None and includeCurrentline else []):
        # And translate back, because the bounds are translated so they can be drawn easier, but the lines aren't translated directly
        # within = line.within(bounds.transformed(self.transformation * -1))
        within = line.within(bounds)
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

def _addLines(self, pattern):
    self.patternLines += pattern.copy().allLines()

@depricated
def getLinesFromPattern(self):
    if self.pattern is None:
        return []

    self.patternLines = []

    self._repeatPatternLoop(self._addLines, self.pattern.transformed)
    # I don't know why shifting it like this is nesicarry
    return [l + (Point(self.size())/2 + (-self.pattern.rect.width()*2, 0)) for l in self.patternLines]
    # return _lines

def imprintLines(self):
    hold = S.settings.value('paper/auto_imprint_pattern')
    S.settings.setValue('paper/auto_imprint_pattern', True)
    S.settings.setValue('paper/auto_imprint_pattern', hold)

    self.lines += self.patternLines

def destroySelection(self, andBounds=True):
    # for line in self.pattern.allLines():
    lines, halfLines = self.getLinesWithinRect(self.getBoundsRect())
    for line in (lines + halfLines) if S.settings['pattern/include_halfsies'] else lines:
        self.lines.remove(line)
    if andBounds:
        self.bounds.clear()
    self.repaint()

def _getPatternTransformations(self, pattern=None):
    """ This is the main engine of the pattern repeating
        This returns a list of transformations to apply to pattern to repeat it
        everywhere
    """
    if pattern is None:
        pattern = self.pattern

    if not self.repeating or pattern is None:
        return []

    patternRelativeTransformation = self.transformation.copy()
    # Restrict the dot transformation to within the screen area, but only shift in increments of pattern.size
    # Then also shift to the middle, to make it the origin
    patternRelativeTransformation[0, 2] = ((patternRelativeTransformation[0, 2] % (patternRelativeTransformation[0, 0] * pattern.size.width())) ) + (self.size().width()  / 2)
    patternRelativeTransformation[1, 2] = ((patternRelativeTransformation[1, 2] % (patternRelativeTransformation[1, 1] * pattern.size.height()))) + (self.size().height() / 2)

    amt = Point(S.settings['pattern/skip_row_amt'], S.settings['pattern/skip_column_amt'])
    # The dimentions of the pattern
    size = Point(pattern.size)

    # The size of the area we want to cover, in "pure" cooridinates
    # I thought we could just transform it, but that didn't work.
    translation = Point(self.transformation[0, 0], self.transformation[1, 1])
    area = Point(self.size()) / translation
    # Not quite sure why this is here, but it almost makes sense
    area /= 2
    # Because the pattern draws from the top left. We want to talk about it from the center
    area -= size / 2
    if S.debugging and False:
        area /= 2

    # The amount we need to offset the start by to have the pattern line up with the
    # already selected pattern
    offset = Point(self.getBoundsRect()) / translation
    #* offset %= size
    # How much space we add between each pattern
    overlap = Point(S.settings['pattern/xOverlap'], S.settings['pattern/yOverlap'])
    # How much we need to translate to draw the next pattern
    shift = size + overlap

    # debug(pattern, 'pattern')
    # debug(area, 'area', clr=2)
    # debug(size, 'size')
    # debug(overlap, 'overlap')
    # debug(shift, 'shift')
    # debug(fit, 'fit')
    # debug(offset, 'offset')
    # debug(S.settings['pattern/flip_row_orient'], 'row orient')
    # debug(S.settings['pattern/flip_column_orient'], 'col orient')

    transformations = []
    # We start at -area, because area is a positive number, and the center should
    # be the origin, not the top-left
    # The +/- are to make sure it draws just outside of the area
    for r, x in enumerate(frange(-area.x, area.x, shift.x)):
        for c, y in enumerate(frange(-area.y, area.y, shift.y)):
            t = np.array([
                [1, 0, x],
                [0, 1, y],
                [0, 0, 1],
            ])

            '''
            if not r % S.settings['pattern/rotate_rows']:
                amt = radians(S.settings['pattern/rotate_row_amt'])
                sin_, cos_ = sin(amt), cos(amt)
                # debug(sin_, 'sin', clr=2)
                # debug(cos_, 'cos')
                translation = Point(t[0, 2], t[1, 2])
                shift = translation #+ (size / 2)
                # debug(shift, 'shift', clr=2)
                # t = t @ np.array([
                #     [1, 0, -shift.x - (size.x/2)],
                #     [0, 1, -shift.y - (size.y/2)],
                #     [0, 0, 1],
                # ])
                # hyp = sqrt(size.width**2 + size.height**2) / 2
                # hyp = size / 2
                # R = hyp
                # R = Point(hyp.x-t[0, 2], hyp.y-t[1, 2])
                t = t @ np.array([
                    [ cos_, sin_, 0],
                    # [ cos_, sin_, shift.x*(1-cos_) + shift.y*sin_],
                    [-sin_, cos_, 0],
                    # [-sin_, cos_, shift.y*(1-cos_) - shift.x*sin_],
                    [0, 0, 1],
                ])
                # t = t @ np.array([
                #     [1, 0, shift.x + shift.x],
                #     [0, 1, shift.y + shift.y],
                #     [0, 0, 1],
                # ])
            if not c % S.settings['pattern/rotate_columns']:
                amt = radians(S.settings['pattern/rotate_column_amt'])
                sin_, cos_ = sin(amt), cos(amt)
                t = t @ np.array([
                    [cos_, sin_, 0],
                    [-sin_, cos_, 0],
                    [0, 0, 1],
                ])
            '''
            if not r % S.settings['pattern/flip_rows']:
                if S.settings['pattern/flip_row_orient'] == S.VERT:
                    t = t @ np.array([
                        [1, 0, 0],
                        [0, -1, -size.x + 1],
                        [0, 0, 1],
                    ])
                elif S.settings['pattern/flip_row_orient'] == S.HORZ:
                    t = t @ np.array([
                        [-1, 0, -size.y - 1],
                        [0, 1, 0],
                        [0, 0, 1],
                    ])
            if not c % S.settings['pattern/flip_columns']:
                if S.settings['pattern/flip_column_orient'] == S.VERT:
                    t = t @ np.array([
                        [1, 0, 0],
                        [0, -1, -size.x + 1],
                        [0, 0, 1],
                    ])
                elif S.settings['pattern/flip_column_orient'] == S.HORZ:
                    t = t @ np.array([
                        [-1, 0, -size.y - 1],
                        [0, 1, 0],
                        [0, 0, 1],
                    ])
            if not r % S.settings['pattern/skip_rows']:
                t = t @ np.array([
                    [1, 0, S.settings['pattern/skip_row_amt']],
                    [0, 1, 0],
                    [0, 0, 1],
                ])
            if not c % S.settings['pattern/skip_columns']:
                t = t @ np.array([
                    [1, 0, 0],
                    [0, 1, S.settings['pattern/skip_column_amt']],
                    [0, 0, 1],
                ])
            if not r % S.settings['pattern/shear_rows']:
                amt = radians(S.settings['pattern/shear_row_amt'])
                # x = 0, y = 1
                if not S.settings['pattern/shear_row_dir']:
                    t = t @ np.array([
                        [1, tan(amt), 0],
                        [0, 1, 0],
                        [0, 0, 1],
                    ])
                else:
                    t = t @ np.array([
                        [1, 0, 0],
                        [tan(amt), 1, 0],
                        [0, 0, 1],
                    ])
            if not c % S.settings['pattern/shear_columns']:
                amt = radians(S.settings['pattern/shear_column_amt'])
                # x = 0, y = 1
                if not S.settings['pattern/shear_column_dir']:
                    t = t @ np.array([
                        [1, tan(amt), 0],
                        [0, 1, 0],
                        [0, 0, 1],
                    ])
                else:
                    t = t @ np.array([
                        [1, 0, 0],
                        [tan(amt), 1, 0],
                        [0, 0, 1],
                    ])

            transformations.append(patternRelativeTransformation @ t)
    return transformations














    """
    for y in range(math.ceil(fit.y)):
        for x in range(math.ceil(fit.x)):
            todo('flipping goes somewhere in here?')
            if not downShift:
                if not x % skip.x:
                    shiftAmt = amt.x * scale + size.x
                else:
                    shiftAmt = size.x
                # current = translate(shiftAmt + (overlap.x * scale), 0, current)
                current = translate(shiftAmt.x + (overlap.x * scale.x), 0, current)
                # current = translate(shiftAmt, 0, current)
            else:
                if not y % skip.y:
                    shiftAmt = amt.y * scale + size.y
                else:
                    shiftAmt = size.y
                # current = translate(-xAtEndOfRow, shiftAmt, current)
                # current = translate(start.x - current.x - size.x, shiftAmt + (overlap.y * scale), current)
                current = translate(start.x - current.x - size.x, shiftAmt.y + (overlap.y * scale.y), current)
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
    """
