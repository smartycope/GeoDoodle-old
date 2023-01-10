import math
import json
import numpy as np
import os
import pickle
import sys
from copy import copy, deepcopy
from os.path import join
from typing import Any, Callable, Iterable, Optional, Union

from Cope import todo, debug, untested, confidence, flattenList
# from Transformation import Transformation

from PyQt6.QtCore import QEvent, QFile, QLine, QLineF, QRect, QRectF, Qt, QTimer
from PyQt6.QtGui import QBrush, QColor, QPainter, QPainterPath, QPen, QTransform, QPolygon, QPolygonF, QCursor, QAction
from PyQt6.QtWidgets import QFileDialog, QMainWindow, QWidget

import Pattern
from Line import Line
from Point import Point
from Singleton import Singleton as S


"""
    IMPORTANT:
    [xy1] @ [100]
            [010]
            [xy1]
        ==
    [10x]   [x]
    [01y] @ [y]
    [001]   [1]

    Holding vectors vertically is just convention!
"""


#* Cool events worth looking into:
    # QEvent.MouseTrackingChange, QEvent.Move, QEvent.Paint, QEvent.Resize, QEvent.Scroll, QEvent.Show,
    # QEvent.Shortcut, QEvent.ShortcutOverride, QEvent.StyleChange, QEvent.UpdateRequest, QEvent.Wheel,
    # QEvent.DragEnter, QEvent.DragLeave, QEvent.DragMove, QEvent.Drop, QEvent.Enter, QEvent.FileOpen,
    # QEvent.Gesture, QEvent.GrabKeyboard, QEvent.GrabMouse, QEvent.HoverEnter, QEvent.HoverLeave,
    # QEvent.HoverMove, QEvent.Leave, QEvent.MouseButtonDblClick


# transformation examples are on page 91

""" There's 2 ways I can see of doing this:
1. Keep track of the current transformation, and apply any new transformations
    immediately to all relevant points (lines, dots, bounds, etc.). Then for the
    goHome function, calculate x from self.transformation*x = identity(2), and apply
    that transformation.

2. Keep track of the current transformation, and apply it to all the relavant vectors
    when painting, keeping all of them "ideal". Then for the goHome function, it
    just sets the transformation to identity(2), and the transform function just
    applies a new transformation to self.transformation

For now, I'm doing option 1
"""
class Paper(QWidget):
    pass
