from Color import Color, namedColor
from Point import Point
from Geometry import *
# from Globals import *
import os, json
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame, pygame_gui
from enum import Enum, auto
# Buttons
from pygame_gui.elements import *
# Color picker
from pygame_gui.windows import UIColourPickerDialog
# File Dialog
from pygame_gui.windows import UIFileDialog
from pygame_gui.core.utility import create_resource_path

from pygame_gui.ui_manager import UIManager
from pygame_gui.elements.ui_window import UIWindow
from pygame_gui.elements.ui_image import UIImage

DIR = os.path.dirname(__file__) + '/'
SAVES_FOLDER = DIR + 'saves/'
GUI_THEME_FILE = DIR + 'data/myTheme.json'

# ARROW = '→'

with open(DIR + 'settings.json') as f:
    SETTINGS = json.load(f)

#TODO 
# create_tool_tip(text: str, position: Tuple[int, int], hover_distance: Tuple[int, int]) → pygame_gui.core.interfaces.tool_tip_interface.IUITooltipInterface
# This would be cool to add

# All the different types of classes we have
class menu(Enum):
    OPTION   = 0
    WELCOME  = 1
    CONTROLS = 2
    TOOLBAR  = 3
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

        self.repeatWindow   = Window([None, None], self.uiManager, 'Repeat Pattern' , '#repeat_window',   RepeatMenu,   (self.width / 1.25, self.height / 1.25))
        self.optionWindow   = Window([None, None], self.uiManager, 'Options'        , '#options_window',  OptionMenu,   (500, 400))
        self.saveWindow     = Window([None, None], self.uiManager, 'Save Pattern'   , '#save_window',     SaveMenu,     (500, 400))
        self.openWindow     = Window([None, None], self.uiManager, 'Open Pattern'   , '#open_window',     OpenMenu,     (500, 400))
        self.exportWindow   = Window([None, None], self.uiManager, 'Export Pattern' , '#export_window',   ExportMenu,   (500, 400))
        self.controlsWindow = Window([None, None], self.uiManager, 'Edit Controls'  , '#controls_window', ControlsMenu, (500, 400))
        self.welcomeWindow  = Window([0, 0],       self.uiManager, 'Welcome!'       , '#welcome_window',  WelcomeMenu,  (self.width - 10, self.height - 10))
        # self.toolbarWindow  = Window((50, 50),     self.uiManager, ''       , '#options_window', OptionsMenu, (500, 400))

    def run(self, event, type=None):
        if type is not None:
            self.getWindow(type)
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

        # if not (event.type == pygame.USEREVENT and event.user_type == pygame_gui.UI_WINDOW_CLOSE):
        self.uiManager.process_events(event)

        if event.type == pygame.USEREVENT and event.user_type == pygame_gui.UI_WINDOW_CLOSE:
            self.hasHacked = False
            return False # Tells Game that the window is now closed
        else:
            return True

    def hackActivateWindow(self):
        # pygame.mouse.set_pos(self.width / 2, self.height / 2)

        eventData = {'pos': (self.width / 2, self.height / 2),
                     'button': 1,
                     'window': None
                    }

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
            self.hackActivateWindow()
            self.hasHacked = True

        others = list(menu)
        others.remove(activate)
        others.remove(menu.TOOLBAR)
        for i in others:
            self.getWindow(i).set_blocking(True)
            self.getWindow(i).disable()
            self.getWindow(i).hide()

        # Get Game to talk to the induvidual GUIs
        self.getWindow(activate).updateContextData(context)

        self.uiManager.update(deltaTime)
        self.uiManager.draw_ui(self.rootWindowSurface)


