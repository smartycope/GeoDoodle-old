from Color import Color, namedColor
from Point import Point
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

ARROW = '→'

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
PREVIEW_EDGE_OFFSET = 50
PREVIEW_DOT_SPREAD = 16
class RepeatMenu:
    def __init__(self, uiManager, container):
        self.size = container.get_size()
        self.uiManager = uiManager

        # Make a background surface for the gui
        self.background = pygame.Surface(self.size)
        self.background = self.background.convert()
        self.background.fill((30, 30, 30))

        self.includeHalfsies = False
        self.overlap = 0

        textPos                    = [None, 20]
        includeHalfsiesCheckboxPos = [(self.size[0] / 2) - 100, 60]
        overlapSliderPos           = [None, 120]
        createPatternButtonPos     = [None, 170]

        self.text = Text('Repeat Menu!', container, textPos)
        self.includeHalfsiesCheckbox = CheckBox(includeHalfsiesCheckboxPos, self.uiManager, container, 'Include Halfsies', startValue=self.includeHalfsies)
        self.overlapSlider = Slider(overlapSliderPos, uiManager, container, 'Overlap', startValue=self.overlap)
        self.createPatternButton = Button(createPatternButtonPos, self.uiManager, container, 'Create!', print, ['Creating Pattern...'], [100, None])

        self.previewDots = self.genDotArray()
        self.previewSurface = pygame.Surface(((self.size[0] - PREVIEW_EDGE_OFFSET * 2), self.size[1] / 2))
        self.updatePreviewSurface()

    def updatePreviewSurface(self):
        self.previewSurface.fill(PREVIEW_BACKGROUND_COLOR)

        for i in self.previewDots:
            pygame.draw.rect(self.previewSurface, SETTINGS['dotColor'], pygame.Rect(i.data(), [SETTINGS['dotSize'], SETTINGS['dotSize']]))

    def genDotArray(self):
        dots = []
        for x in range(int((self.size[0] + (SETTINGS['offScreenAmount'] * 2)) / PREVIEW_DOT_SPREAD)):
            for y in range(int((self.size[1] + (SETTINGS['offScreenAmount'] * 2)) / PREVIEW_DOT_SPREAD)):
                dots.append(Point((x * PREVIEW_DOT_SPREAD) + 4 - SETTINGS['offScreenAmount'], (y * PREVIEW_DOT_SPREAD) + 4 - SETTINGS['offScreenAmount']))
                # dots.append(Point((x * PREVIEW_DOT_SPREAD)+ startingPoint.x - SETTINGS['offScreenAmount'], (y * PREVIEW_DOT_SPREAD) + startingPoint.y - SETTINGS['offScreenAmount']))
        return dots

    def handleEvent(self, event):
        self.includeHalfsiesCheckbox.handleEvent(event)
        self.overlapSlider.handleEvent(event)
        self.createPatternButton.handleEvent(event)

    def draw(self, surface):
        self.text.draw(surface)
        self.includeHalfsiesCheckbox.draw(surface)
        self.overlapSlider.draw(surface)
        self.createPatternButton.draw(surface)
        surface.blit(self.previewSurface, (PREVIEW_EDGE_OFFSET, (self.size[1] / 2) - PREVIEW_EDGE_OFFSET))

    def updateContextData(self, context):
        self.pattern = context['pattern']

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
        if event.type == pygame.USEREVENT:
            if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == self.button:
                    self.func(*self.params)
        
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
        if event.type == pygame.USEREVENT:
            if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == self.button:
                    self.checked = not self.checked

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
        pass
        # if event.type == pygame.USEREVENT:
        #     if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
        #         if event.ui_element == self.button:
        #             self.func(*self.params)

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



