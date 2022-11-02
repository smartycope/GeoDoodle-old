import json
import os
import pickle
from copy import deepcopy
from os.path import join

from Cope import untested, debug, todo
from PyQt5 import uic
from PyQt5.QtCore import QEvent, QFile, QLine, QLineF, QRect, QRectF, Qt, QCoreApplication, pyqtSignal, pyqtSlot, QTimer
from PyQt5.QtWidgets import QFileDialog, QMainWindow, QWidget, QAction, QToolButton, QHBoxLayout, QSizePolicy, QPushButton, QMessageBox
from PyQt5.QtGui import QColor, QKeySequence, QPen

from ColorDialog import ColorDialog
from Geometry import *
from Line import Line
from Paper import Paper
import Pattern
from RepeatMenu import RepeatMenu

from os.path import dirname, join; DIR=dirname(dirname(__file__)); UI=join(DIR, 'ui')


# This has to be in a global scope I'm pretty sure
QCoreApplication.setAttribute(Qt.AA_ShareOpenGLContexts)

class Game(QMainWindow):
    STARING_REPEAT_DOCK_HEIGHT = 82
    STARING_COLOR_DOCK_HEIGHT = 50
    MAX_OVERLAP_MULTIPLIER = 5
#* Init
    def __init__(self):
        super(Game, self).__init__()
        uic.loadUi(join(UI, "main.ui"), self)
        self.setWindowTitle('GeoDoodle')

        # To make everything resize with the window
        self.centralWidget().setLayout(self.gridLayout)
        # Do the same for the docks
        self.dockCentralWidget.setLayout(self.repeatLayout)
        self.dock.setWidget(self.dockCentralWidget)
        self.toolbarCentralWidget.setLayout(self.toolbarLayout)
        self.toolbar.setWidget(self.toolbarCentralWidget)
        self.penCentralWidget.setLayout(self.penLayout)
        self.penDock.setWidget(self.penCentralWidget)

        self.repeatMenu = RepeatMenu(self)

        todo('specify a key repeat', False)
        todo('fix fullscreen', False)
        todo('set up a settings file (Im pretty sure theres a Qt class for this)')
        # with open(DIR + 'settings.jsonc', 'r') as file:
        #     self.settings = json.load(file)

        #* self.setSizeIncrement(self.paper.dotSpread, self.paper.dotSpread)

        # For SOME REASON, Qt Creator will not accept shortcuts for this widget
        self.clearSelectionButton.setShortcut(QKeySequence('Shift+Q'))
        # For SOME REASON Qt Creator will not set this value
        self.lineThickness.setValue(1)

        # I don't remember what this does
        # self.setAttribute(Qt.AA_ShareOpenGLContexts)
        # QCoreApplication.setAttribute(Qt.AA_ShareOpenGLContexts)

        self.bindSignals()
        self.actions = []

        # Hide the overlap sliders to starting out
        self.xOverlapSlider.hide()
        self.yOverlapSlider.hide()
        self.dock.hide()
        self.toolbar.hide()
        self.penDock.hide()
        # self.resizeDocks([self.dock, self.toolbar], [self.STARING_REPEAT_DOCK_HEIGHT, self.STARING_COLOR_DOCK_HEIGHT], Qt.Orientation.Vertical)

        # self.createToolbar()

        self.installEventFilter(self)

        # Why am I doing this??
        self.setGeometry(round(100 / self.width()), round(100 / self.height()), self.width(), self.height())

        for cnt, color in enumerate(('black', 'red', 'green', 'yellow', 'orange', 'blue', 'purple', 'white', 'brown', 'pink')):
            getattr(self, f'pushButton_{cnt}').color = QColor(color)


    def eventFilter(self, target, event):
        """ Key presses aren't widget specific, so they're handled by the window """
        if event.type() == QEvent.KeyPress:
            # if event.key() == Qt.Key_T:
            self.paper.keyPressed(event)
        if event.type() == QEvent.KeyRelease:
            self.paper.keyReleased(event)

        return super().eventFilter(target, event)

    def bindSignals(self):
        self.new_.triggered.connect(self.paper.clearAll)
        self.open.triggered.connect(self.paper.open)
        self.save.triggered.connect(self.paper.save)
        self.saveAs.triggered.connect(self.paper.saveAs)
        self.exportPNG.triggered.connect(self.paper.exportPNG)
        self.exportDXF.triggered.connect(self.paper.exportDXF)
        self.exportSVG.triggered.connect(self.paper.exportSVG)
        self.quit.triggered.connect(self.close)

        self.preferencesMenu.triggered.connect(self._preferencesMenu)
        self.undo.triggered.connect(self.paper.undo)
        self.redo.triggered.connect(self.paper.redo)

        def toggleVisible(obj):
            obj.setVisible(not obj.isVisible())
        self.showToolbar.triggered.connect(lambda: toggleVisible(self.toolbar))

        self.fullscreen_.triggered.connect(self.toggleFullscreen)
        self.showLen.triggered.connect(self.paper.setShowLen)
        self.showPenBar.triggered.connect(lambda: toggleVisible(self.penDock))

        # When R is pressed...
        self.repeatButton.triggered.connect(self.toggleRepeatMode)

        self.addBound.triggered.connect(self.paper.addBound)
        self.clearSelectionButton.triggered.connect(self.paper.bounds.clear)
        self.clearSelectionButton.triggered.connect(self.paper.repaint)
        self.clearAll.triggered.connect(self.paper.clearAll)

        self.actionHome.triggered.connect(self.paper.goHome)

        self.imprintLines.triggered.connect(self.paper.imprintLines)
        self.copyAction.triggered.connect(self.paper.copy)
        self.pasteAction.triggered.connect(self.paper.paste)
        self.cutAction.triggered.connect(self.paper.cut)

        todo('bind the mirror QActions')
        # mirror
        # mirrorInvert
        # mirrorVertical
        # mirrorHorizontal
        # mirrorCrossing

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
            setattr(Pattern.params, param, to)
            self.paper.updatePattern()

        def setXOverlap(to):
            Pattern.params.xOverlap = to
            self.paper.updatePattern()

        def setYOverlap(to):
            Pattern.params.yOverlap = to
            self.paper.updatePattern()

        self.restoreDefaultsButton.triggered.connect(self.setDefaults)
        self.includeHalfsies.toggled.connect(lambda v: updatePatternParam('includeHalfsies', v))

        self.xOverlapSlider.valueChanged.connect(setXOverlap)
        self.yOverlapSlider.valueChanged.connect(setYOverlap)

        self.rowSkip.valueChanged.connect(                     lambda v: updatePatternParam('skipRows', v))
        self.rowSkipAmount.valueChanged.connect(               lambda v: updatePatternParam('skipRowAmt', v))
        self.columnSkip.valueChanged.connect(                  lambda v: updatePatternParam('skipColumns', v))
        self.columnSkipAmount.valueChanged.connect(            lambda v: updatePatternParam('skipColumnAmt', v))
        self.flipRow.valueChanged.connect(                     lambda v: updatePatternParam('flipRows', v))
        self.flipRowOrientation.currentIndexChanged.connect(   lambda v: updatePatternParam('flipRowOrient', v))
        self.flipColumn.valueChanged.connect(                  lambda v: updatePatternParam('flipColumns', v))
        self.flipColumnOrientation.currentIndexChanged.connect(lambda v: updatePatternParam('flipColumnOrient', v))

        #* Bind all the toolbar buttons
        def setPaperPen(color=self.paper.currentPen.color, width=None, style=None):
            if width is None:
                width = self.paper.currentPen.width()
            if style is None:
                style = self.paper.currentPen.style()
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

        # The repeat menu
        # If they press okay/cancel, set/reset the pattern
        # self.repeatMenu.okCancel.accepted.connect(self.paper.acceptPattern)
        # self.repeatMenu.okCancel.accepted.connect(toggleSliders)
        # self.repeatMenu.okCancel.rejected.connect(self.paper.revertPattern)
        # self.repeatMenu.okCancel.rejected.connect(toggleSliders)