# All the different GUI classes
PREVIEW_BACKGROUND_COLOR = [200, 160, 100]
# PREVIEW_EDGE_OFFSET = 50
PREVIEW_DOT_SPREAD = 16
class RepeatMenu:
    def __init__(self, uiManager, container):
        self.size = container.get_size()
        self.uiManager = uiManager
        self.pattern = None

        # Make a background surface for the gui
        self.background = pygame.Surface(self.size)
        self.background = self.background.convert()
        self.background.fill((30, 30, 30))

        self.halfsies = False
        self.overlap = [0, 0]

        row = self.size[1] / 20
        textPos                    = [None,                     row]
        includeHalfsiesCheckboxPos = [(self.size[0] / 2) - 100, row * 2.5]
        xOverlapSliderPos          = [(self.size[0] / 2) - 205, row * 6]
        yOverlapSliderPos          = [(self.size[0] / 2) + 25,  row * 6]
        createPatternButtonPos     = [None,                     row * 8.5]
        self.previewEdgeOffset     = self.size[1] / 20

        self.text = Text('Repeat Menu!', container, textPos)
        self.includeHalfsiesCheckbox = CheckBox(includeHalfsiesCheckboxPos, self.uiManager, container, 'Include Halfsies', startValue=self.halfsies)
        self.xOverlapSlider = Slider(xOverlapSliderPos, uiManager, container, 'x Overlap', startValue=self.overlap[0], range=(-2, 2))
        self.yOverlapSlider = Slider(yOverlapSliderPos, uiManager, container, 'y Overlap', startValue=self.overlap[1], range=(-2, 2))
        self.createPatternButton = Button(createPatternButtonPos, self.uiManager, container, 'Create!', print, ['Creating Pattern...'], [100, None])
        self.previewStartY = (row * 8.5) + self.previewEdgeOffset + self.createPatternButton.height

        self.previewDots = self.genDotArray()
        self.previewSurface = pygame.Surface(((self.size[0] - self.previewEdgeOffset * 6), 
                                               self.size[1] - self.previewStartY - self.previewEdgeOffset))
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
            drawLines = scaleLines(repeatPattern(self.pattern, self.size, PREVIEW_DOT_SPREAD, self.previewDots[0],
                                                 SETTINGS['offScreenAmount'], self.overlap, self.halfsies),
                                   SETTINGS['dotSpread'], PREVIEW_DOT_SPREAD)

            if drawLines is not None:
                # print('len of drawlines =', len(drawLines))
                for i in drawLines:
                    i.draw(self.previewSurface)

            # for l in self.pattern.getPatternAtLoc(patternStartingPoint, halfsies=self.halfsies):
                # l.draw(self.previewSurface)

    def genDotArray(self):
        dots = []
        for x in range(int((self.size[0] + (SETTINGS['offScreenAmount'] * 2)) / PREVIEW_DOT_SPREAD)):
            for y in range(int((self.size[1] + (SETTINGS['offScreenAmount'] * 2)) / PREVIEW_DOT_SPREAD)):
                dots.append(Point((x * PREVIEW_DOT_SPREAD) + 4 - SETTINGS['offScreenAmount'], (y * PREVIEW_DOT_SPREAD) + 4 - SETTINGS['offScreenAmount']))
                # dots.append(Point((x * PREVIEW_DOT_SPREAD)+ startingPoint.x - SETTINGS['offScreenAmount'], (y * PREVIEW_DOT_SPREAD) + startingPoint.y - SETTINGS['offScreenAmount']))
        return dots

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
            self.open = False
            self.updatePreviewSurface()

    def draw(self, surface):
        # print(f'length of pattern = {len(self.pattern.lines)}')
        # self.updatePreviewSurface()
        self.text.draw(surface)
        self.includeHalfsiesCheckbox.draw(surface)
        self.xOverlapSlider.draw(surface)
        self.yOverlapSlider.draw(surface)
        self.createPatternButton.draw(surface)
        surface.blit(self.previewSurface, (self.previewEdgeOffset * 3, self.previewStartY))

    def updateContextData(self, context):
        # Only update from Game once
        if self.pattern is None:
            # print(f'pattern = {self.pattern}')
            self.pattern = context
            self.updatePreviewSurface()

class OptionMenu:
    def __init__(self, uiManager, container):
        self.size = container.get_size()
        self.uiManager = uiManager

        # Make a background surface for the gui
        self.background = pygame.Surface(self.size)
        self.background = self.background.convert()
        self.background.fill((0, 0, 0))

        self.text = Text('Menu!', container)
        self.helloButton = Button([None, None], self.uiManager, container, 'Hello World!', print, ['Hello World!'], [100, None])

    def handleEvent(self, event):
        self.helloButton.handleEvent(event)

    def draw(self, surface):
        self.text.draw(surface)
        self.helloButton.draw(surface)

    def updateContextData(self, context):
         pass

