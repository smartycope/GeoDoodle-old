import json
import os
import pickle
from copy import deepcopy
from os.path import join

from Cope import debug, todo, untested
from PyQt6 import uic
from PyQt6.QtCore import (QCoreApplication, QEvent, QFile, QLine, QLineF,
                          QRect, QRectF, Qt, QTimer, pyqtSignal, pyqtSlot)
from PyQt6.QtGui import QColor, QKeySequence, QPen, QAction
from PyQt6.QtWidgets import (QFileDialog, QHBoxLayout, QMainWindow,
                             QMessageBox, QPushButton, QSizePolicy,
                             QToolButton, QWidget)

import Pattern
from ColorDialog import ColorDialog
from Line import Line
from Paper import Paper
from RepeatMenu import RepeatMenu
from FileManager import FileManager

from Singleton import Singleton as S


# This has to be in a global scope I'm pretty sure
QCoreApplication.setAttribute(Qt.ApplicationAttribute.AA_ShareOpenGLContexts)

class Window(QMainWindow):
    # STARING_REPEAT_DOCK_HEIGHT = 82
    # STARING_COLOR_DOCK_HEIGHT = 50
    MAX_OVERLAP_MULTIPLIER = 5

#* Init
    def __init__(self):
        super(Window, self).__init__()
        uic.loadUi(join(S.ui, "main.ui"), self)

        # self.repeatMenu = RepeatMenu(self)
        self.fileManager = FileManager(self.paper)

        if S.settings.value('window/resize_with_dotSpread'):
            self.setSizeIncrement(S.settings.dotSpread, S.settings.dotSpread)

        # For SOME REASON, Qt Creator will not accept shortcuts for this widget
        self.clearSelectionButton.setShortcut(QKeySequence('Shift+Q'))
        # For SOME REASON Qt Creator will not set this value
        self.lineThickness.setValue(1)

        self.bindSignals()
        self.actions = []

        # Hide the overlap sliders to starting out
        self.xOverlapSlider.hide()
        self.yOverlapSlider.hide()
        # And the docks
        self.repeatDock.hide()
        self.colorDock.hide()
        self.penDock.hide()

        for i in range(10):
            getattr(self, f'pushButton_{i}').color = S.settings[f'window/color_button_{i}']

    def bindSignals(self):
        for group, actions in self.paper.actionsToAdd.items():
            for a in actions:
                getattr(self, f'menu{group}').addAction(a)

        self.open.triggered.connect(self.fileManager.show)
        self.exportPNG.triggered.connect(self.paper.exportPNG)
        self.exportDXF.triggered.connect(self.paper.exportDXF)
        self.exportSVG.triggered.connect(self.paper.exportSVG)
        self.quit.triggered.connect(self.close)

        self.preferencesMenu.triggered.connect(lambda: S.settings.generateMenu(self))

        def toggleVisible(obj):
            obj.setVisible(not obj.isVisible())
        self.showToolbar.triggered.connect(lambda: toggleVisible(self.colorDock))

        self.showLen.triggered.connect(self.paper.setShowLen)
        self.showPenBar.triggered.connect(lambda: toggleVisible(self.penDock))

        # When R is pressed...
        self.repeatButton.triggered.connect(self.toggleRepeatMode)

        self.controlsMenu.triggered.connect(self._controlsMenu)
        self.aboutMenu.triggered.connect(self._aboutMenu)
        self.creditsMenu.triggered.connect(self._creditsMenu)
        self.licenseMenu.triggered.connect(self._licenseMenu)
        self.donateMenu.triggered.connect(self._donateMenu)
        self.statusMenu.triggered.connect(self._statusMenu)
        self.aboutQt.triggered.connect(lambda *_: QMessageBox.aboutQt(None))

        #* The Repeat Options
        def updatePatternParam(param, to):
            # Because lambdas are kinda dumb sometimes
            S.settings[f'pattern/{param}'] = to
            self.paper.repaint()

        self.restoreDefaultsButton.triggered.connect(self.setDefaults)
        self.includeHalfsies.toggled.connect(lambda v: updatePatternParam('include_halfsies', v))

        self.xOverlapSlider.valueChanged.connect(lambda v: updatePatternParam('xOverlap', v))
        self.yOverlapSlider.valueChanged.connect(lambda v: updatePatternParam('yOverlap', v))

        self.rowSkip.valueChanged.connect(                     lambda v: updatePatternParam('skip_rows', v))
        self.rowSkipAmount.valueChanged.connect(               lambda v: updatePatternParam('skip_row_amt', v))
        self.columnSkip.valueChanged.connect(                  lambda v: updatePatternParam('skip_columns', v))
        self.columnSkipAmount.valueChanged.connect(            lambda v: updatePatternParam('skip_column_amt', v))
        self.flipRow.valueChanged.connect(                     lambda v: updatePatternParam('flip_rows', v))
        self.flipRowOrientation.currentIndexChanged.connect(   lambda v: updatePatternParam('flip_row_orient', v))
        self.flipColumn.valueChanged.connect(                  lambda v: updatePatternParam('flip_columns', v))
        self.flipColumnOrientation.currentIndexChanged.connect(lambda v: updatePatternParam('flip_column_orient', v))
        self.rotateRow.valueChanged.connect(                   lambda v: updatePatternParam('rotate_rows', v))
        self.rotateColumn.valueChanged.connect(                lambda v: updatePatternParam('rotate_columns', v))
        self.rotateRowAmt.valueChanged.connect(                lambda v: updatePatternParam('rotate_row_amt', v))
        self.rotateColumnAmt.valueChanged.connect(             lambda v: updatePatternParam('rotate_column_amt', v))
        self.shearRow.valueChanged.connect(                    lambda v: updatePatternParam('shear_rows', v))
        self.shearColumn.valueChanged.connect(                 lambda v: updatePatternParam('shear_columns', v))
        self.shearRowDir.currentIndexChanged.connect(          lambda v: updatePatternParam('shear_row_dir', v))
        self.shearColumnDir.currentIndexChanged.connect(       lambda v: updatePatternParam('shear_column_dir', v))
        self.shearRowAmt.valueChanged.connect(                 lambda v: updatePatternParam('shear_row_amt', v))
        self.shearColumnAmt.valueChanged.connect(              lambda v: updatePatternParam('shear_column_amt', v))

        #* Bind all the toolbar buttons
        def setPaperPen(color=None, width=None, style=None):
            if width is None:
                width = self.paper.currentPen.width()
            if style is None:
                style = self.paper.currentPen.style()
            if color is None:
                color = self.paper.currentPen.color
            self.paper.currentPen = QPen(color(), width, style)

        # For SOME reason, lambdas just REALLY hate loops.
        self.pushButton_0.clicked.connect(lambda: setPaperPen(color=self.pushButton_0.getColor))
        self.pushButton_1.clicked.connect(lambda: setPaperPen(color=self.pushButton_1.getColor))
        self.pushButton_2.clicked.connect(lambda: setPaperPen(color=self.pushButton_2.getColor))
        self.pushButton_3.clicked.connect(lambda: setPaperPen(color=self.pushButton_3.getColor))
        self.pushButton_4.clicked.connect(lambda: setPaperPen(color=self.pushButton_4.getColor))
        self.pushButton_5.clicked.connect(lambda: setPaperPen(color=self.pushButton_5.getColor))
        self.pushButton_6.clicked.connect(lambda: setPaperPen(color=self.pushButton_6.getColor))
        self.pushButton_7.clicked.connect(lambda: setPaperPen(color=self.pushButton_7.getColor))
        self.pushButton_8.clicked.connect(lambda: setPaperPen(color=self.pushButton_8.getColor))
        self.pushButton_9.clicked.connect(lambda: setPaperPen(color=self.pushButton_9.getColor))


        # self.lineThickness.valueChanged.connect(self.paper.currentPen.setWidth)
        self.lineThickness.valueChanged.connect(lambda w: setPaperPen(width=w))

        #* Bind the pen buttons
        self.solidPenButton.clicked.connect(lambda: setPaperPen(style=Qt.PenStyle.SolidLine))
        self.dashedPenButton.clicked.connect(lambda: setPaperPen(style=Qt.PenStyle.DashLine))
        self.dottedPenButton.clicked.connect(lambda: setPaperPen(style=Qt.PenStyle.DotLine))
        self.dashDotPenButton.clicked.connect(lambda: setPaperPen(style=Qt.PenStyle.DashDotLine))
        self.dashDotDotPenButton.clicked.connect(lambda: setPaperPen(style=Qt.PenStyle.DashDotDotLine))
        self.customPenButton.clicked.connect(lambda: setPaperPen(style=Qt.PenStyle.CustomDashLine))

    def syncWidgets(self):
        # We only need to do this upon showing, not upon hiding
        # if self.paper.repeating:
            # Make sure the sliders have updated values based on the available pattern
        # Paper.pattern is a getter, so lets just run it once
        pattern = self.paper.pattern
        self.xOverlapSlider.setMinimum(1 - pattern.size.width())
        self.xOverlapSlider.setMaximum(pattern.size.width() * self.MAX_OVERLAP_MULTIPLIER)
        self.yOverlapSlider.setMinimum(1 - pattern.size.height())
        self.yOverlapSlider.setMaximum(pattern.size.height() * self.MAX_OVERLAP_MULTIPLIER)
        self.xOverlapSlider.setValue(S.settings['pattern/xOverlap'])
        self.yOverlapSlider.setValue(S.settings['pattern/yOverlap'])

        self.rowSkip.setValue(                     S.settings['pattern/skip_rows'])
        self.rowSkipAmount.setValue(               S.settings['pattern/skip_row_amt'])
        self.columnSkip.setValue(                  S.settings['pattern/skip_columns'])
        self.columnSkipAmount.setValue(            S.settings['pattern/skip_column_amt'])
        self.flipRow.setValue(                     S.settings['pattern/flip_rows'])
        self.flipColumn.setValue(                  S.settings['pattern/flip_columns'])
        self.flipRowOrientation.setCurrentIndex(   S.settings['pattern/flip_row_orient'])
        self.flipColumnOrientation.setCurrentIndex(S.settings['pattern/flip_column_orient'])
        self.rotateRow.setValue(                   S.settings['pattern/rotate_rows'])
        self.rotateColumn.setValue(                S.settings['pattern/rotate_columns'])
        self.rotateRowAmt.setValue(                S.settings['pattern/rotate_row_amt'])
        self.rotateColumnAmt.setValue(             S.settings['pattern/rotate_column_amt'])
        self.shearRow.setValue(                    S.settings['pattern/shear_rows'])
        self.shearColumn.setValue(                 S.settings['pattern/shear_columns'])
        self.shearRowDir.setCurrentIndex(          S.settings['pattern/shear_row_dir'])
        self.shearColumnDir.setCurrentIndex(       S.settings['pattern/shear_column_dir'])
        self.shearRowAmt.setValue(                 S.settings['pattern/shear_row_amt'])
        self.shearColumnAmt.setValue(              S.settings['pattern/shear_column_amt'])

        self.rowSkipAmount.setMaximum(pattern.size.width()-1)
        self.rowSkipAmount.setMinimum(-pattern.size.width()+1)
        self.columnSkipAmount.setMaximum(pattern.size.height()-1)
        self.columnSkipAmount.setMinimum(-pattern.size.height()+1)

    def toggleRepeatMode(self):
        # This is already called by paper.toggleRepeat()
        if self.paper.pattern is None:
            return
        else:
            self.paper.toggleRepeat()
            for widget in (self.xOverlapSlider, self.yOverlapSlider, self.repeatDock):
                widget.setVisible(not widget.isVisible())

            self.syncWidgets()

