from Cope import todo, debug, untested, confidence, flattenList
from PyQt6.QtCore import QEvent, QFile, QLine, QLineF, QRect, QRectF, Qt
from PyQt6.QtGui import QBrush, QColor, QPainter, QPainterPath, QPen, QTransform, QPolygon, QPolygonF
from PyQt6.QtWidgets import QFileDialog, QMainWindow, QWidget
import Pattern
from Line import Line
from Point import Pair

from Singleton import Singleton as S

def updateFocus(self):
    self.focusLoc = Pair(min(self.dots, key=lambda p:abs(p[0] - self.mouseLoc.x))[0],
                            min(self.dots, key=lambda p:abs(p[1] - self.mouseLoc.y))[1])
    # I think we have to check bounds here because I think this is called before keyReleased() is
    if self.selecting and len(self.bounds):
        self.bounds[-1] = self.focusLoc

    if not S.settings.value('paper/use_custom_cursor'):
        # if self.window().rect().contains(self.focusLoc.toPoint(), proper=True):
        self.cursor().setPos(self.mapToGlobal(self.focusLoc.copy().toPoint()))

    # if self.AUTO_IMPRINT_PATTERN:
        # self.updatePattern()

def updateMouse(self, event):
    self.mouseLoc = Pair(event.pos())
    self.updateFocus()
    # This is now done in the draw function itself
    if self.currentLine is not None:
        self.currentLine.end = self.focusLoc.copy()

def eventFilter(self, target, event):
    if target == self:
        if event.type() in (QEvent.Type.MouseMove, QEvent.Type.DragMove, QEvent.Type.HoverMove):
            self.updateMouse(event)
            self.dragButtons[event.buttons().value] = True
            if self.selecting is None:
                self.selecting = True
            if self.currentLine is not None and self.repeating and self.pattern is not None:
                self.updatePattern()
            else:
                self.repaint()

        elif event.type() == QEvent.Type.MouseButtonPress:
            if event.buttons() == Qt.MouseButton.LeftButton:
                if self.copying is not None:
                    self.paste(False)
                else:
                    self.createLine()

            elif event.buttons() == Qt.MouseButton.RightButton:
                if self.copying is not None:
                    self.paste(True)
                else:
                    self.createLine(True)

            elif event.buttons() == Qt.MouseButton.MiddleButton:
                if self.copying is not None:
                    self.copying = None
                    self.repaint()
                else:
                    self.deleteLine()

        elif event.type() == QEvent.Type.MouseButtonRelease:
            if self.dragButtons[event.button().value]:
                self.dragButtons[event.button().value] = False
                if event.button() & (Qt.MouseButton.RightButton | Qt.MouseButton.LeftButton):
                    self.createLine(linkAnother=event.button().value == Qt.MouseButton.RightButton)

        elif event.type() == QEvent.Type.MouseButtonDblClick:
            if event.buttons() == Qt.MouseButton.LeftButton or event.buttons() == Qt.MouseButton.RightButton:
                if self.copying is not None:
                    self.paste(True)
                else:
                    self.createLine(True)

        elif event.type() == QEvent.Type.Wheel:
            # The amount the wheel moved, in 1/8ths of a degree
            self.translate(Pair(event.angleDelta()))

    return super(QWidget, self).eventFilter(target, event)

def keyPressed(self, event):
    if   event.key() == Qt.Key.Key_Up or event.key() == Qt.Key.Key_W:
        self.moveFocus('y', -1)

    elif event.key() == Qt.Key.Key_Down or event.key() == Qt.Key.Key_S:
        self.moveFocus('y', 1)

    elif event.key() == Qt.Key.Key_Left or event.key() == Qt.Key.Key_A:
        self.moveFocus('x', -1)

    elif event.key() == Qt.Key.Key_Right or event.key() == Qt.Key.Key_D:
        self.moveFocus('x', 1)

    elif event.key() == Qt.Key.Key_Space:
        if self.copying is not None:
            self.paste(True)
        else:
            self.createLine()

    elif event.key() == Qt.Key.Key_C:
        if self.copying is not None:
            self.paste(True)
        else:
            self.createLine(True)

    elif event.key() == Qt.Key.Key_M:
        self.updateMirror(increment=1)

    elif event.key() == Qt.Key.Key_Q:
        if self.copying is not None:
            self.copying = None
            self.repaint()
        else:
            self.deleteLine()

    elif event.key() == Qt.Key.Key_Shift:
        self.selecting = None
        # If there's already bounds out there, just expand the selection instead
        if not len(self.bounds):
            self.addBound(False)
        self.addBound(False)

    elif event.key() == Qt.Key.Key_E:
        self.specificErase()

    elif event.key() == Qt.Key.Key_Escape:
        if self.copying is not None:
            self.copying = None
            self.repaint()
        else:
            if S.settings.value('window/esc_quits'):
                self.window().close()
            else:
                event.ignore()
                return

    elif event.key() == Qt.Key.Key_Delete:
        if self.copying is not None:
            self.copying = None
            self.repaint()
        else:
            if self.pattern is not None:
                self.destroySelection(False)
            else:
                self.deleteLine()


    else:
        # Other keys are handled by the associated QAction Shortcuts
        event.ignore()
        return

    event.accept()

