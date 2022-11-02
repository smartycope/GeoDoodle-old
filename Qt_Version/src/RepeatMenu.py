from PyQt6 import uic
from PyQt6.QtCore import QEvent, QFile, QLine, QLineF, QRect, QRectF, Qt
from PyQt6.QtWidgets import QFileDialog, QMainWindow, QWidget, QDialog

import Pattern
from Cope import debug, todo

from Singleton import Singleton

class RepeatMenu(QDialog):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        uic.loadUi(str(Singleton.ui / "repeat.ui"), self)

        todo('this could be optimized to update induvidual values instead')

    def updateValues(self, *_):
        #* Update all of the pattern options
        Pattern.params.includeHalfsies  = self.includeHalfsies.isChecked()
        Pattern.params.skipRows         = self.rowSkip.value()
        Pattern.params.skipRowAmt       = self.rowSkipAmount.value()
        Pattern.params.skipColumns      = self.columnSkip.value()
        Pattern.params.skipColumnAmt    = self.columnSkipAmount.value()
        Pattern.params.flipRows         = self.flipRow.value()
        Pattern.params.flipRowOrient    = self.flipRowOrientation.currentText()
        Pattern.params.flipColumns      = self.flipColumn.value()
        Pattern.params.flipColumnOrient = self.flipColumnOrientation.currentText()
        # This is a bit of a hack. This just tells the main Paper's pattern to regenerate
        todo('make this a signal/slot instead')
        self.parent().paper.updatePattern()

    def setVisible(self, visible):
        super().setVisible(visible)
        if visible:
            current = self.geometry()
            # Just shift it over a little so it's not RIGHT in the middle
            current.setX(current.x() + round(self.parent().width() / 2) + round(self.width() / 2))
            self.setGeometry(current.x(), current.y(), self.width(), self.height())