#* Menus
    def _controlsMenu(self):
        controls = 'Important Controls:\n'\
        '\n'\
        'Left click/space bar: start/finish a line\n'\
        'Right click/c: start/finish a line and start a new one\n'\
        'Middle click/q: delete bound or lines (for now, will eventually switch to moving the pattern)\n'\
        'Scroll: zoom in/out (not implemented yet)\n'\
        'o: open the preferences menu\n'\
        'Q: delete all lines\n'\
        'b: add a bound\n'\
        'r: repeat the lines in the selected area across the screen\n'\
        'l: toggle line lengths\n'\
        'm: mirror lines (not implemented yet)\n'\
        't: toggle color toolbar (works, but colors are currently broken)\n'\
        'ctrl+s: save the pattern for later editing\n'\
        'ctrl+o: open a saved pattern\n'\
        'ctrl+n: make a new pattern (not implemeted yet)\n'\
        'ctrl+shift+s: save as (not implemented yet)\n'\
        'ctrl+e: export pattern as an image (I don\'t think this works. I haven\'t tried.)\n'\
        'ctrl+z: undo (not implemented yet)\n'\
        'ctrl+y: redo (not implemented yet)\n'\
        'Esc: exit'

        QMessageBox.information(None, 'Controls', controls)

    def _aboutMenu(self):
        about = 'Welcome to GeoDoodle!\n'\
        'GeoDoodle is a graph paper-like doodling program. At least, that\'s what it was originally intended for. '\
        'It turned out to be useful for things from quilting to landscaping, and I\'ve tried to include features for each.\n'\
        '\n'\
        'If you have any problems, if it crashes, if something doesn\'t work how you like it to, or you have ideas for it, '\
        'please let me know so I can fix it or add it in. This is the alpha test, so I would love your feedback. '\
        'Just text or email me at smartycope@gmail.com / (208)513-0110\n'\
        '\n'\
        'If you just found this and are completely bamboozled as to how to do anything with it, check out the controls menu.\n'\
        '\n'\
        'If you don\'t think it\'s complete garbage, check out the donate menu. College is expensive.\n'\
        '\n'\
        'If you are a programmer and you like it so much you\'d like to contribute, go for it. My GitHub username is smartycope.\n'\
        'Enjoy!'

        # QMessageBox.information(None, 'About', about)
        QMessageBox.about(None, 'About', about)

    def _creditsMenu(self):
        credits = 'This magnificent program is brought to you by: \n'\
        'Copeland Carter, Eng.\n'\
        '\n'\
        'I would also like to thank Brigham Keys, for answering all my dumb questions, and my parents for, you know, raising me.\n'\
        '\n'\
        'Hi Liam!'

        QMessageBox.about(None, 'Credits', credits)

    def _licenseMenu(self):
        l = 'This software is licensed under the GPL3.0.\n'\
        'This means it is free and open-source software\n'\
        'This just means you can do whatever the heck you want with it.\n'\
        'If you really want to, you can learn more about it here: https://www.gnu.org/licenses/gpl-3.0.en.html'

        QMessageBox.about(None, 'License', l)

    def _donateMenu(self):
        donate = 'While this software is free, I am a poor college student who likes to eat.\n'\
        'Like, preferably regularly.\n'\
        'So if you liked this program and can spare change for some ramen noodles, Venmo me some money at @Copeland-Carter\n'\
        'I\'d greatly appreciate it.'

        QMessageBox.about(None, 'Donate', donate)

    def _statusMenu(self):
        status = 'If you have any ideas or problems, text or email me at smartycope@gmail.com / (208)513-0110\n'\
        '\n'\
        'What works, what does\'t, and what\'s on the todo list \n'\
        '(in no particular order):\n'\
        'What works:\n'\
        'Drawing lines (you have to start somewhere)\n'\
        'Repeating patterns\n'\
        'Offsetting rows/columns\n'\
        'Flipping rows/columns\n'\
        'Saving patterns\n'\
        'Opening patterns\n'\
        'The preferences menu\n'\
        'Length labels\n'\
        'Changing the dot color\n'\
        'Changing the focus color\n'\
        'Changing the background color\n'\
        'The color toolbar\n'\
        '\n'\
        'What should work, but doesn\'t:\n'\
        'The induvidual line colors\n'\
        'Exporting patterns to images\n'\
        'Setting the background to be an image\n'\
        'The easter egg ;)\n'\
        '\n'\
        'Features I\'m planning to add eventually:\n'\
        'Setting the background to be a pretty gradient\n'\
        'Setting the background to be a satalite view of a property\n'\
        'More cool features in that direction (like hooking up to GIS data to get property lines and accurate measurements)\n'\
        'Moving the pattern/page around\n'\
        'Scaling the pattern/page\n'\
        'Customizable key repeat/interval delay\n'\
        'Customizable controls\n'\
        'Mirroring\n'\
        'Split the vertical and horizontal drop down menus into buttons, so you can do both\n'\
        'Lots of more things that I can\'t think of at the moment, but I know I\'ve had the idea for.'

        QMessageBox.about(None, 'Status', status)