def keyReleased(self, event):
    # No idea why capslock here is necissary, maybe it's my own personal hacked together keyboard configuration?
    if event.key() == Qt.Key.Key_Shift or event.key() == Qt.Key.Key_CapsLock:
        if self.selecting:
            self.addBound(False)
        self.selecting = False

@untested
def fileDropped(self, event):
    self.open(event.file())
    # with open(event.file, 'r') as f:
    #     self.lines = pickle.load(f)

def resizeEvent(self, event):
    self.regenerateDots(event.size())
    self.updateMirror()

def paintEvent(self, event):
    # Because apparently this gets called at the same time resizeEvent does?
    if self.dots is None:
        return

    painter = QPainter(self)
    painter.setBrush(self.backgroundBrush)
    if (S.settings.value('paper/antialiased')):
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

    #* Now it's all set up, do all the painting stuff -- in order
    # Draw the background
    painter.drawRect(self.rect())
    # brush = QBrush(Qt.Dense7Pattern)
    # painter.setBackgroundMode(Qt.BGMode.OpaqueMode)
    # painter.setBackground(self.backgroundBrush)

    # Draw the bounds box
    painter.setPen(self.boundsLinePen)
    painter.drawRect(self.getBoundsRect())

    # Draw the dots
    painter.setPen(self.dotPen)
    for dot in self.dots:
        # painter.drawPoint(*((self.width(), self.height()) - (dot % round(self.translation).data())))
        painter.drawPoint(*dot)
    # painter.drawPoints(self.dots)

    # Draw the pattern -- this automatically checks if we have a pattern and if we're repeating or not
    painter.save()
    if S.settings.value('paper/auto_imprint_pattern'):
        for line in self.patternLines:
            painter.setPen(line.pen)
            painter.drawLine(line)
    else:
        self._repeatPatternLoop(painter.drawPath, painter.translate)
    painter.restore()

    # Draw the regular lines
    # painter.drawLines(self.lines)
    for line in self.lines:
        painter.setPen(line.pen)
        painter.drawLine(line)

    # Draw the mirrorLines
    painter.setPen(self.mirrorLinePen)
    painter.drawLines(self.mirrorLines)

    # Draw the bounds
    for bound in self.bounds:
        painter.setPen(self.boundsPen)
        s=S.settings.value('paper/bounds_size')
        if S.settings.value('pattern/include_halfsies'):
            # painter.drawPolygon(QPolygon([QPoint(0, s), QPoint(s, 0), QPoint(-s, 0), QPoint(0, -s)]))
            painter.drawRoundedRect(QRectF(*(bound - s).data(), s*2, s*2), 1, 1)
        else:
            painter.drawEllipse(bound.copy(), s, s)

    # Draw the current line
    if self.currentLine is not None:
        # painter.setPen(self.currentLinePen)
        painter.setPen(self.currentPen)
        painter.drawLine(self.currentLine.copy())
        # Draw the mirrored current lines
        for line in self.mirrorLine(self.currentLine):
            painter.drawLine(line)

    # Draw the pattern we're copying, if we are
    if self.copying is not None:
        self.updateFocus()
        todo('This (and in paste) dont translate correctly')
        painter.setPen(self.activeCopyPen)
        painter.drawPath(self.copying.translated(self.focusLoc))
        # painter.drawPath(self.copying)

    # Draw the focus
    # if self.selecting:
        # painter.drawEllipse(self.focusLoc, self.BOUNDS_SIZE, self.BOUNDS_SIZE)
    if self.focusLoc and S.settings.value('paper/use_custom_cursor'):
        painter.setPen(self.focusPen)
        focusSize = S.settings.value('paper/focus_size')
        painter.drawLines([Line(self.focusLoc + (0, focusSize), self.focusLoc + (0, -focusSize)),
                            Line(self.focusLoc + (focusSize, 0), self.focusLoc + (-focusSize, 0))])

    # painter.setRenderHint(QPainter.Antialiasing, False)
    # painter.setPen(self.palette().dark().color())
    # painter.setBrush(Qt.BrushStyle.NoBrush)
    # painter.drawRect(QRect(0, 0, self.width() - 1, self.height() - 1))
    painter.end()
