from Color import Color, namedColor
from Point import Point
from Geometry import *
# from Globals import *
import os, json
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame, pygame_gui
from enum import Enum, auto
from pygame_gui.elements import *
from pygame_gui.windows import UIColourPickerDialog, UIFileDialog
from pygame_gui.core.utility import create_resource_path

from pygame_gui.ui_manager import UIManager
from pygame_gui.elements.ui_window import UIWindow
from pygame_gui.elements.ui_image import UIImage

DIR = os.path.dirname(__file__) + '/../'
SAVES_FOLDER = DIR + 'saves/'
GUI_THEME_FILE = DIR + 'data/myTheme.json'

# ARROW = '→'

with open(DIR + 'settings.json', 'r') as f:
    SETTINGS = json.load(f)

offScreenAmount = SETTINGS['offScreenAmount'] * SETTINGS['dotSpread']

#TODO 
# create_tool_tip(text: str, position: Tuple[int, int], hover_distance: Tuple[int, int]) → pygame_gui.core.interfaces.tool_tip_interface.IUITooltipInterface
# This would be cool to add

# All the different types of classes we have
class menu(Enum):
    OPTION   = 0
    WELCOME  = 1
    CONTROLS = 2
    # TOOLBAR  = 3
    REPEAT   = 4
    SAVE     = 5
    OPEN     = 6
    EXPORT   = 7


# The semi-abstract class via which all the GUIs are made. Be careful when touching this.
class Window(UIWindow):
    def __init__(self, pos, uiManager, title, id, menu, size):
        if pos[0] is None:
            pos[0] = (uiManager.get_root_container().get_size()[0] / 2) - (size[0] / 2)

        if pos[1] is None:
            pos[1] = (uiManager.get_root_container().get_size()[1] / 2) - (size[1] / 2)

        self.width  = size[0]
        self.height = size[1]

        #// This might not stay here
        self.uiManager = uiManager

        self.id = id
        self.active = False

        super().__init__(pygame.Rect(pos, (self.width, self.height)), uiManager, window_display_title=title, object_id=id)

        drawSurfaceSize = self.get_container().get_size()
        self.drawSurface = pygame.Surface(drawSurfaceSize).convert()
        
        self.drawImage = UIImage(pygame.Rect((0, 0), drawSurfaceSize),
                            self.drawSurface,
                            manager=self.uiManager,
                            container=self,
                            parent_element=self)

        self.menu = menu(uiManager, self.get_container())

    def updateContextData(self, context):
        self.menu.updateContextData(context)

    def process_event(self, event):
        # if not (event.type == pygame.USEREVENT and event.user_type == pygame_gui.UI_WINDOW_CLOSE):
        handled = super().process_event(event)

        if event.type == pygame.USEREVENT and event.user_type == pygame_gui.UI_WINDOW_CLOSE and event.ui_object_id == self.id:
            handled = True
            self.disable()
            self.hide()
            self.set_blocking(True)

        # TODO this doesn't quite work. Split it up into 2 if statements, maybe?
        if self.check_clicked_inside_or_blocking(event) or \
           (event.type == pygame.USEREVENT and \
            event.user_type == pygame_gui.UI_BUTTON_PRESSED and \
            (self.id + ".#window_element_container" in event.ui_object_id)):

            # print('here!')
            self.enable()
            self.show()
            self.set_blocking(False)
            # handled = True
            event_data = {'user_type': 'window_selected',
                          'ui_element': self,
                          'ui_object_id': self.most_specific_combined_id
                         }

            window_selected_event = pygame.event.Event(pygame.USEREVENT, event_data)
            pygame.event.post(window_selected_event)

        if self.active and not handled:
            handled = self.menu.handleEvent(event)

        return handled

    def update(self, deltaTime):
        if self.alive() and self.active:
            self.drawImage.image.fill(self.uiManager.get_theme().get_colour('dark_bg'))
            
            self.menu.draw(self.drawImage.image)

        super().update(deltaTime)


