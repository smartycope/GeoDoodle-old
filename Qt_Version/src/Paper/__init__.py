import math
import os
import pickle
import sys
from copy import copy, deepcopy
from os.path import join
from typing import Any, Callable, Iterable, Optional, Union

from Cope import todo, debug, untested, confidence, flattenList

from PyQt6.QtCore import QEvent, QFile, QLine, QLineF, QRect, QRectF, Qt
from PyQt6.QtGui import QBrush, QColor, QPainter, QPainterPath, QPen, QTransform, QPolygon, QPolygonF, QCursor
from PyQt6.QtWidgets import QFileDialog, QMainWindow, QWidget

import Pattern
from Line import Line
from Point import Pair
from Singleton import Singleton as S

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

    # These are ints instead of an enum so we can do math with them.
    # The numbers make sense, I promise
    MIRROR_STATES = (0, 1, 2, 4) # 1 is horizontal line only


    def __init__(self, parent=None):
        super(Paper, self).__init__(parent)

        # self.setBackgroundRole(10)
        self.setAutoFillBackground(True)

        # mouseLoc is the 'normal' location of the cursor, focusLoc is the openGL location of the adjusted cursor.
        self.focusLoc = Pair(0, 0) # GLPair(self.width, self.height-1, -1)
        self.mouseLoc = Pair(0, 0) # TLPair(0, 0)
        self.backgroundColor = S.settings.value('paper/default_background')
        self.dragButtons = [False] * 32

        self.lines = [
            Line(Pair(310.0, 214.0), Pair(294.0, 246.0)) - Pair(6, 6),
            Line(Pair(294.0, 246.0), Pair(310.0, 278.0)) - Pair(6, 6),
            Line(Pair(310.0, 278.0), Pair(326.0, 246.0)) - Pair(6, 6),
            Line(Pair(326.0, 246.0), Pair(310.0, 214.0)) - Pair(6, 6),
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

        if not S.settings.value('paper/use_custom_cursor'):
            self.setCursor(QCursor(Qt.CursorShape.CrossCursor))

        # For when not using smooth translation
        self.translationBuffer = 0

        # Our current translation
        self.translation = Pair(0, 0)

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
        self.backgroundBrush = QBrush(S.settings.value('paper/default_background'))
        # boundsBrush = QBrush(DEFAULT_BACKGROUND) # Currently unimplemented
