from PyQt6 import uic
import numpy as np
import json
from Singleton import Singleton as S
from PyQt6.QtCore import (QCoreApplication, QEvent, QFile, QLine, QLineF,
                          QRect, QRectF, Qt, QTimer, pyqtSignal, pyqtSlot)
from PyQt6.QtGui import QColor, QKeySequence, QPen, QAction, QStandardItemModel, QBrush
from PyQt6.QtWidgets import (QFileDialog, QHBoxLayout, QMainWindow, QTableView, QTableWidget, QTableWidgetItem,
                             QMessageBox, QPushButton, QSizePolicy, QDialog,
                             QToolButton, QWidget)
from Paper import Paper
from Cope import debug


class PaperButton(Paper):
    def __init__(self, parent, file, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.file = file
        with open(file, 'r') as f:
            self.data = f.read()
            self.deserialze(self.data)

        self.setMouseTracking(False)
        # This doesn't work, cause the pattern might not be at the center
        # self.goHome()
        # TODO: Transform to the start of the first line in self.lines so we can actually see the pattern
        self.setCursor(self.parent().cursor())
        self.repaint()

    def init(self):
        super().init()
        if len(self.bounds):
            goto = self.bounds[0]
            self.bounds.clear()
        elif len(self.lines):
            goto = self.lines[0].start
        else:
            goto = Point()

        self.home = np.array([
                    [8, 0, self.width()/2],
                    [0, 8, self.height()/2],
                    [0, 0, 1]
                ])
        self.transformation = self.home.copy()
        self.relativeTransformation = self.home.copy()

        self.transform(np.array([
            [1, 0, goto.x],
            [0, 1, goto.y],
            [0, 0, 1],
        ]))
        self.toggleRepeat()

    def mouseMoveEvent(self, event):
        pass
    def mousePressEvent(self, event):
        self.setFocus()
    def mouseDoubleClickEvent(self, event):
        self.window().load()
    def mouseReleaseEvent(self, event):
        pass
    # Actually, I kinda like this
    # def wheelEvent(self, event):
        # pass
    def keyPressEvent(self, event):
        pass
    def keyReleaseEvent(self, event):
        pass
    def fileDropped(self, event):
        pass
    def paintEvent(self, event):
        tmp = self.backgroundBrush
        if self.hasFocus():
            self.backgroundBrush = QBrush(QColor(self.backgroundBrush.color().darker(130)))
        super().paintEvent(event)
        self.backgroundBrush = tmp


class FileManager(QDialog):
    def __init__(self, paper):
        super().__init__()
        # self.table = QTableView()
        uic.loadUi(S.ui / "FileManager.ui", self)
        self.searchBar.hide()
        self.paper = paper
        self.cols = 5
        self.table.setModel(QStandardItemModel(1, self.cols))
        self.bindSignals()

    def bindSignals(self):
        self.loadButton.pressed.connect(self.load)
        self.mergeButton.pressed.connect(self.merge)
        self.searchBar.textChanged.connect(self.filterTable)

    def filterTable(self, text):
        pass

    def load(self):
        if len(self.table.selectedIndexes()) == 1:
            selected = self.table.indexWidget(self.table.selectedIndexes()[0])
            if selected is not None:
                self.paper.deserialze(selected.data)
                self.paper.saveFile = selected.file
                self.close()

    def merge(self):
        if len(self.table.selectedIndexes()) == 1:
            selected = self.table.indexWidget(self.table.selectedIndexes()[0])
            if selected is not None:
                self.paper.lines += selected.lines
                self.paper.bounds += selected.bounds
                self.close()

    def reload(self):
        debug(trace=1)
        for cnt, file in enumerate(S.settings['files/loadDir'].iterdir()):
            p = PaperButton(self.table, file)
            self.table.setIndexWidget(self.table.model().index(cnt % self.cols, cnt // self.cols), p)

    def show(self):
        self.reload()
        super().show()