class ControlsMenu:
    def __init__(self, uiManager, container):
        self.size = container.get_size()
        self.uiManager = uiManager

        # Make a background surface for the gui
        self.background = pygame.Surface(self.size)
        self.background = self.background.convert()
        self.background.fill((0, 0, 0))

        self.text = Text('Menu!', container)
        self.helloButton = Button([None, None], self.uiManager, container, 'Hello World!', print, ['Hello World!'], [100, None])

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

        self.text = Text('Menu!', container)
        self.helloButton = Button([None, None], self.uiManager, container, 'Hello World!', print, ['Hello World!'], [100, None])

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

        self.text = Text('Menu!', container)
        self.helloButton = Button([None, None], self.uiManager, container, 'Hello World!', print, ['Hello World!'], [100, None])

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

        self.text = Text('Menu!', container)
        self.helloButton = Button([None, None], self.uiManager, container, 'Hello World!', print, ['Hello World!'], [100, None])

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

        self.text = Text('Menu!', container)
        self.helloButton = Button([None, None], self.uiManager, container, 'Hello World!', print, ['Hello World!'], [100, None])

    def handleEvent(self, event):
        self.helloButton.handleEvent(event)

    def draw(self, surface):
        self.text.draw(surface)
        self.helloButton.draw(surface)

    def updateContextData(self, context):
         pass


# All the different elements the GUIs can have. They're essentially my own wrappers for pygame_gui's UIElements,
#   because they're poorly written (or at least, hard to interface with).
#   HandleEvent()'s return True is something happened, and false if not (value and None in the case of Slider)
class Button:
    def __init__(self, pos, uiManager, container, text, func, params = None, size=None):
        if size[0] is None:
            self.width  = 50
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
        self.pos    = pos
        self.func   = func
        self.params = params
        
        # self.rect = pygame.Rect((start_pos[0], start_pos[1]), (self.width, self.height))
        self.color = pygame.Color("#FFFFFF")

        self.button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect(pos, (self.width, self.height)), text=text, manager=self.uiManager, container=container)

    def handleEvent(self, event):
        if event.type == pygame.USEREVENT and \
           event.user_type == pygame_gui.UI_BUTTON_PRESSED and \
           event.ui_element == self.button:

            self.func(*self.params)
            return True
        else:
            return False
        
    def draw(self, surface):
        pass

class Text:
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
            pos[0] = (container.get_size()[0] / 2) - (self.width / 2)
        if pos[1] is None:
            pos[1] = (container.get_size()[1] / 2) - (self.height / 2)

        self.uiManager = uiManager
        self.pos   = pos

        textSize = self.height - 3
        # textPos = [0, 0]
        textPos = [pos[0] + self.width + 5, pos[1] + (self.height / 2) - (textSize / 4)]
        self.label = Text(label, container, textPos, size=textSize)
        # self.pos[0] -= (self.label.getSize()[0] / 2) + (self.width / 2)
        # self.label.pos = textPos

        self.checked = startValue

        self.button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect(pos, (self.width, self.height)), text=' ',
                                                   manager=self.uiManager, container=container, tool_tip_text=hoverText, allow_double_clicks=False)

    def handleEvent(self, event):
        if event.type == pygame.USEREVENT and \
           event.user_type == pygame_gui.UI_BUTTON_PRESSED and \
           event.ui_element == self.button:
           
            self.checked = not self.checked
            return True
        else:
            return False

    def draw(self, surface):
        self.label.draw(surface)
        if self.checked:
            self.button.set_text('✓')
        else:
            self.button.set_text(' ')

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
        self.label = Text(label, container, (self.pos[0], self.pos[1] - (self.height / 2) - 5))
        # self.valueLabel = Text(str(startValue), container, (self.pos[0] - 20, self.pos[1] + (self.height / 4) - 1))
        self.container = container
        
        self.slider = UIHorizontalSlider(relative_rect=pygame.Rect(pos, (self.width, self.height)), start_value=startValue, value_range=range, manager=uiManager, container=container)

    def handleEvent(self, event):
        if event.type == pygame.USEREVENT and \
           event.user_type == pygame_gui.UI_HORIZONTAL_SLIDER_MOVED and \
           event.ui_element == self.slider:

            return event.value
        else:
            return None

    def draw(self, surface):
        self.value = self.slider.get_current_value()
        # self.valueLabel.text = str(self.slider.get_current_value())
        Text(str(self.value), self.container, (self.pos[0] - 20, self.pos[1] + (self.height / 4) - 1)).draw(surface)
        # print(f'Slider is currently at {self.value}')

        # self.valueLabel.draw(surface)
        self.label.draw(surface)



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
