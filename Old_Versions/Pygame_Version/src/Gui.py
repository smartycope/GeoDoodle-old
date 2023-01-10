import os, json
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame, pygame_gui

from pygame_gui.core.utility import create_resource_path

from pygame_gui.ui_manager import UIManager
from pygame_gui.elements.ui_window import UIWindow
from pygame_gui.elements.ui_image import UIImage

from copy import deepcopy

from menu import menu
from Point import Point
from Menus import *

import os; DIR = os.path.dirname(os.path.dirname(__file__)); DIR += '\\main\\' if os.name == 'nt' else '/'

SAVES_FOLDER = DIR + 'saves'
GUI_THEME_FILE = DIR + 'data\\myTheme.json' if os.name == 'nt' else 'data/myTheme.json'

NON_TOOLBAR_MENU = list(menu)
NON_TOOLBAR_MENU.remove(menu.TOOLBAR)

MAX_TOOLBAR_SIZE = 1050

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
        self.active = True

        super().__init__(pygame.Rect(pos, (self.width, self.height)), uiManager, window_display_title=title, object_id=id)

        drawSurfaceSize = self.get_container().get_size()
        self.drawSurface = pygame.Surface(drawSurfaceSize).convert()
        
        self.drawImage = UIImage(pygame.Rect((0, 0), drawSurfaceSize),
                            self.drawSurface,
                            manager=self.uiManager,
                            container=self,
                            parent_element=self)

        self.menu = menu(uiManager, self.get_container())
        self.show()
        self.enable()

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
        self.size   = rootWindowSurface.get_size()

        self.rootWindowSurface = rootWindowSurface

        self.uiManager = pygame_gui.UIManager((self.width, self.height), GUI_THEME_FILE)

        self.hasHacked = False

        self.passDataToGame = dict(zip(menu, [None] * len(menu)))

        # self.repeatWindow   = Window([None, None], self.uiManager, 'Repeat Pattern' , '#repeat_window',   RepeatMenu,   Point(self.size) / 1.25)
        # self.optionWindow   = Window([None, None], self.uiManager, 'Options'        , '#options_window',  OptionMenu,   (300, self.height / 1.05))
        # self.saveWindow     = Window([None, None], self.uiManager, 'Save Pattern'   , '#save_window',     SaveMenu,     (500, 400))
        # self.openWindow     = Window([None, None], self.uiManager, 'Open Pattern'   , '#open_window',     OpenMenu,     (500, 400))
        # self.exportWindow   = Window([None, None], self.uiManager, 'Export Pattern' , '#export_window',   ExportMenu,   (500, 400))
        # self.controlsWindow = Window([None, None], self.uiManager, 'Edit Controls'  , '#controls_window', ControlsMenu, (500, 400))
        # self.welcomeWindow  = Window([0, 0],       self.uiManager, 'Welcome!'       , '#welcome_window',  WelcomeMenu,   Point(self.size) - 10)

        self.repeatWindow   = None
        self.optionWindow   = None
        self.saveWindow     = None
        self.openWindow     = None
        self.exportWindow   = None
        self.controlsWindow = None
        self.welcomeWindow  = None

        self.toolbarSize  = [self.size[0], 50]
        if self.size[0] > MAX_TOOLBAR_SIZE:
            self.toolbarSize[0] = MAX_TOOLBAR_SIZE
        self.toolbarPos   = Point((self.size[0] / 2) - (self.toolbarSize[0] / 2), self.size[1] - self.toolbarSize[1])
        # self.toolbar = Toolbar(self.uiManager, toolbarPos.data(), toolbarSize)
        self.toolbar = None

    def handleInput(self, event, type=None):
        if type == menu.TOOLBAR and self.toolbar is not None:
            self.toolbar.handleEvent(event)

        if event.type == pygame.QUIT:
            exit(0)

        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            return False

        self.uiManager.process_events(event)

        if event.type == pygame.USEREVENT and event.user_type == pygame_gui.UI_WINDOW_CLOSE:
            return False # Tells Game that the window is now closed
        else:
            return True

    def createWindow(self, type):
        # print(f'Creating {type.name}')
        if type == menu.REPEAT:
            self.repeatWindow   = Window([None, None], self.uiManager, 'Repeat Pattern' , '#repeat_window',   RepeatMenu,   Point(self.size) / 1.25)
            return self.repeatWindow
        if type == menu.OPTION:
            self.optionWindow   = Window([None, None], self.uiManager, 'Options'        , '#options_window',  OptionMenu,   (300, self.height / 1.05))
            return self.optionWindow
        # if type == menu.SAVE:
        #     # self.saveWindow     = Window([None, None], self.uiManager, 'Save Pattern'   , '#save_window',     SaveMenu,     (500, 400))
        #     self.saveWindow = SaveMenu(self.uiManager)
        #     return self.saveWindow
        # if type == menu.OPEN:
        #     self.openWindow     = Window([None, None], self.uiManager, 'Open Pattern'   , '#open_window',     OpenMenu,     (500, 400))
        #     return self.openWindow
        # if type == menu.EXPORT:
        #     self.exportWindow   = Window([None, None], self.uiManager, 'Export Pattern' , '#export_window',   ExportMenu,   (500, 400))
        #     return self.exportWindow
        if type == menu.CONTROLS:
            self.controlsWindow = Window([None, None], self.uiManager, 'Edit Controls'  , '#controls_window', ControlsMenu, (500, 400))
            return self.controlsWindow
        if type == menu.WELCOME:
            self.welcomeWindow  = Window([0, 0],       self.uiManager, 'Welcome!'       , '#welcome_window',  WelcomeMenu,   Point(self.size) - 10)
            return self.welcomeWindow
        if type == menu.TOOLBAR:
            self.toolbar = Toolbar(self.uiManager, self.toolbarPos.data(), self.toolbarSize)
            return self.toolbar

    def getWindow(self, type):
        if type == menu.OPTION:
            return self.optionWindow
        if type == menu.WELCOME:
            return self.welcomeWindow
        if type == menu.CONTROLS:
            return self.controlsWindow
        if type == menu.TOOLBAR:
            return self.toolbar
        if type == menu.REPEAT:
            return self.repeatWindow
        if type == menu.SAVE:
            return self.saveWindow
        if type == menu.OPEN:
            return self.openWindow
        if type == menu.EXPORT:
            return self.exportWindow

    def killWindow(self, type):
        # print(f'Killing {type.name}')
        if type == menu.OPTION:
            if self.optionWindow is not None:
                self.optionWindow.kill()
            self.optionWindow = None
        if type == menu.WELCOME:
            if self.welcomeWindow is not None:
                self.welcomeWindow.kill()
            self.welcomeWindow = None
        if type == menu.CONTROLS:
            if self.controlsWindow is not None:
                self.controlsWindow.kill()
            self.controlsWindow = None
        if type == menu.TOOLBAR:
            if self.toolbar is not None:
                self.toolbar.toolbar.kill()
            self.toolbar = None
        if type == menu.REPEAT:
            if self.repeatWindow is not None:
                self.repeatWindow.kill()
            self.repeatWindow = None
        if type == menu.SAVE:
            if self.saveWindow is not None:
                self.saveWindow.filePicker.element.kill()
            self.saveWindow = None
        if type == menu.OPEN:
            if self.openWindow is not None:
                self.openWindow.filePicker.element.kill()
            self.openWindow = None
        if type == menu.EXPORT:
            if self.exportWindow is not None:
                self.exportWindow.filePicker.element.kill()
            self.exportWindow = None

    def draw(self, deltaTime, activate, context):
        if self.getWindow(activate) is None:
            self.createWindow(activate)

        # Get Game to talk to the induvidual GUIs
        self.getWindow(activate).updateContextData(context)

        # Get the menu-based GUIs to talk to Game
        for m in [menu.WELCOME, menu.OPTION, menu.REPEAT, menu.CONTROLS]:
            if self.getWindow(m) is not None and self.getWindow(m).active:
                self.passDataToGame[m] = self.getWindow(m).menu.passDataBack()
            else:
                self.passDataToGame[m] = None

        # Get induvidual GUIs to talk to Game
        if activate in [menu.TOOLBAR, menu.OPEN, menu.SAVE, menu.EXPORT]:
            if self.getWindow(activate) is not None and self.getWindow(activate).active:
                self.passDataToGame[activate] = self.getWindow(activate).passDataBack()
            else:
                self.passDataToGame[activate] = None

        self.uiManager.update(deltaTime)
        self.uiManager.draw_ui(self.rootWindowSurface)

        return self.passDataToGame