# The class that the main Game class talks to, and that initializes all of the specific GUIs
class MenuManager:
    def __init__(self, rootWindowSurface):
        self.width  = rootWindowSurface.get_width()
        self.height = rootWindowSurface.get_height()

        self.rootWindowSurface = rootWindowSurface

        self.uiManager = pygame_gui.UIManager((self.width, self.height), GUI_THEME_FILE)

        self.hasHacked = False

        self.passDataToGame = dict(zip(menu, [None] * len(menu)))

        self.repeatWindow   = Window([None, None], self.uiManager, 'Repeat Pattern' , '#repeat_window',   RepeatMenu,   (self.width / 1.25, self.height / 1.25))
        self.optionWindow   = Window([None, None], self.uiManager, 'Options'        , '#options_window',  OptionMenu,   (300, self.height / 1.05))
        self.saveWindow     = Window([None, None], self.uiManager, 'Save Pattern'   , '#save_window',     SaveMenu,     (500, 400))
        self.openWindow     = Window([None, None], self.uiManager, 'Open Pattern'   , '#open_window',     OpenMenu,     (500, 400))
        self.exportWindow   = Window([None, None], self.uiManager, 'Export Pattern' , '#export_window',   ExportMenu,   (500, 400))
        self.controlsWindow = Window([None, None], self.uiManager, 'Edit Controls'  , '#controls_window', ControlsMenu, (500, 400))
        self.welcomeWindow  = Window([0, 0],       self.uiManager, 'Welcome!'       , '#welcome_window',  WelcomeMenu,  (self.width - 10, self.height - 10))
        # self.toolbarWindow  = Window((50, 50),     self.uiManager, ''       , '#options_window', OptionsMenu, (500, 400))

    def run(self, event, type=None):
        # if type is not None:
        #     self.getWindow(type)
        if event.type == pygame.QUIT:
            exit(0)

        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            return False

        if event.type == pygame.USEREVENT and event.user_type == 'window_selected':
            event.ui_element.active = True
            event.ui_element.enable()
            event.ui_element.show()
            event.ui_element.set_blocking(False)
            # print(f'blocked: {event.ui_element.is_blocking}\nenabled: {event.ui_element.is_enabled}\nin focus: {event.ui_element.is_focused}\nvisible: {event.ui_element.visible}\n------------------------')
            # event.ui_element.show()
            # event.ui_element.enable()

        if not (event.type == pygame.USEREVENT and \
                event.user_type == pygame_gui.UI_WINDOW_CLOSE):
        #    not (event.type == pygame.USEREVENT and \
        #         event.):
            self.uiManager.process_events(event)

        if event.type == pygame.USEREVENT and event.user_type == pygame_gui.UI_WINDOW_CLOSE:
            self.hasHacked = False
            return False # Tells Game that the window is now closed
        else:
            return True

    def hackActivateWindow(self, window):
        if window == menu.REPEAT:
            loc = (self.width / 2, self.height / 2)
        elif window == menu.OPTION:
            loc = ((self.width / 2) + 50, self.height / 2)
        else:
            loc = (self.width / 2, self.height / 2)

        eventData = {'pos': loc, 'button': 1, 'window': None}

        pygame.event.post(pygame.event.Event(pygame.MOUSEBUTTONDOWN, eventData))
        pygame.event.post(pygame.event.Event(pygame.MOUSEBUTTONUP,   eventData))

    def getWindow(self, type):
        if type == menu.OPTION:
            return self.optionWindow    
        if type == menu.WELCOME:
            return self.welcomeWindow
        if type == menu.CONTROLS:
            return self.controlsWindow
        # if type == menu.TOOLBAR:
        #     return self.toolWindow
        if type == menu.REPEAT:
            return self.repeatWindow
        if type == menu.SAVE:
            return self.saveWindow
        if type == menu.OPEN:
            return self.openWindow
        if type == menu.EXPORT:
            return self.exportWindow

    def draw(self, deltaTime, activate, context):
        self.getWindow(activate).set_blocking(False)
        self.getWindow(activate).enable()
        self.getWindow(activate).show()
        if not self.hasHacked:
            self.hackActivateWindow(activate)
            self.hasHacked = True

        others = list(menu)
        others.remove(activate)
        for i in others:
            self.getWindow(i).set_blocking(True)
            self.getWindow(i).disable()
            self.getWindow(i).hide()

        # Get Game to talk to the induvidual GUIs
        self.getWindow(activate).updateContextData(context)

        # Get the induvidual GUIs to talk to Game
        for m in menu:
            if self.getWindow(m).active:
                self.passDataToGame[m] = self.getWindow(m).menu.passDataBack()
            else:
                self.passDataToGame[m] = None

        self.uiManager.update(deltaTime)
        self.uiManager.draw_ui(self.rootWindowSurface)

        return self.passDataToGame