class Paper(QWidget):
    from ._events import (mouseMoveEvent, keyReleaseEvent, keyPressEvent,
                          fileDropped, resizeEvent, paintEvent, mousePressEvent, mouseDoubleClickEvent, mouseReleaseEvent, wheelEvent)
    from ._dots import regenerateDots, transform, copyTransform
    from ._lines import createLine, mirrorLine, _mirrorTransforms
    from ._pattern import (_getPatternTransformations, getLinesWithinRect, _addLines, imprintLines,
                          toggleRepeat, getLinesFromPattern, destroySelection, getBoundsRect)
    from ._file import (getFile, save, saveAs, exportPNG, exportDXF, exportSVG)
    from ._misc import updateMirror, setShowLen, focusLocChanged, alignFocus, updateMouse, _getClosestDot, loopFocus
    from ._input import (scaleControl, createControl, deleteControl, deleteLine, specificErase,
        clearSelectionControl, rotateControl, selectAreaControl, deleteLine, specificErase, goHome,
        cancelControl, debugControl, moveFocus, addBound, clearAll, rotateSelectionControl,
        undo, redo, cut, copy, paste)

    # These are ints instead of an enum so we can do math with them.
    # The numbers make sense, I promise
    MIRROR_STATES = (0, 1, 2, 4) # 1 is horizontal line only

    def __init__(self, parent=None, lines=[], bounds=[]):
        self.lines = lines
        self.bounds = bounds

        super(Paper, self).__init__(parent)

        # self.setBackgroundRole(10)
        self.setAutoFillBackground(True)
        self.setMouseTracking(True)

        # mouseLoc is the 'normal' location of the cursor, focusLoc is the openGL location of the adjusted cursor.
        self.focusLoc = Point()
        # self.backgroundColor = S.settings.value('paper/default_background')
        self.dragButtons = [False] * 32

        self.currentMirrorState = 0
        self.rememberedMirrorState = self.currentMirrorState
        self.currentLine = None
        # This is a string when we've saved before
        self.saveFile = None
        self.shifted = False
        # If we're holding a pattern to be pasted, that, otherwise, None
        self.copying = None
        self.clipboard = None
        self.repeating = False
        # Gets set to None while shift is pressed, but the mouse hasn't moved yet
        self.selecting = False
        self.pureDots = []
        # We generate the dots exclusively in the _resize function, which is called as shortly after we're constructed
        # This is now a nested numpy array for speed (since in translating we were just regenerating constantly)
        self.dots = None
        # An ordered list of lists of Lines that hold the last lines to be removed due to undo
        #   Previously deleted and not drawn lines are included in this.
        #   Should have a limiter to stop it from getting too big?
        self.redoBuffer = []
        # For when we just want to delete one specific line. This is the point of the other end of the line, or None
        self.specificEraseBuffer = None
        self._uninitialized = True
        # Actions we want to be in the menuBar of the main window, organized by which group they're in
        self.actionsToAdd = {}

        # If we're not using a custom cursor, then we can only update the mouse
        # so frequently in order for it to not get stuck on dots
        # self._lastUpdatedFocus = 0
        self._updateFocusTimer = QTimer(self)
        self._updateFocusTimer.setInterval(S.settings['paper/cursor_snap_delay'])
        self._updateFocusTimer.setSingleShot(True)
        self._updateFocusTimer.timeout.connect(self.alignFocus)

        if S.settings.value('paper/use_custom_cursor'):
            self.setCursor(Qt.CursorShape.BlankCursor)
        else:
            self.setCursor(Qt.CursorShape.CrossCursor)

        self.bindActions()

        if S.debugging:
            self.lines += [
                Line(Point(0, 32), Point(16, 0)),# + Point(8, 6),
                Line(Point(16, 0), Point(0, -32)),# + Point(8, 6),
                Line(Point(0, -32), Point(-16, 0)),# + Point(8, 6),
                Line(Point(-16, 0), Point(0, 32)),# + Point(8, 6),
                Line(Point(-16, 0), Point(0, 32)),# + Point(8, 6),

                Line(Point(0, -32), Point(0, 0)),# + Point(8, 6),
                Line(Point(16, 0), Point(0, 0)),# + Point(8, 6),
            ]
            self.bounds += [
                Point(16, 32),# + Point(8, 6),
                Point(-16, -32),# + Point(8, 6),
            ]

    def init(self):
        """ Because when the constructor is called, we don't have the correct
            widget size for some reason. This is called when resize is called
            for the first time. """
        # Our current translation
        # We need to start off translating by half the window size, so the
        # origin is in the middle instead of the top left
        self.home = np.array([
            [16, 0, 0],#self.width() / 2],
            [0, 16, 0],#self.height() / 2],
            [0, 0, 1],
        ])

        self.transformation = self.home.copy()
        self.relativeTransformation = self.transformation.copy()
        self.relativeTransformation[0, 2] = self.size().width()  / 2
        self.relativeTransformation[1, 2] = self.size().height() / 2
        # The transformation to apply to the current selection (i.e. when copying)
        self._selectionTransformation = np.identity(3)
        self._selectionRotation = 0
        size = Point(self.size())
        self.centerDot = (size - (size % self.scale)) / 2
        self.regenerateDots()

    def bindActions(self):
        # The tuple is (what group the action should be in in the main window menuBar, function to bind to)
        for shortcut, f in {
            'add_single_line':  (None, lambda: self.createControl(addAnother=False)),
            'add_another_line': (None, lambda: self.createControl(addAnother=True)),
            'move_up':          (None, lambda: self.moveFocus('y', -1)),
            'jump_up':          (None, lambda: self.moveFocus('y', -S.settings['paper/dot_jump_amt'])),
            'move_down':        (None, lambda: self.moveFocus('y', 1)),
            'jump_down':        (None, lambda: self.moveFocus('y', S.settings['paper/dot_jump_amt'])),
            'move_left':        (None, lambda: self.moveFocus('x', -1)),
            'jump_left':        (None, lambda: self.moveFocus('x', -S.settings['paper/dot_jump_amt'])),
            'move_right':       (None, lambda: self.moveFocus('x', 1)),
            'jump_right':       (None, lambda: self.moveFocus('x', S.settings['paper/dot_jump_amt'])),
            'scale_up':         ('View',  lambda: self.scaleControl(+2)),
            'scale_down':       ('View',  lambda: self.scaleControl(.5)),
            'increment_mirror': ('View',  lambda: self.updateMirror(increment=1)),
            'delete':           (None, self.deleteControl),
            'rotate':           ('View',  self.rotateControl),
            # 'area_select':      self.selectAreaControl,
            'specific_erase':   (None, self.specificErase),
            'go_home':          ('View',  self.goHome),
            'cancel':           (None, self.cancelControl),
            'clear_selection':  ('Edit',  self.clearSelectionControl),
            'clear_everything': ('Edit',  self.clearAll),
            'rotate_selection': ('Edit',  self.rotateSelectionControl),
            "copy":             ('Edit',  self.copy),
            "cut":              ('Edit',  self.cut),
            "paste":            ('Edit',  self.paste),
            "undo":             ('Edit',  self.undo),
            "redo":             ('Edit',  self.redo),
            'debug':            (None, self.debugControl),
        }.items():
            group, func = f
            a = QAction(shortcut.replace('_', ' ').capitalize(), self)
            a.setShortcut(S.settings[f'controls/{shortcut}'])
            a.triggered.connect(func)
            self.addAction(a)
            if group is not None:
                if group not in self.actionsToAdd.keys():
                    self.actionsToAdd[group] = []
                self.actionsToAdd[group].append(a)

    @property
    def scale(self):
        return Point(self.transformation[0, 0], self.transformation[1, 1])
    @property
    def translation(self):
        return Point(self.transformation[0, 2], self.transformation[1, 2])

    @property
    def relativeScale(self):
        return Point(self.relativeTransformation[0, 0], self.relativeTransformation[1, 1])
    @property
    def relativeTranslation(self):
        return Point(self.relativeTransformation[0, 2], self.relativeTransformation[1, 2])

    @property
    def horzMirror(self):
        start = Point(-self.width(), self.centerDot.y)
        end   = Point( self.width(), self.centerDot.y)
        return Line(start, end, QPen(S.settings['paper/mirror_line_color']))
    @property
    def vertMirror(self):
        start = Point(self.centerDot.x, -self.height())
        end   = Point(self.centerDot.x,  self.height())
        return Line(start, end, QPen(S.settings['paper/mirror_line_color']))

    @property
    def pattern(self):
        if len(self.bounds) < 2:
            return

        rect = self.getBoundsRect()
        if not (rect.width() and rect.height()):
            return

        return Pattern.Pattern(*self.getLinesWithinRect(rect, True), rect, self.transformation)

    def serialize(self) -> str:
        return json.dumps({
            # 'pattern': self.pattern.serialize(),
            'params': {
                'xOverlap':           S.settings['pattern/xOverlap'],
                'yOverlap':           S.settings['pattern/yOverlap'],
                'skip_rows':          S.settings['pattern/skip_rows'],
                'skip_columns':       S.settings['pattern/skip_columns'],
                'skip_row_amt':       S.settings['pattern/skip_row_amt'],
                'skip_column_amt':    S.settings['pattern/skip_column_amt'],
                'flip_rows':          S.settings['pattern/flip_rows'],
                'flip_columns':       S.settings['pattern/flip_columns'],
                'flip_row_orient':    S.settings['pattern/flip_row_orient'],
                'flip_column_orient': S.settings['pattern/flip_column_orient'],
                'rotate_rows':        S.settings['pattern/rotate_rows'],
                'rotate_columns':     S.settings['pattern/rotate_columns'],
                'rotate_row_amt':     S.settings['pattern/rotate_row_amt'],
                'rotate_column_amt':  S.settings['pattern/rotate_column_amt'],
                'shear_rows':         S.settings['pattern/shear_rows'],
                'shear_columns':      S.settings['pattern/shear_columns'],
                'shear_row_dir':      S.settings['pattern/shear_row_dir'],
                'shear_column_dir':   S.settings['pattern/shear_column_dir'],
                'shear_row_amt':      S.settings['pattern/shear_row_amt'],
                'shear_column_amt':   S.settings['pattern/shear_column_amt'],
                'include_halfsies':   S.settings['pattern/include_halfsies'],
            },
            'lines': [l.serialize() for l in self.lines],
            'bounds': [b.serialize() for b in self.bounds],
        }, indent=4)

    def deserialze(self, s:str):
        s = json.loads(s)
        self.lines  = [Line.deserialize(l)  for l in s['lines']]
        self.bounds = [Point.deserialize(b) for b in s['bounds']]
        S.settings['pattern/xOverlap']           = s['params']['xOverlap']
        S.settings['pattern/yOverlap']           = s['params']['yOverlap']
        S.settings['pattern/skip_rows']          = s['params']['skip_rows']
        S.settings['pattern/skip_columns']       = s['params']['skip_columns']
        S.settings['pattern/skip_row_amt']       = s['params']['skip_row_amt']
        S.settings['pattern/skip_column_amt']    = s['params']['skip_column_amt']
        S.settings['pattern/flip_rows']          = s['params']['flip_rows']
        S.settings['pattern/flip_columns']       = s['params']['flip_columns']
        S.settings['pattern/flip_row_orient']    = s['params']['flip_row_orient']
        S.settings['pattern/flip_column_orient'] = s['params']['flip_column_orient']
        S.settings['pattern/rotate_rows']        = s['params']['rotate_rows']
        S.settings['pattern/rotate_columns']     = s['params']['rotate_columns']
        S.settings['pattern/rotate_row_amt']     = s['params']['rotate_row_amt']
        S.settings['pattern/rotate_column_amt']  = s['params']['rotate_column_amt']
        S.settings['pattern/shear_rows']         = s['params']['shear_rows']
        S.settings['pattern/shear_columns']      = s['params']['shear_columns']
        S.settings['pattern/shear_row_dir']      = s['params']['shear_row_dir']
        S.settings['pattern/shear_column_dir']   = s['params']['shear_column_dir']
        S.settings['pattern/shear_row_amt']      = s['params']['shear_row_amt']
        S.settings['pattern/shear_column_amt']   = s['params']['shear_column_amt']
        S.settings['pattern/include_halfsies']   = s['params']['include_halfsies']
        return self













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

# Don't remember what this is, but I remember it was important when I pasted it here
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
