import math
import os
import pickle
import sys
from copy import copy, deepcopy
from os.path import join
from typing import Any, Callable, Iterable, Optional, Union

from Cope import todo, debug, untested, confidence, flattenList

from PyQt5.QtCore import QEvent, QFile, QLine, QLineF, QRect, QRectF, Qt
from PyQt5.QtGui import QBrush, QColor, QPainter, QPainterPath, QPen, QTransform, QPolygon, QPolygonF, QCursor
from PyQt5.QtWidgets import QFileDialog, QMainWindow, QWidget

import Pattern
from Line import Line
from Point import Point, Pair

todo('undo undos too many/too few lines after mirror is changed', False)
# -- maybe use indecies instead of a buffer?

todo('add the ability to add text like in LTSpice')
todo('bind ctrl+y to redo')

todo('zooming')
todo('flipping')
todo('add different dot formations')
todo('filling spaces')
todo('repeating only across a specific axis')
todo('add mouse middle click dragging do translation')
todo('Allow the focus go offscreen properly')
todo('add curves')
todo('AUTO_IMPRINT_PATTERN doesnt quite work yet, and the pattern colors dont work either')

todo('consider making mirror use patterns instead of hand mirroring all the lines')
todo('add a rotation option to Pattern.params')
# todo('add a seperate shortcut to just delete the selected area and not copy it')
todo('the toolbar (file, edit, view thing bar) is grabbing focus I think')
todo('mirroring has an off-by-one error somewhere that makes it so you cant touch those lines')
todo('make shift when not being dragged toggle the current bound')
todo('holding shift while moving with the arrow keys works, but doesnt let go until one move after you let go of shift')
todo('change clipboard to use the actual clipboard via JSON')
todo('if you hold down a number key, it triggers to change the color of that button')
todo('add some sort of shortcuts to bring up the basic lines and/or basic chords')
todo('just go through and play with it and fix or note any bugs that come up')
todo('saving broke')
todo('adding a preferences menu')
todo('add an option to make clearAll reset the mirror or not')
todo('figure out how to get the docks to work on the side')
todo('a custom line editor (for custom pens)')
todo('grabbing pattern isnt working right, possibly something to do with mirroring')
todo('space and c stop working at random points, until you click the pattern, not sure why, something grabbing focus maybe?')

#* Cool events worth looking into:
    # QEvent.MouseTrackingChange, QEvent.Move, QEvent.Paint, QEvent.Resize, QEvent.Scroll, QEvent.Show,
    # QEvent.Shortcut, QEvent.ShortcutOverride, QEvent.StyleChange, QEvent.UpdateRequest, QEvent.Wheel,
    # QEvent.DragEnter, QEvent.DragLeave, QEvent.DragMove, QEvent.Drop, QEvent.Enter, QEvent.FileOpen,
    # QEvent.Gesture, QEvent.GrabKeyboard, QEvent.GrabMouse, QEvent.HoverEnter, QEvent.HoverLeave,
    # QEvent.HoverMove, QEvent.Leave, QEvent.MouseButtonDblClick