#TODO Make abscract classes for the menus and the elements
# All the different GUI classes
PREVIEW_BACKGROUND_COLOR = [200, 160, 100]
PREVIEW_DOT_SPREAD = 16
class RepeatMenu:
    def __init__(self, uiManager, container):
        self.size = container.get_size()
        self.uiManager = uiManager
        self.pattern = None

        # This is Game's dotSpread, not the preview surface's dotSpread.
        self.gameDotSpread = None

        self.halfsies = False
        self.overlap = [0, 0]

        self.allowPassing = False

        self.uiManager = uiManager
        self.container = container

        row = self.size[1] / 20
        textPos                    = [None, row]
        includeHalfsiesCheckboxPos = [(self.size[0] / 2) - 100, row * 2.5]
        self.xOverlapSliderPos     = [(self.size[0] / 2) - 205, row * 6]
        self.yOverlapSliderPos     = [(self.size[0] / 2) + 25,  row * 6]
        createPatternButtonPos     = [None,                     row * 8.5]
        self.previewEdgeOffset     = self.size[1] / 20

        self.text = Text(textPos, uiManager, container, 'Repeat Menu!')
        self.includeHalfsiesCheckbox = CheckBox(includeHalfsiesCheckboxPos, self.uiManager, container, 'Include Halfsies', startValue=self.halfsies)
        self.xOverlapSlider = None      #* Created when we get access to the pattern data (for the range)
        self.yOverlapSlider = None
        self.createPatternButton = Button(createPatternButtonPos, self.uiManager, container, 'Create!', print, params=['Creating Pattern...'], size=[100, None])
        self.previewStartY = (row * 8.5) + self.previewEdgeOffset + self.createPatternButton.height

        self.previewSurface = pygame.Surface(((self.size[0] - self.previewEdgeOffset * 6), 
                                               self.size[1] - self.previewStartY - self.previewEdgeOffset))
        self.previewDots = genDotArrayPoints(self.previewSurface.get_size(), SETTINGS['offScreenAmount'], PREVIEW_DOT_SPREAD)
        self.updatePreviewSurface()

    def updatePreviewSurface(self):
        # Draw background
        self.previewSurface.fill(PREVIEW_BACKGROUND_COLOR)

        # Draw the dots
        for i in self.previewDots:
            pygame.draw.rect(self.previewSurface, SETTINGS['dotColor'], pygame.Rect(i.data(),
                             [SETTINGS['dotSize'], SETTINGS['dotSize']]))

        # patternStartingPoint = self.previewDots[round(len(self.previewDots) / 2)]

        # Draw the lines
        if self.pattern is not None:
            # print('drawing lines')

            startPoint = Point(min(self.previewDots, key=lambda i: i.x).x,
                               min(self.previewDots, key=lambda i: i.y).y)

            print('startPoint:', startPoint)

            # drawLines = scaleLines(self.pattern.repeat(self.size, offScreenAmount, self.overlap,
            #                                            dotSpread=PREVIEW_DOT_SPREAD,
            #                                            startPoint=startPoint - 6, # - self.previewDots[0], # - (Point(self.size) / 2),
            #                                            halfsies=self.halfsies,
            #                                            preview=True),
            #                        Point(self.previewSurface.get_size()) / 2, self.gameDotSpread, PREVIEW_DOT_SPREAD)

            # for i in drawLines:
            #     i.start -= Point(self.size) / 2
            #     i.end   -= Point(self.size) / 2

            drawLines = scaleLines(self.pattern.repeat(self.size, offScreenAmount, self.overlap,
                                            dotSpread=PREVIEW_DOT_SPREAD,
                                            startPoint=Point(0, 0),
                                            halfsies=self.halfsies,
                                            preview=False),
                                    

            if drawLines is not None:
                # print('len of drawlines =', len(drawLines))
                for i in drawLines:
                    i.draw(self.previewSurface)

            # for l in self.pattern.getPatternAtLoc(patternStartingPoint, halfsies=self.halfsies):
                # l.draw(self.previewSurface)
        # if self.drawSurface is not None:
        #     self.drawSurface.blit(self.previewSurface, (self.previewEdgeOffset * 3, self.previewStartY))

    def handleEvent(self, event):
        if self.includeHalfsiesCheckbox.handleEvent(event):
            self.halfsies = not self.halfsies
            self.updatePreviewSurface()

        tmp = self.xOverlapSlider.handleEvent(event)
        if tmp is not None:
            self.overlap[0] = tmp
            self.updatePreviewSurface()

        tmp2 = self.yOverlapSlider.handleEvent(event)
        if tmp2 is not None:
            self.overlap[1] = tmp2
            self.updatePreviewSurface()
        
        if self.createPatternButton.handleEvent(event):
            # TODO Do cool stuff here (pass the pattern back to Game)
            self.allowPassing = True

            # self.open = False
            # self.updatePreviewSurface()

    def draw(self, surface):
        # if self.drawSurface is None:
        #     self.drawSurface = surface
        #     self.updatePreviewSurface()
        surface.blit(self.previewSurface, (self.previewEdgeOffset * 3, self.previewStartY))
        # pass
        # print(f'length of pattern = {len(self.pattern.lines)}')
        # self.updatePreviewSurface()
        # self.text.draw(surface)
        # self.includeHalfsiesCheckbox.draw(surface)
        # self.xOverlapSlider.draw(surface)
        # self.yOverlapSlider.draw(surface)
        # self.createPatternButton.draw(surface)
        # surface.blit(self.previewSurface, (self.previewEdgeOffset * 3, self.previewStartY))

    def updateContextData(self, context):
        if self.pattern != context:
            self.pattern = context
            self.gameDotSpread = context.dotSpread

            #* Generate new sliders with the proper ranges
            s = self.pattern.getSize(1)

            if self.xOverlapSlider is not None and self.yOverlapSlider is not None:
                self.xOverlapSlider.slider.kill()
                self.yOverlapSlider.slider.kill()
            #                If you want slider values to persist between openings, change this to self.overlap[0/1]    \|/
            self.xOverlapSlider = Slider(self.xOverlapSliderPos, self.uiManager, self.container, 'x Overlap', startValue=0, range=(-s[0] + 1, s[0]))
            self.yOverlapSlider = Slider(self.yOverlapSliderPos, self.uiManager, self.container, 'y Overlap', startValue=0, range=(-s[1] + 1, s[1]))

            self.allowPassing = False
            self.updatePreviewSurface()

    def passDataBack(self):
        if self.allowPassing:
            self.pattern.halfsies = self.halfsies
            self.pattern.overlap  = self.overlap
            return self.pattern
        else:
            return None

class OptionMenu:
    def __init__(self, uiManager, container):
        self.size = container.get_size()
        self.uiManager = uiManager
        self.allowPassing = False

        with open(DIR + 'settings.json', 'r') as f:
            self.settings = json.load(f)

        row = self.size[1] / 20
        rowSpacing = 2.5
        currentRow = .9
        centerx = (self.size[0] / 2) - 15 # 15 for the scroll bar
        xpos = 20

        self.textPos              = [xpos, row * currentRow]; currentRow += rowSpacing; currentRow += .1
        self.dotSpreadPos         = [xpos, row * currentRow]; currentRow += rowSpacing
        self.dragDelayPos         = [xpos, row * currentRow]; currentRow += rowSpacing
        self.fpsPos               = [xpos, row * currentRow]; currentRow += rowSpacing
        self.keyRepeatDelayPos    = [xpos, row * currentRow]; currentRow += rowSpacing
        self.keyRepeatIntervalPos = [xpos, row * currentRow]; currentRow += rowSpacing
        self.offScreenAmountPos   = [xpos, row * currentRow]; currentRow += rowSpacing
        self.savesFileLocPos      = [xpos, row * currentRow]; currentRow += rowSpacing
        self.imageSavesFileLocPos = [xpos, row * currentRow]; currentRow += rowSpacing
        # self.cancelButtonPos      = [centerx - 80, row * currentRow] 
        self.acceptButtonPos      = [centerx - 55, row * currentRow]

        self.text              = Text([*self.textPos],                  uiManager, container, 'Options')
        self.dotSpread         = InputBox([*self.dotSpreadPos],         uiManager, container, 'Dot Spread',                  str(self.settings['dotSpread']),         numbersOnly=True)
        self.dragDelay         = InputBox([*self.dragDelayPos],         uiManager, container, 'Drag Delay',                  str(self.settings['dragDelay']),         numbersOnly=True)
        self.fps               = InputBox([*self.fpsPos],               uiManager, container, 'FPS',                         str(self.settings['FPS']),               numbersOnly=True)
        self.keyRepeatDelay    = InputBox([*self.keyRepeatDelayPos],    uiManager, container, 'Key Repeat Delay',            str(self.settings['keyRepeatDelay']),    numbersOnly=True)
        self.keyRepeatInterval = InputBox([*self.keyRepeatIntervalPos], uiManager, container, 'Key Repeat Interval',         str(self.settings['keyRepeatInterval']), numbersOnly=True)
        self.offScreenAmount   = InputBox([*self.offScreenAmountPos],   uiManager, container, 'Off-Screen Amount',           str(self.settings['offScreenAmount']),   numbersOnly=True)
        self.savesFileLoc      = InputBox([*self.savesFileLocPos],      uiManager, container, 'Default Save Location',       str(self.settings['saveLoc']),           disallowedChars='forbidden_file_path', size=[self.size[0] - (xpos * 2) - 15, None])
        self.imageSavesFileLoc = InputBox([*self.imageSavesFileLocPos], uiManager, container, 'Default Image Save Location', str(self.settings['imageSaveLoc']),      disallowedChars='forbidden_file_path', size=[self.size[0] - (xpos * 2) - 15, None])
        self.acceptButton      = Button([*self.acceptButtonPos],        uiManager, container, 'Accept & Save', self.saveSettings)
        # self.cancelButton      = Button([*self.cancelButtonPos],        uiManager, container, 'Cancel', self.closeWindow, size=[self.acceptButton.size[0], None])
        
        self.verticalPercentage = self.size[1] / (self.acceptButtonPos[1] + self.acceptButton.size[1] + 20)

        self.scrollBar = ScrollBar(uiManager, container, self.verticalPercentage)

    def closeWindow(self):
        downEventData = {'unicode': 'o',
                         'key': 111,
                         'mod': 0,
                         'window': None
                         }

        upEventData = {'key': 111,
                       'mod': 0,
                       'scancode': 32,
                       'window': None
                       }

        pygame.event.post(pygame.event.Event(pygame.KEYDOWN, downEventData))
        pygame.event.post(pygame.event.Event(pygame.KEYUP,   upEventData))

    def saveSettings(self):
        print('Saving Settings')
        self.allowPassing = True
        self.settings['dotSpread']         = self.dotSpread.getInput()
        self.settings['dragDelay']         = self.dragDelay.getInput()
        self.settings['FPS']               = self.fps.getInput()
        self.settings['keyRepeatDelay']    = self.keyRepeatDelay.getInput()
        self.settings['keyRepeatInterval'] = self.keyRepeatInterval.getInput()
        self.settings['offScreenAmount']   = self.offScreenAmount.getInput()
        self.settings['savesLoc']          = self.savesFileLoc.getInput()
        self.settings['imageSavesLoc']     = self.imageSavesFileLoc.getInput()

    def handleEvent(self, event):
        self.dotSpread.handleEvent(event)
        self.dragDelay.handleEvent(event)
        self.fps.handleEvent(event)
        self.keyRepeatDelay.handleEvent(event)
        self.keyRepeatInterval.handleEvent(event)
        self.offScreenAmount.handleEvent(event)
        self.savesFileLoc.handleEvent(event)
        self.imageSavesFileLoc.handleEvent(event)
        # self.cancelButton.handleEvent(event)
        self.acceptButton.handleEvent(event)
        if self.scrollBar.handleEvent(event):
            self.text.setPos(              [None, (self.scrollBar.getPos() * -self.size[1]) + self.textPos[1]])
            self.dotSpread.setPos(         [None, (self.scrollBar.getPos() * -self.size[1]) + self.dotSpreadPos[1]])
            self.dragDelay.setPos(         [None, (self.scrollBar.getPos() * -self.size[1]) + self.dragDelayPos[1]])
            self.fps.setPos(               [None, (self.scrollBar.getPos() * -self.size[1]) + self.fpsPos[1]])
            self.keyRepeatDelay.setPos(    [None, (self.scrollBar.getPos() * -self.size[1]) + self.keyRepeatDelayPos[1]])
            self.keyRepeatInterval.setPos( [None, (self.scrollBar.getPos() * -self.size[1]) + self.keyRepeatIntervalPos[1]])
            self.offScreenAmount.setPos(   [None, (self.scrollBar.getPos() * -self.size[1]) + self.offScreenAmountPos[1]])
            self.savesFileLoc.setPos(      [None, (self.scrollBar.getPos() * -self.size[1]) + self.savesFileLocPos[1]])
            self.imageSavesFileLoc.setPos( [None, (self.scrollBar.getPos() * -self.size[1]) + self.imageSavesFileLocPos[1]])
            # self.cancelButton.setPos(      [None, (self.scrollBar.getPos() * -self.size[1]) + self.cancelButtonPos[1]])
            self.acceptButton.setPos(      [None, (self.scrollBar.getPos() * -self.size[1]) + self.acceptButtonPos[1]])

    def draw(self, surface):
        pass

    def updateContextData(self, context):
        if self.settings != context and not self.allowPassing:
            self.settings = context

    def passDataBack(self):
        if self.allowPassing:
            self.allowPassing = False
            return self.settings
        else:
            return None

class ControlsMenu:
    def __init__(self, uiManager, container):
        self.size = container.get_size()
        self.uiManager = uiManager

        # Make a background surface for the gui
        self.background = pygame.Surface(self.size)
        self.background = self.background.convert()
        self.background.fill((0, 0, 0))

        
        self.helloButton = Button([None, None], self.uiManager, container, 'Hello World!', print, ['Hello World!'], size=[100, None])

    def handleEvent(self, event):
        self.helloButton.handleEvent(event)

    def draw(self, surface):
        self.text.draw(surface)
        self.helloButton.draw(surface)

    def updateContextData(self, context):
         pass

class SaveMenu:
    def __init__(self, uiManager, container):
        self.size = container.get_size()
        self.uiManager = uiManager

        # Make a background surface for the gui
        self.background = pygame.Surface(self.size)
        self.background = self.background.convert()
        self.background.fill((0, 0, 0))

        
        self.helloButton = Button([None, None], self.uiManager, container, 'Hello World!', print, ['Hello World!'], size=[100, None])

    def handleEvent(self, event):
        self.helloButton.handleEvent(event)

    def draw(self, surface):
        self.text.draw(surface)
        self.helloButton.draw(surface)

    def updateContextData(self, context):
         pass

class OpenMenu:
    def __init__(self, uiManager, container):
        self.size = container.get_size()
        self.uiManager = uiManager

        # Make a background surface for the gui
        self.background = pygame.Surface(self.size)
        self.background = self.background.convert()
        self.background.fill((0, 0, 0))

        
        self.helloButton = Button([None, None], self.uiManager, container, 'Hello World!', print, ['Hello World!'], size=[100, None])

    def handleEvent(self, event):
        self.helloButton.handleEvent(event)
    
    def draw(self, surface):
        self.text.draw(surface)
        self.helloButton.draw(surface)

    def updateContextData(self, context):
        pass

class ExportMenu:
    def __init__(self, uiManager, container):
        self.size = container.get_size()
        self.uiManager = uiManager

        # Make a background surface for the gui
        self.background = pygame.Surface(self.size)
        self.background = self.background.convert()
        self.background.fill((0, 0, 0))

        
        self.helloButton = Button([None, None], self.uiManager, container, 'Hello World!', print, ['Hello World!'], size=[100, None])

    def handleEvent(self, event):
        self.helloButton.handleEvent(event)

    def draw(self, surface):
        self.text.draw(surface)
        self.helloButton.draw(surface)

    def updateContextData(self, context):
         pass

class WelcomeMenu:
    def __init__(self, uiManager, container):
        self.size = container.get_size()
        self.uiManager = uiManager

        # Make a background surface for the gui
        self.background = pygame.Surface(self.size)
        self.background = self.background.convert()
        self.background.fill((0, 0, 0))

        
        self.helloButton = Button([None, None], self.uiManager, container, 'Hello World!', print, ['Hello World!'], size=[100, None])

    def handleEvent(self, event):
        self.helloButton.handleEvent(event)

    def draw(self, surface):
        self.text.draw(surface)
        self.helloButton.draw(surface)

    def updateContextData(self, context):
         pass

# TODO Phase out all of the self.width and self.heights in favor of sizes
# TODO make all of these more alive
# TODO cast all the 2 item list params to lists in case we pass in a tuple
# All the different elements the GUIs can have. They're essentially my own wrappers for pygame_gui's UIElements,
#   because they're poorly written (or at least, hard to interface with).
#   HandleEvent()'s return True is something happened, and false if not (value and None in the case of Slider)
class Button:
    def __init__(self, pos, uiManager, container, text, func, params=None, label=None, size=[None, None]):
        if size[0] is None:
            self.width = len(text) * 10
        else:
            self.width  = size[0]
        if size[1] is None:
            self.height = 30
        else:
            self.height = size[1]

        if pos[0] is None:
            pos[0] = (container.get_size()[0] / 2) - (self.width / 2)
        if pos[1] is None:
            pos[1] = (container.get_size()[1] / 2) - (self.height / 2)

        self.uiManager = uiManager
        self.pos       = pos
        self.size      = [self.width, self.height]
        self.func      = func
        self.params    = params

        labelPos = [pos[0] - (self.width / 2), pos[1] - self.height]

        self.button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect(pos, (self.width, self.height)), text=text, manager=self.uiManager, container=container)
        
        if label is not None:
            self.label = Text(labelPos, uiManager, container, label)
        else:
            self.label = None

    def handleEvent(self, event):
        if event.type == pygame.USEREVENT and \
           event.user_type == pygame_gui.UI_BUTTON_PRESSED and \
           event.ui_element == self.button:

            if self.params is not None:
                self.func(*self.params)
            else:
                self.func()
            return True
        else:
            return False
        
    def draw(self, surface):
        pass

    def move(self, deltaLoc=[None, None]):
        if deltaLoc[0] is not None:
            self.pos[0] += deltaLoc[0]
            self.button.set_relative_position(self.pos)
        if deltaLoc[1] is not None:
            self.pos[1] += deltaLoc[1]
            self.button.set_relative_position(self.pos)

        if self.label is not None:
            self.label.move(deltaLoc)

    def setPos(self, loc=[None, None]):
        deltaLoc = [*loc]
        if loc[0] is not None:
            deltaLoc[0] = loc[0] - self.pos[0]
            self.pos[0] = loc[0]
            self.button.set_relative_position(self.pos)
        if loc[1] is not None:
            deltaLoc[1] = loc[1] - self.pos[1]
            self.pos[1] = loc[1]
            self.button.set_relative_position(self.pos)

        if self.label is not None:
            self.label.move(deltaLoc)

