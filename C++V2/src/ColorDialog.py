from PyQt5.QtWidgets import QColorDialog, QPushButton, QCommandLinkButton, QFileDialog, QLineEdit
from PyQt5.QtGui import QColor, QPalette
from PyQt5.QtCore import pyqtSlot, QEvent, Qt

from os.path import dirname

from Cope import debug
from copy import deepcopy


class ColorDialog(QPushButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setAutoFillBackground(True)
        self.color = QColor(237, 126, 4)
        self.updateColor()

        def _tmp():
            self.color = QColorDialog.getColor()
            self.updateColor()

        self.showMenu = _tmp
        self.clicked.connect(_tmp)

    def updateColor(self):
        #* StyleSheet method
        # self.setStyleSheet(f"background-color: rgba{self.color.getRgb()};"
        #                    f"selection-background-color: rgba{self.color.getRgb()};"
        #                    f"selection-color: rgba{self.color.getRgb()};")

        #* Palette method
        pal = QPalette()
        pal.setColor(QPalette.Highlight, self.color)
        pal.setColor(QPalette.Button, self.color)
        pal.setColor(QPalette.ButtonText, self.color)
        self.setPalette(pal)

        self.clearFocus()
        self.update()


    def getColor(self):
        return self.color.getRgb()

    def setColor(self, color):
        self.color = QColor(*color)
        self.updateColor()


class AbstractFileDialog(QLineEdit):
    def __init__(self, typeFunc, params, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.file = "NOT A FILE"
        self.setText(self.file)

        def getFile(*_):
            got = typeFunc(*params)
            debug(got)
            if not len(got) or not len(got[0]):
                return
            else:
                self.file = got if len(got[0]) == 1 else got[0]
                self.setText(self.file)

        def setFile(to):
            self.file = to

        self.returnPressed.connect(getFile)
        self.textChanged['QString'].connect(setFile)
        self.installEventFilter(self)



    def eventFilter(self, target, event):
        if event.type() == QEvent.KeyPress and event.key() == Qt.Key_Return and target is self:
            debug()
            event.accept()
            self.returnPressed.emit()
            return True
        else:
            return super().eventFilter(target, event)


class SaveFileDialog(AbstractFileDialog):
    def __init__(self, *args, **kwargs):
        super().__init__(QFileDialog.getSaveFileName,
                         (None, "Save Pattern", "~/", "GeoDoodle Pattern (*.gdl)"),
                         *args, **kwargs)


class OpenImageDialog(AbstractFileDialog):
    def __init__(self, *args, **kwargs):
        super().__init__(QFileDialog.getOpenFileName,
                         (None, "Open Image", "~/", "Image (*.png, *.jpg, *.jpeg, *.*)"),
                         *args, **kwargs)

class OpenPatternDialog(AbstractFileDialog):
    def __init__(self, *args, **kwargs):
        super().__init__(QFileDialog.getOpenFileName,
                         (None, "Open Pattern", "~/", "GeoDoodle Pattern (*.gdl)"),
                         *args, **kwargs)


class OpenFolderDialog(AbstractFileDialog):
    def __init__(self, *args, **kwargs):
        super().__init__(QFileDialog.getExistingDirectory,
                         (None, "Set Folder", "~/"),
                         *args, **kwargs)