#* Misc
    def setDefaults(self):
        S.settings.setDefault('pattern/xOverlap')
        S.settings.setDefault('pattern/yOverlap')
        S.settings.setDefault('pattern/skip_rows')
        S.settings.setDefault('pattern/skip_columns')
        S.settings.setDefault('pattern/skip_row_amt')
        S.settings.setDefault('pattern/skip_column_amt')
        S.settings.setDefault('pattern/flip_rows')
        S.settings.setDefault('pattern/flip_columns')
        S.settings.setDefault('pattern/flip_row_orient')
        S.settings.setDefault('pattern/flip_column_orient')
        S.settings.setDefault('pattern/rotate_rows')
        S.settings.setDefault('pattern/rotate_columns')
        S.settings.setDefault('pattern/rotate_row_amt')
        S.settings.setDefault('pattern/rotate_column_amt')
        S.settings.setDefault('pattern/shear_rows')
        S.settings.setDefault('pattern/shear_columns')
        S.settings.setDefault('pattern/shear_row_dir')
        S.settings.setDefault('pattern/shear_column_dir')
        S.settings.setDefault('pattern/shear_row_amt')
        S.settings.setDefault('pattern/shear_column_amt')
        self.syncWidgets()

    def close(self):
        self.paper.close()
        super().close()
