from Cope import todo, debug, untested, confidence, flattenList
# from Transformation import Transformation
import numpy as np
from PyQt6.QtCore import QEvent, QFile, QLine, QLineF, QRect, QRectF, Qt, QTimer, QPointF, QPoint, QSize, QSizeF
from PyQt6.QtGui import QBrush, QColor, QPainter, QPainterPath, QPen, QTransform, QPolygon, QPolygonF
from PyQt6.QtWidgets import QFileDialog, QMainWindow, QWidget, QApplication
import Pattern
from Line import Line
from Point import Point
from time import time as now

from Singleton import Singleton as S

def mouseMoveEvent(self, event):
    self.updateMouse(event)
    self.dragButtons[event.buttons().value] = True
    if self.selecting is None:
        self.selecting = True
    # if self.currentLine is not None and self.repeating and self.pattern is not None:
        # self.reloadPattern()
    else:
        if S.settings['paper/use_custom_cursor']:
            self.repaint()

def mousePressEvent(self, event):
    if event.buttons() == Qt.MouseButton.LeftButton:
        self.createControl(addAnother=False)
    elif event.buttons() == Qt.MouseButton.RightButton:
        self.createControl(addAnother=True)
    elif event.buttons() == Qt.MouseButton.MiddleButton:
        self.deleteControl()

def mouseDoubleClickEvent(self, event):
    if event.buttons() == Qt.MouseButton.LeftButton or event.buttons() == Qt.MouseButton.RightButton:
        if self.copying is not None:
            self.paste(True)
        else:
            self.createLine(True)

def mouseReleaseEvent(self, event):
    if self.dragButtons[event.button().value] and self.copying is None:
        self.dragButtons[event.button().value] = False
        if event.button() & (Qt.MouseButton.RightButton | Qt.MouseButton.LeftButton):
            self.createLine(linkAnother=event.button().value == Qt.MouseButton.RightButton)

def wheelEvent(self, event):
    self.transform(np.array([
        [1, 0, round(event.angleDelta().x() / S.settings['scroll_sensitivity'])],
        [0, 1, round(event.angleDelta().y() / S.settings['scroll_sensitivity'])],
        [0, 0, 1],
    ]))

def keyPressEvent(self, event):
    # Because shift is a keyboard modifier, it can't trigger a QAction by itself
    if event.key() == Qt.Key.Key_Shift:
        self.selectAreaControl()

def keyReleaseEvent(self, event):
    # No idea why capslock here is necissary, maybe it's my own personal hacked together keyboard configuration?
    if event.key() == Qt.Key.Key_Shift or event.key() == Qt.Key.Key_CapsLock:
        if self.selecting:
            self.addBound(False)
        self.selecting = False

@untested
def fileDropped(self, event):
    todo('file dropped event')

def resizeEvent(self, event):
    if self._uninitialized:
        self.init()
        self._uninitialized = False
        return
    # I'm honestly not sure why this works?...
    self.transform(np.identity(3), regenerate=True, resizing=True)

def paintEvent(self, event):
    # Because apparently this gets called at the same time resizeEvent does?
    if self._uninitialized:
        return

    painter = QPainter(self)
    if (S.settings['paper/antialiased']):
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

    #* Now it's all set up, do all the painting stuff -- in order
    # Draw the background
    painter.setBrush(S.settings['paper/background_color'])
    painter.drawRect(self.rect())

    # Draw the debugging half size area square under everything
    if S.debugging and self.repeating:
        painter.drawRect(QRect(Point(self.size() / 4).toPoint(), self.size() / 2))

    # Draw the bounds
    for bound in self.bounds:
        painter.setPen(QPen(S.settings['paper/bounds_color']))
        s = S.settings['paper/bounds_size']
        # Draw rounded squares in we're including halfsies, otherwise draw circles
        if S.settings['pattern/include_halfsies']:
            painter.drawRoundedRect(QRectF(*(bound - s).data(), s*2, s*2), 1, 1)
        else:
            painter.drawEllipse(bound.copy(), s, s)

    S.settings.beginGroup('paper')

    # Draw the bounds box
    painter.setPen(S.settings['bounds_line_pen'])
    painter.setBrush(QBrush(S.settings['selection_color']))
    painter.drawRect(self.getBoundsRect())
    #* painter.setBrush(self.backgroundBrush)

    # Draw the dots
    for dot in self.dots.T.astype(int):
        painter.drawPoint(dot[0], dot[1])

    # Draw the pattern
    for trans in self._getPatternTransformations():
        painter.drawPath(self.pattern.transformed(trans))

    # Draw the regular lines
    # We can't do this because they potentially all have different pens
    # painter.drawLines(self.lines)
    for line in self.lines:
        painter.setPen(line.pen)
        painter.drawLine(line)

    # Draw the mirrorLines
    painter.setPen(S.settings['mirror_line_pen'])
    if self.MIRROR_STATES[self.currentMirrorState] in [1, 4]:
        # painter.drawLine(self.horzMirror.transformed(self.relativeTransformation))
        painter.drawLine(self.horzMirror)
    if self.MIRROR_STATES[self.currentMirrorState] >= 2:
        # painter.drawLine(self.vertMirror.transformed(self.relativeTransformation))
        painter.drawLine(self.vertMirror)

    # Draw the current line
    if self.currentLine is not None:
        painter.setPen(S.settings['current_pen'])
        for line in self.mirrorLine(self.currentLine):
            painter.drawLine(line)

    # Draw the pattern we're copying, if we are
    if self.copying is not None:
        painter.setPen(S.settings['active_copy_pen'])
        painter.drawPath(self.copying.transformed(self.copyTransform()))

    # Draw the focus
    if self.focusLoc and S.settings['use_custom_cursor']:
        painter.setPen(QPen(S.settings['focus_color']))
        focusSize = S.settings['focus_size']
        painter.drawLines([Line(self.focusLoc + (0, focusSize), self.focusLoc + (0, -focusSize)),
                           Line(self.focusLoc + (focusSize, 0), self.focusLoc + (-focusSize, 0))])

    if S.debugging:
        # Draw the transformation matrix in the top-right for debugging
        painter.drawText(
            QRectF(self.size().width() - 100, 5, 150, 150),
            np.array2string(self.transformation, precision=1, suppress_small=True, floatmode='maxprec')
        )

        painter.drawText(
            QRectF(self.size().width() - 125, 165, 150, 150),
            np.array2string(self.relativeTransformation, precision=1, suppress_small=True, floatmode='maxprec')
        )

        if self.pattern is not None:
            properPattern = self.pattern.transformed(np.array([
                [16, 0,  self.size().width() - 50],#self.relativeTransformation[0, 2]],
                [0,  16, self.size().height()- 100],#self.relativeTransformation[1, 2]],
                [0,  0,  1 ]
            ]))

            # Displays the place where the pattern *should* be
            size = round(Point(self.pattern.size) * 16)
            painter.drawRect(QRect(
                (Point(self.size()) - (50, 100)).toPoint(),
                QSize(size.width, size.height)))

            # Displays the current pattern in the bottom right ish
            painter.drawPath(properPattern)

        # Display the origin as a different color
        painter.setPen(QPen(QColor('blue')))
        painter.drawEllipse(Point(self.size())/2, 1, 1)

        # And where relativeTransform is pointing
        painter.setPen(QPen(QColor('red')))
        painter.drawEllipse(Point(self.relativeTransformation[0, 2], self.relativeTransformation[1, 2]), 1, 1)

        # And the center dot
        painter.setPen(QPen(QColor('green')))
        painter.drawEllipse(self.centerDot, 2, 2)

    S.settings.endGroup()
    painter.end()