'''

class PongWindow(UIWindow):
    def __init__(self, position, ui_manager):
        super().__init__(pygame.Rect(position, (320, 240)), ui_manager,
                         window_display_title='Super Awesome Pong!',
                         object_id='#pong_window')

        game_surface_size = self.get_container().get_size()
        self.game_surface_element = UIImage(pygame.Rect((0, 0),
                                                        game_surface_size),
                                            pygame.Surface(game_surface_size).convert(),
                                            manager=ui_manager,
                                            container=self,
                                            parent_element=self)

        self.pong_game = PongGame(game_surface_size)

        self.is_active = False

    def process_event(self, event):
        handled = super().process_event(event)
        if (event.type == pygame.USEREVENT and
                event.user_type == pygame_gui.UI_BUTTON_PRESSED and
                event.ui_object_id == "#pong_window.#title_bar" and
                event.ui_element == self.title_bar):
            handled = True
            event_data = {'user_type': 'pong_window_selected',
                          'ui_element': self,
                          'ui_object_id': self.most_specific_combined_id}
            window_selected_event = pygame.event.Event(pygame.USEREVENT,
                                                       event_data)
            pygame.event.post(window_selected_event)
        if self.is_active:
            handled = self.pong_game.process_event(event)
        return handled

    def update(self, time_delta):
        if self.alive() and self.is_active:
            self.pong_game.update(time_delta)

        super().update(time_delta)

        self.pong_game.draw(self.game_surface_element.image)


class MiniGamesApp:
    def __init__(self):
        pygame.init()

        self.root_window_surface = pygame.display.set_mode((1024, 600))

        self.background_surface = pygame.Surface((1024, 600)).convert()
        self.background_surface.fill(pygame.Color('#505050'))
        self.ui_manager = UIManager((1024, 600), 'data/themes/theme_3.json')
        self.clock = pygame.time.Clock()
        self.is_running = True

        self.pong_window_1 = PongWindow((25, 25), self.ui_manager)
        self.pong_window_2 = PongWindow((50, 50), self.ui_manager)

    def run(self):
        while self.is_running:
            time_delta = self.clock.tick(60)/1000.0

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.is_running = False

                self.ui_manager.process_events(event)

                if event.type == pygame.USEREVENT and event.user_type == 'pong_window_selected':
                    event.ui_element.is_active = True
                    if event.ui_element == self.pong_window_1:
                        self.pong_window_2.is_active = False
                    elif event.ui_element == self.pong_window_2:
                        self.pong_window_1.is_active = False

            self.ui_manager.update(time_delta)

            self.root_window_surface.blit(self.background_surface, (0, 0))
            self.ui_manager.draw_ui(self.root_window_surface)

            pygame.display.update()


class ControlScheme:
    def __init__(self):
        self.up = pygame.K_UP
        self.down = pygame.K_DOWN


class PongGame:
    def __init__(self, size):
        self.size = size
        self.background = pygame.Surface(size)  # make a background surface
        self.background = self.background.convert()
        self.background.fill((0, 0, 0))

        font = pygame.font.Font(None, 24)

        self.score = Score(font)

        self.walls = [Wall((5, 5), (size[0] - 10, 10)),
                      Wall((5, size[1] - 10), (size[0] - 10, size[1] - 5))]

        self.bats = []

        control_scheme_1 = ControlScheme()
        control_scheme_1.up = pygame.K_w
        control_scheme_1.down = pygame.K_s

        control_scheme_2 = ControlScheme()
        control_scheme_2.up = pygame.K_UP
        control_scheme_2.down = pygame.K_DOWN

        self.bats.append(Bat((5, int(size[1]/2)), control_scheme_1, self.size))
        self.bats.append(Bat((size[0] - 10, int(size[1]/2)), control_scheme_2, self.size))

        self.ball = Ball((int(size[0]/2), int(size[1]/2)))

    def process_event(self, event):
        for bat in self.bats:
            bat.process_event(event)

    def update(self, time_delta):
        for bat in self.bats:
            bat.update(time_delta)

        self.ball.update(time_delta, self.bats, self.walls)

        if self.ball.position[0] < 0:
            self.ball.reset()
            self.score.increase_player_2_score()
        elif self.ball.position[0] > self.size[0]:
            self.ball.reset()
            self.score.increase_player_1_score()

    def draw(self, surface):
        surface.blit(self.background, (0, 0))

        for wall in self.walls:
            wall.render(surface)

        for bat in self.bats:
            bat.render(surface)

        self.ball.render(surface)
        self.score.render(surface, self.size)


class Bat:
    def __init__(self, start_pos, control_scheme, court_size):
        self.control_scheme = control_scheme
        self.move_up = False
        self.move_down = False
        self.move_speed = 450.0

        self.court_size = court_size

        self.length = 30.0
        self.width = 5.0

        self.position = [float(start_pos[0]), float(start_pos[1])]
        
        self.rect = pygame.Rect((start_pos[0], start_pos[1]), (self.width, self.length))
        self.colour = pygame.Color("#FFFFFF")

    def process_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == self.control_scheme.up:
                self.move_up = True
            if event.key == self.control_scheme.down:
                self.move_down = True

        if event.type == pygame.KEYUP:
            if event.key == self.control_scheme.up:
                self.move_up = False
            if event.key == self.control_scheme.down:
                self.move_down = False

    def update(self, dt):
        if self.move_up:
            self.position[1] -= dt * self.move_speed

            if self.position[1] < 10.0:
                self.position[1] = 10.0

            self.rect.y = self.position[1]
                
        if self.move_down:
            self.position[1] += dt * self.move_speed

            if self.position[1] > self.court_size[1] - self.length - 10:
                self.position[1] = self.court_size[1] - self.length - 10

            self.rect.y = self.position[1]

    def render(self, screen):
        pygame.draw.rect(screen, self.colour, self.rect)


class Wall:
    def __init__(self, top_left, bottom_right):
        self.rect = pygame.Rect(top_left, (bottom_right[0] - top_left[0], bottom_right[1] - top_left[1]))
        self.colour = pygame.Color("#C8C8C8")

    def render(self, screen):
        pygame.draw.rect(screen, self.colour, self.rect)


class Ball:
    def __init__(self, start_position):
        self.rect = pygame.Rect(start_position, (5, 5))
        self.colour = pygame.Color(255, 255, 255)
        self.position = [float(start_position[0]), float(start_position[1])]
        self.start_position = [self.position[0], self.position[1]]
        self.ball_speed = 120.0
        self.max_bat_bounce_angle = 5.0 * math.pi/12.0
        self.collided = False

        self.velocity = [0.0, 0.0]
        self.create_random_start_vector()

    def render(self, screen):
        pygame.draw.rect(screen, self.colour, self.rect)

    def create_random_start_vector(self):
        y_random = random.uniform(-0.5, 0.5)
        x_random = 1.0 - abs(y_random)
        if random.randint(0, 1) == 1:
            x_random = x_random * -1.0
        self.velocity = [x_random * self.ball_speed, y_random * self.ball_speed]

    def reset(self):
        self.position = [self.start_position[0], self.start_position[1]]
        self.create_random_start_vector()

    def update(self, dt, bats, walls):
        self.position[0] += self.velocity[0] * dt
        self.position[1] += self.velocity[1] * dt
        self.rect.x = self.position[0]
        self.rect.y = self.position[1]

        collided_this_frame = False
        for wall in walls:
            if self.rect.colliderect(wall.rect):
                collided_this_frame = True
                if not self.collided:
                    self.collided = True
                    self.velocity[1] = self.velocity[1] * -1

        for bat in bats:
            if self.rect.colliderect(bat.rect):
                collided_this_frame = True
                if not self.collided:
                    self.collided = True
                    bat_y_centre = bat.position[1] + (bat.length/2)
                    ball_y_centre = self.position[1] + 5
                    relative_intersect_y = bat_y_centre - ball_y_centre  # should be in 'bat space' between -50 and +50
                    normalized_relative_intersect_y = relative_intersect_y/(bat.length/2)
                    bounce_angle = normalized_relative_intersect_y * self.max_bat_bounce_angle

                    self.velocity[0] = self.velocity[0] * -1
                    self.velocity[1] = self.ball_speed * -math.sin(bounce_angle)

        if not collided_this_frame:
            self.collided = False


class Score:
    def __init__(self, font):
        self.player_1_score = 0
        self.player_2_score = 0
        self.font = font

        self.score_string = None
        self.score_text_render = None

        self.update_score_text()

    def update_score_text(self):
        self.score_string = str(self.player_1_score) + " - " + str(self.player_2_score)
        self.score_text_render = self.font.render(self.score_string, True, pygame.Color(200, 200, 200))

    def render(self, screen, size):
        screen.blit(self.score_text_render, self.score_text_render.get_rect(centerx=size[0]/2,
                                                                            centery=size[1]/10))

    def increase_player_1_score(self):
        self.player_1_score += 1
        self.update_score_text()

    def increase_player_2_score(self):
        self.player_2_score += 1
        self.update_score_text()
'''


'''
    if self.type == menu.OPTION:
        pass

    if self.type == menu.WELCOME:
        pass

    if self.type == menu.CONTROLS:
        pass

    if self.type == menu.TOOLBAR:
        pass

    if self.type == menu.REPEAT:
        pass

    if self.type == menu.SAVE:
        pass

    if self.type == menu.OPEN:
        pass

    if self.type == menu.EXPORT:
        pass
'''