class RenderedText:
    def __init__(self, text, container, pos=[None, None], font=None, size=24):
        if font is None:
            self.font = pygame.font.Font(None, size)
        else:
            self.font = font

        self.text = text
        self.textSurface = self.font.render(self.text, True, pygame.Color(200, 200, 200))

        if pos[0] is None:
            pos[0] = (container.get_size()[0] / 2) - (self.textSurface.get_rect().width / 2)
        if pos[1] is None:
            pos[1] = (container.get_size()[1] / 2) - (self.textSurface.get_rect().height / 2)

        self.pos = pos
        
    def getSize(self):
        return self.textSurface.get_rect()

    def draw(self, surface):
        # print(f'Drawing "{self.text}" at {self.pos}')
        surface.blit(self.textSurface, self.pos)
        # surface.blit(self.textSurface, self.pos)

class ColorPicker:
    def __init__(self, uiManager, initalColor):
        self.uiManager = uiManager
        # self.initalColor = initalColor
        self.color = None
        self.colorPicker = UIColourPickerDialog(pygame.Rect(160, 50, 420, 400), self.uiManager, window_title='Change Color...', initial_colour=initalColor)
    
    def handleEvent(self, event):
        if event.type == pygame.USEREVENT and event.user_type == pygame_gui.UI_COLOUR_PICKER_COLOUR_PICKED:
            self.color = event.colour
            # self.picked_colour_surface.fill(self.current_colour)

        if event.type == pygame.USEREVENT and event.user_type == pygame_gui.UI_WINDOW_CLOSE and event.ui_element == self.colorPicker:
            # self.pick_colour_button.enable()
            # self.colour_picker = None
            self.colorPicker.disable()
            self.colorPicker.hide()
            self.colorPicker.set_blocking(True)

        # self.pick_colour_button = UIButton(relative_rect=pygame.Rect(-180, -60, 150, 30),
        #                                    text='Pick Colour',
        #                                    manager=self.ui_manager,
        #                                    anchors={'left': 'right',
        #                                             'right': 'right',
        #                                             'top': 'bottom',
        #                                             'bottom': 'bottom'})