#* Preferences
    @untested
    def _preferencesMenu(self):
        self.optionsMenu = uic.loadUi(join(UI, "preferences.ui"))
        self.setWindowTitle('Preferences')
        self.setModal(True)
        # self.optionsMenu
        # self.shortCuts = {}

        def restoreDefaults():
            todo('set defaults')

        def setShortcut():
            todo('custom shortcuts')

        def setBackground(selector):
            debug(selector)
            if selector == "Color":
                self.paper.background = self.optionsMenu.backgroundColor.getColor()
            elif selector == "Pattern":
                todo('figure out how to select a pattern/gradient')
                self.paper.background = self.optionsMenu.backgroundColor.getColor()
            elif selector == "Image":
                self.paper.background = self.optionsMenu.backgroundPath.file
            elif selector == "Map Image":
                todo('get an image from the map')
                self.paper.background = (255, 160, 100, 255)
            else:
                raise UserWarning("Something has gone horribly, horribly wrong.")


        #* Bind the dot unit mesurement to look pretty
        self.optionsMenu.dotSpreadMeasure.setSuffix(' ' + self.optionsMenu.dotSpreadUnit.text())
        self.optionsMenu.dotSpreadUnit.textEdited.connect(lambda s: self.optionsMenu.dotSpreadMeasure.setSuffix(' ' + s))

        #* Connect the restoreDefaults button
        self.optionsMenu.restoreDefaults.clicked.connect(restoreDefaults)

        #* Set all the values from paper
        if type(self.paper.background) is tuple:
            self.optionsMenu.backgroundColor.setColor(self.paper.background)
        elif type(self.paper.background) is str:
            self.optionsMenu.backgroundPath.file = self.paper.background
        # elif type(self.paper.background) is QGradient:
        #*     todo('Setting QGradient')
        # elif type(self.paper.background) is QImage:
        #*     todo('Setting QImage')

        self.optionsMenu.dotColor.setColor(self.paper.dotColor)
        self.optionsMenu.focusColor.setColor(self.paper.focusColor)

        self.optionsMenu.dotSpread.setValue(self.paper.dotSpread)
        self.optionsMenu.dotSpreadMeasure.setValue(self.paper.dotSpreadMeasure)
        self.optionsMenu.dotSpreadUnit.setText(self.paper.dotSpreadUnit)

        self.optionsMenu.exportThickness.setValue(self.paper.exportThickness)
        self.optionsMenu.savePath.setText(self.paper.savePath)
        self.optionsMenu.exportPath.setText(self.paper.exportPath)

        #* Fill the drop down menus
        self.optionsMenu.backgroundType.addItems(("Color", "Pattern", "Image", "Map Image"))


        #* Connect the background menu
        self.optionsMenu.backgroundType.currentIndexChanged["QString"].connect(setBackground)

        # TODO Set up the shortcuts
        self.optionsMenu.setShortcut.clicked.connect(setShortcut)

        #* Connect the ok button
        self.optionsMenu.accepted.connect(lambda *_: self.paper.updateSettings(self.optionsMenu))
        self.optionsMenu.accepted.connect(lambda *_: setBackground(self.optionsMenu.backgroundType.currentText()))

        self.optionsMenu.show()