class Paper(QWidget):
    from ._events import (updateFocus, updateMouse, eventFilter, keyPressed, keyReleased,
                         fileDropped, resizeEvent, paintEvent)
    from ._dots import regenerateDots, translate, goHome
    from ._lines import createLine, mirrorLine, deleteLine, specificErase
    from ._pattern import (updatePattern, _repeatPatternLoop, getLinesWithinRect, _addLines, imprintLines,
                          toggleRepeat, getLinesFromPattern, destroySelection, addBound, getBoundsRect)
    from ._shortcuts import undo, redo, cut, copy, paste
    from ._file import (save, saveAs, open, exportPNG, exportDXF, exportSVG, exportJSON, importJSON)
    from ._misc import updateMirror, clearAll, updateSettings, setShowLen, moveFocus

    dotSpread = 16
    dotSize = 1 # Currently unused
    dragDelay = 7 # Currently unused
    antialiased = True

    EXPORT_LINE_THICKNESS = 2
    BOUNDS_SIZE = 4
    MIRROR_LINE_COLOR = QColor(31, 43, 58)
    FOCUS_SIZE = 5
    DEFAULT_BACKGROUND = QColor(200, 160, 100)

    savePath   = "~/.GeoDoodle/saves/" # Currently unused
    exportPath = "~/.GeoDoodle/images/" # Currently unused
    loadDir    = savePath # Currently unused

    MIRROR_STATES = (0, 1, 2, 4) # 1 is horizontal line only

    # Smooth translation is slower, because it has to regenerate or move all the dots every time, and
    #   it has to handle every scroll event instead of collecting them and then translating everyhting
    SMOOTH_TRANSLATION = True

    # Just kidding, don't use this, it's conceptually impossible, you'll see why.
    USE_CUSTOM_CURSOR = True

    AUTO_IMPRINT_PATTERN = True
    ESC_QUITS = True

    def __init__(self, parent=None):
        super(Paper, self).__init__(parent)

        # self.setBackgroundRole(10)
        self.setAutoFillBackground(True)

        # mouseLoc is the 'normal' location of the cursor, focusLoc is the openGL location of the adjusted cursor.
        self.focusLoc = Point(0, 0) # GLPoint(self.width, self.height-1, -1)
        self.mouseLoc = Point(0, 0) # TLPoint(0, 0)
        self.backgroundColor = self.DEFAULT_BACKGROUND
        self.dragButtons = [False] * 32

        self.lines = [
            Line(Point(310.0, 214.0), Point(294.0, 246.0)) - Point(6, 6),
            Line(Point(294.0, 246.0), Point(310.0, 278.0)) - Point(6, 6),
            Line(Point(310.0, 278.0), Point(326.0, 246.0)) - Point(6, 6),
            Line(Point(326.0, 246.0), Point(310.0, 214.0)) - Point(6, 6),
        ]

        self.patternLines = []

        self.setMouseTracking(True)
        self.installEventFilter(self)

        # currentLineColor = (150, 44, 44)
        # If we're holding a pattern to be pasted, that, otherwise, None
        self.copying = None
        self.clipboard = None
        self.repeating = False
        self.pattern = None
        # Gets set to None while shift is pressed, but the mouse hasn't moved yet
        self.selecting = False

        self.mirrorLines = []
        self.currentMirrorState = 0
        self.rememberedMirrorState = self.currentMirrorState
        self.bounds = [
            Pair(288.0, 208.0),
            Pair(320.0, 272.0)
        ]
        self.currentLine = None

        self.vertPattern = None
        self.horzPattern = None
        self.fullFlippedPattern = None

        if not self.USE_CUSTOM_CURSOR:
            self.setCursor(QCursor(Qt.CursorShape.CrossCursor))

        # For when not using smooth translation
        self.translationBuffer = 0

        # Our current translation
        self.translation = Point(0, 0)

        # An ordered list of lists of Lines that hold the last lines to be removed due to undo
        #   Previously deleted and not drawn lines are included in this.
        #   Should have a limiter to stop it from getting too big?
        self.redoBuffer = []

        # For when we just want to delete one specific line. This is the point of the other end of the line, or None
        self.specificEraseBuffer = None

        # We generate the dots exclusively in the _resize function, which is called as shortly after we're constructed
        # This is now a nested numpy array for speed (since in translating we were just regenerating constantly)
        self.dots = None

        self.currentPen      = QPen(QColor(0, 0, 0))
        self.dotPen          = QPen(QColor(0, 0, 0))
        self.focusPen        = QPen(QColor(37, 37, 37))
        self.boundsPen       = QPen(QColor(30, 30, 30))
        self.boundsLinePen   = QPen(QColor(32, 45, 57))
        self.mirrorLinePen   = self.boundsLinePen
        self.activeCopyPen   = QPen(QColor(30, 30, 30))
        self.backgroundBrush = QBrush(self.DEFAULT_BACKGROUND)
        # boundsBrush = QBrush(DEFAULT_BACKGROUND) # Currently unimplemented