class CheckBox:
    def __init__(self, pos, uiManager, container, label, startValue=False, size=[None, None], hoverText=''):
        if size[0] is None:
            self.width  = 25
        else:
            self.width  = size[0]
        if size[1] is None:
            self.height = 25
        else:
            self.height = size[1]

        if pos[0] is None:
            pos[0] = (container.get_size()[0] / 2) - ((self.width + 5) / 2) - (4.5 * len(label))
        if pos[1] is None:
            pos[1] = (container.get_size()[1] / 2) - (self.height / 2)

        self.uiManager = uiManager
        self.pos = pos

        labelPos = [pos[0] + self.width + 5, pos[1] + (self.height / 2) - ((self.height - 3) / 4)]

        self.label = Text(labelPos, uiManager, container, label)

        self.checked = startValue

        self.button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect(pos, (self.width, self.height)), text=' ',
                                                   manager=self.uiManager, container=container, tool_tip_text=hoverText, allow_double_clicks=False)

    def handleEvent(self, event):
        if event.type == pygame.USEREVENT and \
           event.user_type == pygame_gui.UI_BUTTON_PRESSED and \
           event.ui_element == self.button:
           
            self.checked = not self.checked

            if self.checked:
                self.button.set_text('✓')
            else:
                self.button.set_text(' ')
            return True
        else:
            return False

    def draw(self, surface):
        # self.label.draw(surface)
        pass

    def move(self, deltaLoc=[None, None]):
        if deltaLoc[0] is not None:
            self.pos[0] += deltaLoc[0]
            self.button.set_relative_position(self.pos)
        if deltaLoc[1] is not None:
            self.pos[1] += deltaLoc[1]
            self.button.set_relative_position(self.pos)

        self.label.move(deltaLoc)

    def setPos(self, loc=[None, None]):
        deltaLoc = [*loc]
        if loc[0] is not None:
            deltaLoc[0] = loc[0] - self.pos[0]
            self.pos[0] = loc[0]
            self.button.set_relative_position(self.pos)
        if loc[1] is not None:
            deltaLoc[1] = loc[1] - self.pos[1]
            self.pos[1] = loc[1]
            self.button.set_relative_position(self.pos)

        self.label.move(deltaLoc)