#* Toggling
    @untested
    def toggleFullscreen(self, *_):
        todo('toggleFullscreen')
        # pygame.display.toggle_fullscreen()

        # if not self.fullscreen:
        #     self.mainSurface = pygame.display.set_mode(self.screenSize, self.fullscreenWindowFlags)
        #     self.startingPoint = Pointf(self.screenSize) / 2
        #     self.dots = genDotArrayPoints(self.screenSize, OFFSCREEN_AMOUNT, DOTSPREAD)
        # else:
        #     self.mainSurface = pygame.display.set_mode(self.windowedSize, self.windowedWindowFlags)
        #     self.startingPoint = Pointf(self.windowedSize) / 2
        #     self.dots = genDotArrayPoints(self.windowedSize, OFFSCREEN_AMOUNT, DOTSPREAD)

        # self.fullscreen = not self.fullscreen

    def toggleRepeatMode(self):
        self.paper.updatePattern()
        if self.paper.pattern is None:
            return
        else:
            self.paper.toggleRepeat()
            for widget in (self.xOverlapSlider, self.yOverlapSlider, self.dock):
                widget.setVisible(not widget.isVisible())

            # We only need to do this upon showing, not upon hiding
            if self.paper.repeating:
                # Make sure the sliders have updated values based on the available pattern
                self.xOverlapSlider.setMinimum(1 - self.paper.pattern.dotSize.width())
                self.xOverlapSlider.setMaximum(self.paper.pattern.dotSize.width() * self.MAX_OVERLAP_MULTIPLIER)
                self.yOverlapSlider.setMinimum(1 - self.paper.pattern.dotSize.height())
                self.yOverlapSlider.setMaximum(self.paper.pattern.dotSize.height() * self.MAX_OVERLAP_MULTIPLIER)
                self.xOverlapSlider.setValue(Pattern.params.xOverlap)
                self.yOverlapSlider.setValue(Pattern.params.yOverlap)

#* Toolbar
    # @untested
    # def toggleToolbar(self, on):
    #     self.toolbar.addWidget(self.lSpacer)
    #     if on: #self.getMenuBarAction('View', 'Toggle Toolbar').isChecked():
    #         self.toolbar.show()
    #     else:
    #         self.toolbar.hide()
        # self.toolbar.hide()

    @untested
    def createToolbar(self):
        class QDoubleAction(QAction):
            # I have NO idea why this is static, and but it only works if it is.
            doubleClicked = pyqtSignal()
            def __init__(self, *args, delay=250, **kwargs):
                QPushButton.__init__(self, *args, **kwargs)
                # self.doubleClicked = pyqtSignal()
                self.delay = delay
                self.timer = QTimer()
                self.timer.setSingleShot(True)
                def tmp():
                    self.triggered.emit()
                    self.timer.stop()
                self.timer.timeout.connect(tmp)
                super().triggered.connect(self.checkDoubleClick)

            @pyqtSlot()
            def checkDoubleClick(self):
                if self.timer.isActive():
                    self.doubleClicked.emit()
                    self.timer.stop()
                else:
                    self.timer.start(self.delay)

        class ToolColorButton(QDoubleButton):
            colors = [QColor(i) for i in ('black', 'red', 'green', 'yellow', 'orange', 'blue', 'purple', 'white', 'brown', 'pink')]
            colorChanged = pyqtSignal(tuple)

            def __init__(self, index, *args, **kwargs):
                super().__init__(*args, **kwargs)

                self.color = self.colors[index]
                self.setObjectName(str(index+1))
                self.setText(str(index+1))
                self.setMinimumWidth(45)
                self.setShortcut(QKeySequence(str(index-1)))
                self.updateColor()

                self.clicked.connect(self.updateColor)
                self.doubleClicked.connect(self.getColor)

            def updateColor(self):
                #* StyleSheet method
                self.setStyleSheet(f"widget-animation-duration:40;"
                                   f"background-color: rgba{self.color.getRgb()};"
                                   f"color: rgba{self.color.getRgb()};"
                                   f"selection-background-color: rgba{self.color.getRgb()};"
                                   f"selection-color: rgba{self.color.getRgb()};")

                #* Palette method
                # pal = QPalette()
                # pal.setColor(QPalette.Highlight, self.colors[i])
                # pal.setColor(QPalette.Button, self.colors[i])
                # pal.setColor(QPalette.ButtonText, self.colors[i])
                # self.actions[i].setPalette(pal)

                # self.paper.currentDrawColor = self.colors[i].getRgb()

                self.colorChanged.emit(self.color.getRgb())

                # self.clearFocus()
                self.setFocus()
                self.update()

            def getColor(self):
                self.color = QColorDialog.getColor()
                self.updateColor()


        self.toolbar = self.addToolBar("")

        #* Configure the toolbar setup
        self.toolbar.setLayout(QHBoxLayout())
        self.toolbar.layout().setSpacing(25)

        #* Make simple expanding widgets to center the colors
        self.rSpacer = QWidget()
        self.lSpacer = QWidget()
        self.rSpacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.lSpacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.toolbar.addWidget(self.rSpacer)

        #* Actually add the buttons
        for i in range(10):
            button = ToolColorButton(i)
            # button.colorChanged.connect(self.paper.setCurrentDrawColor)
            self.toolbar.addWidget(button)

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
        'f: toggle fullscreen (not implemented yet)\n'\
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
        self.includeHalfsies.setChecked(False)
        self.rowSkip.setValue(1)
        self.rowSkipAmount.setValue(0)
        self.columnSkip.setValue(1)
        self.columnSkipAmount.setValue(0)
        self.flipRow.setValue(1)
        self.flipRowOrientation.setIndex(0)
        self.flipColumn.setValue(1)
        self.flipColumnOrientation.setIndex(0)
        self.paper.updatePattern()

    @untested
    def meme():
        url = QtCore.QUrl.fromLocalFile('/home/marvin/Downloads/Rick-Astley-Never-Gonna-Give-You-Up.mp3')
        content = QtMultimedia.QMediaContent(url)
        player = QtMultimedia.QMediaPlayer()
        player.setMedia(content)
        player.play()


        meme = uic.loadUi(join(DATA, 'meme.ui'))
        debug(meme)

        pixmap = QPixmap("/home/marvin/hello/python/GeoDoodle/Qt_Version/GeoDoodle/paulblart.png")
        scene = QGraphicsScene(meme)
        item = QGraphicsPixmapItem(pixmap)
        scene.addItem(item)
        meme.graphicsView.setScene(scene)

        meme.show()

    def close(self):
        self.paper.close()
        super().close()