class Slider:
    def __init__(self, pos, uiManager, container, label, range=(-10, 10), startValue = 0, size=[None, None]):
        if size[0] is None:
            self.width  = 200
        else:
            self.width  = size[0]
        if size[1] is None:
            self.height = 25
        else:
            self.height = size[1]

        if pos[0] is None:
            pos[0] = (container.get_size()[0] / 2) - (self.width / 2)
        if pos[1] is None:
            pos[1] = (container.get_size()[1] / 2) - (self.height / 2)

        self.uiManager = uiManager
        self.pos   = pos
        self.value = startValue

        textPos = [self.pos[0], self.pos[1] - (self.height / 2) - 5]
        valueLabelPos = [self.pos[0] - 20, self.pos[1] + (self.height / 4) - 1]

        self.label = Text(textPos, uiManager, container, label)
        self.valueLabel = Text(valueLabelPos, uiManager, container, str(self.value), size=[16, 12])

        self.container = container
        self.range = range
        
        self.slider = UIHorizontalSlider(relative_rect=pygame.Rect(pos, (self.width, self.height)), start_value=startValue, value_range=self.range, manager=uiManager, container=container)

    def handleEvent(self, event):
        if event.type == pygame.USEREVENT and \
           event.user_type == pygame_gui.UI_HORIZONTAL_SLIDER_MOVED and \
           event.ui_element == self.slider:

            self.value = event.value
            self.slider.set_current_value(self.value)
            self.valueLabel.text.set_text(str(self.value))
            return self.value


        elif event.type == pygame.USEREVENT and \
             event.user_type == 'ui_button_pressed' and \
             event.ui_element == self.slider.left_button:
                
            if self.value > self.range[0]:
                self.value -= 1
            self.slider.set_current_value(self.value)
            self.valueLabel.text.set_text(str(self.value))
            return self.value


        elif event.type == pygame.USEREVENT and \
             event.user_type == 'ui_button_pressed' and \
             event.ui_element == self.slider.right_button:
                
            if self.value < self.range[1]:
                self.value += 1
            self.slider.set_current_value(self.value)
            self.valueLabel.text.set_text(str(self.value))
            return self.value


        else:
            return None

    def draw(self, surface):
        pass
    
    def move(self, deltaLoc=[None, None]):
        if deltaLoc[0] is not None:
            self.pos[0] += deltaLoc[0]
            self.slider.set_relative_position(self.pos)
        if deltaLoc[1] is not None:
            self.pos[1] += deltaLoc[1]
            self.slider.set_relative_position(self.pos)

        self.label.move(deltaLoc)

    def setPos(self, loc=[None, None]):
        deltaLoc = [*loc]
        if loc[0] is not None:
            deltaLoc[0] = loc[0] - self.pos[0]
            self.pos[0] = loc[0]
            self.slider.set_relative_position(self.pos)
        if loc[1] is not None:
            deltaLoc[1] = loc[1] - self.pos[1]
            self.pos[1] = loc[1]
            self.slider.set_relative_position(self.pos)

        self.label.move(deltaLoc)

class Text:
    def __init__(self, pos, uiManager, container, text, size=[None, None]):
        if size[0] is None:
            size[0] = 1000
        if size[1] is None:
            size[1] = 1000

        if pos[0] is None:
            pos[0] = (container.get_size()[0] / 2) - (size[0] / 2)
        if pos[1] is None:
            pos[1] = (container.get_size()[1] / 2) - (size[1] / 2)

        self.pos = pos

        self.text = UILabel(pygame.Rect(pos, size), text, uiManager, container)

        self.size = self.text.font.size(text)
        self.text.set_dimensions(self.size)

    def move(self, deltaLoc=[None, None]):
        if deltaLoc[0] is not None:
            self.pos[0] += deltaLoc[0]
            self.text.set_relative_position(self.pos)
        if deltaLoc[1] is not None:
            self.pos[1] += deltaLoc[1]
            self.text.set_relative_position(self.pos)

    def setPos(self, loc=[None, None]):
        if loc[0] is not None:
            self.pos[0] = loc[0]
            self.text.set_relative_position(self.pos)
        if loc[1] is not None:
            self.pos[1] = loc[1]
            self.text.set_relative_position(self.pos)

class InputBox:
    def __init__(self, pos, uiManager, container, label, startingText='', numbersOnly=False,
                 textLengthLimit=None, allowedChars=None, disallowedChars=None, size=[None, None]):
        if size[0] is None:
            size[0] = 70
        if size[1] is None:
            size[1] = 30

        if pos[0] is None:
            pos[0] = (container.get_size()[0] / 2) - (size[0] / 2)
        if pos[1] is None:
            pos[1] = (container.get_size()[1] / 2) - (size[1] / 2)

        self.uiManager = uiManager
        self.pos  = pos
        self.size = size

        textPos = [pos[0], pos[1] - (size[1] / 2)]
        self.label = Text(textPos, uiManager, container, label)

        self.textEntry = pygame_gui.elements.UITextEntryLine(pygame.Rect(pos, size), self.uiManager, container)

        self.textEntry.set_text(startingText)

        self.numbersOnly = numbersOnly

        if numbersOnly:
            if textLengthLimit is None:
                textLengthLimit = 3
            if allowedChars is None:
                allowedChars = 'numbers'

        if textLengthLimit is not None:
            self.textEntry.set_text_length_limit(textLengthLimit)

        if allowedChars is not None:
            self.textEntry.set_allowed_characters(allowedChars)

        if disallowedChars is not None:
            self.textEntry.set_forbidden_characters(disallowedChars)

    def getInput(self):
        return int(self.textEntry.get_text()) if self.numbersOnly else self.textEntry.get_text()

    def handleEvent(self, event):
        # if event.type == pygame.USEREVENT and \
        #    event.user_type == pygame_gui.UI_BUTTON_PRESSED and \
        #    event.ui_element == self.button:

        #     self.func(*self.params)
        #     return True
        # else:
        #     return False
        pass

    def draw(self, surface):
        pass

    def move(self, deltaLoc=[None, None]):
        if deltaLoc[0] is not None:
            self.pos[0] += deltaLoc[0]
            self.textEntry.set_relative_position(self.pos)
        if deltaLoc[1] is not None:
            self.pos[1] += deltaLoc[1]
            self.textEntry.set_relative_position(self.pos)

        self.label.move(deltaLoc)

    def setPos(self, loc=[None, None]):
        deltaLoc = [*loc]
        if loc[0] is not None:
            deltaLoc[0] = loc[0] - self.pos[0]
            self.pos[0] = loc[0]
            self.textEntry.set_relative_position(self.pos)
        if loc[1] is not None:
            deltaLoc[1] = loc[1] - self.pos[1]
            self.pos[1] = loc[1]
            self.textEntry.set_relative_position(self.pos)

        self.label.move(deltaLoc)

class ScrollBar:
    def __init__(self, uiManager, container, verticalPercentage, pos=[None, None], size=[None, None]):
        if size[0] is None:
            size[0] = 16
        if size[1] is None:
            size[1] = container.get_size()[1]

        if pos[0] is None:
            pos[0] = container.get_size()[0] - size[0]
        if pos[1] is None:
            pos[1] = 0

        self.pos = pos
        self.percentage = verticalPercentage

        self.bar = pygame_gui.elements.UIVerticalScrollBar(pygame.Rect(pos, size), verticalPercentage, uiManager, container)
        # self.bar.show()
        # self.bar.enable()

    def handleEvent(self, event):
        # print(self.bar.start_percentage)
        tmp = self.bar.process_event(event)
        if tmp or self.bar.check_has_moved_recently():
            return True
        else:
            return False
        # if event.type == pygame.USEREVENT and \
        #    event.user_type == pygame_gui.UI_BUTTON_PRESSED and \
        #    event.ui_element == self.button:

        #     self.func(*self.params)
        #     return True
        # else:
        #     return False
        pass

    def draw(self, surface):
        # print('Scroll bar is at:', self.bar.start_percentage)
        pass

    def getPos(self):
        return self.bar.start_percentage

    def move(self, deltaLoc=[None, None]):
        if deltaLoc[0] is not None:
            self.pos[0] += deltaLoc[0]
            self.bar.set_relative_position(self.pos)
        if deltaLoc[1] is not None:
            self.pos[1] += deltaLoc[1]
            self.bar.set_relative_position(self.pos)

    def setPos(self, loc=[None, None]):
        if loc[0] is not None:
            self.pos[0] = loc[0]
            self.bar.set_relative_position(self.pos)
        if loc[1] is not None:
            self.pos[1] = loc[1]
            self.bar.set_relative_position(self.pos)



# menu.OPTION
#************** Options: ***********************#
# Focus color: Color picker
# dot spread: number input box, with text showing presets
# drag delay: number input box
# FPS: number input box
# key repeat delay: number input box
# key repeat interval: number input box
#// saves file: file dialog
#// image save file: file dialog
# background color: color picker

# Welcome
#************** Options: ***********************#
# Welcome text
# start button
# options menu button

# Controls
#************** Options: ***********************#
# Figure this out.

# Toolbar
#************** Options: ***********************#
# colored buttons changing the draw color

# Repeat
#************** Options: ***********************#
# include lines with one end outside the bounding box: checkbox
# how far apart the connecting patterns should be, 1 for x and one for y: slider, -pattern width/height - +pattern width/height
# preview Surface

# Save
#************** Options: ***********************#
# file dialog
# file extensions: drop down menu
# file name: text box

# Open
#************** Options: ***********************#
# file dialog
# file name: text box

# Export
#************** Options: ***********************#
# file dialog
# file name: text box



###################################################################################################
