from menu import menu
from Elements import *
import pygame_gui
import json, re

from Point import Point
from Geometry import *

from os.path import dirname; DIR = dirname(__file__) + '/../'

with open(DIR + 'settings.jsonc', 'r') as f:
    SETTINGS = json.load(f)

offScreenAmount = SETTINGS['offScreenAmount'] * SETTINGS['dotSpread']


class AbstractMenu:
    def __init__(self, uiManager, container):
        self.size = container.get_size()
        self.uiManager = uiManager
        self.allowPassing = False
        self.active = True
        self.context = None
        self.elementPos = []
        self.elements   = ()

    def handleEvent(self, event):
        for element in self.elements:
            # if element is not None:
            element.handleEvent(event)

    def updateContextData(self, context):
        if self.context != context and not self.allowPassing:
            self.context = context

    def passDataBack(self):
        if self.allowPassing:
            self.allowPassing = False
            return self.context
        else:
            return None

    def draw(self, surface):
        pass

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
        self.previewStartY = (row * 8.5) + self.previewEdgeOffset + self.createPatternButton.size[1]

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

        # center = (Point(self.previewSurface.get_size()) / 2) % PREVIEW_DOT_SPREAD
        # startPoint = Point(min(self.previewDots, key=lambda i:abs(i.x - center.x)).x + 1, min(self.previewDots, key=lambda i:abs(i.y - center.y)).y + 1)


        # Draw the lines
        if self.pattern is not None:
            drawLines = self.pattern.repeat(self.previewSurface.get_size(), offScreenAmount, self.overlap,
                                                       dotSpread=PREVIEW_DOT_SPREAD,
                                                       startPoint=center,
                                                       halfsies=self.halfsies)

            if drawLines is not None:
                for i in drawLines:
                    i.draw(self.previewSurface)

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
        surface.blit(self.previewSurface, (self.previewEdgeOffset * 3, self.previewStartY))

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


class OptionMenu(AbstractMenu):
    def __init__(self, uiManager, container):
        super().__init__(uiManager, container)

        with open(DIR + 'settings.jsonc', 'r') as f:
            settings = json.load(f)

        row = self.size[1] / 20
        rowSpacing = 2.5
        # currentRow = .9
        centerx = (self.size[0] / 2) - 15 # 15 for the scroll bar
        xpos = 20

        ELEMENT_COUNT = 10

        for i in range(ELEMENT_COUNT):
            self.elementPos.append([xpos, row * (i + .2) * rowSpacing])
            # currentRow += rowSpacing

        self.elementPos[-1][0] = centerx - 55
        self.elementPos[0][1] -= .1 * row 

        self.elements = (
            Text([*self.elementPos[0]],     uiManager, container, 'Options'),
            InputBox([*self.elementPos[1]], uiManager, container, 'Dot Spread',                  str(settings['dotSpread']),         numbersOnly=True),
            InputBox([*self.elementPos[2]], uiManager, container, 'Drag Delay',                  str(settings['dragDelay']),         numbersOnly=True),
            InputBox([*self.elementPos[3]], uiManager, container, 'FPS',                         str(settings['FPS']),               numbersOnly=True),
            InputBox([*self.elementPos[4]], uiManager, container, 'Key Repeat Delay',            str(settings['keyRepeatDelay']),    numbersOnly=True),
            InputBox([*self.elementPos[5]], uiManager, container, 'Key Repeat Interval',         str(settings['keyRepeatInterval']), numbersOnly=True),
            InputBox([*self.elementPos[6]], uiManager, container, 'Off-Screen Amount',           str(settings['offScreenAmount']),   numbersOnly=True),
            InputBox([*self.elementPos[7]], uiManager, container, 'Default Save Location',       str(settings['saveLoc']),           disallowedChars='forbidden_file_path', size=[self.size[0] - (xpos * 2) - 15, None]),
            InputBox([*self.elementPos[8]], uiManager, container, 'Default Image Save Location', str(settings['imageSaveLoc']),      disallowedChars='forbidden_file_path', size=[self.size[0] - (xpos * 2) - 15, None]),
            Button([*self.elementPos[9]],   uiManager, container, 'Accept & Save', self.saveSettings)
            # Button(self.elementPos[x],   uiManager, container, 'Cancel', self.closeWindow, size=[self.acceptButton.size[0], None])
        )

        self.verticalPercentage = self.size[1] / (self.elementPos[-1][1] + self.elements[-1].size[1] + 50)

        self.scrollBar = ScrollBar(uiManager, container, self.verticalPercentage)

    def saveSettings(self):
        print('Saving Settings')
        self.allowPassing = True
        self.context['dotSpread']         = self.elements[1].getInput()   #dotSpread.getInput()
        self.context['dragDelay']         = self.elements[2].getInput()   #dragDelay.getInput()
        self.context['FPS']               = self.elements[3].getInput()   #fps.getInput()
        self.context['keyRepeatDelay']    = self.elements[4].getInput()   #keyRepeatDelay.getInput()
        self.context['keyRepeatInterval'] = self.elements[5].getInput()   #keyRepeatInterval.getInput()
        self.context['offScreenAmount']   = self.elements[6].getInput()   #offScreenAmount.getInput()
        self.context['savesLoc']          = self.elements[7].getInput()   #savesFileLoc.getInput()
        self.context['imageSavesLoc']     = self.elements[8].getInput()   #imageSavesFileLoc.getInput()

    def handleEvent(self, event):
        super().handleEvent(event)
        print(self.scrollBar.element.scroll_position)
        print(self.scrollBar.getPos())

        if self.scrollBar.handleEvent(event):
            for pos, element in zip(self.elementPos, self.elements):
                element.setPos([None, (self.scrollBar.getPos() * -self.size[1]) + pos[1]])


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

'''
class SaveMenu(AbstractMenu):
    def __init__(self, uiManager):
        super().__init__(uiManager, uiManager.get_root_container())

        self.filePicker = FilePicker(uiManager, startingPath=SETTINGS['saveLoc'], title='Save Pattern', size=(Point(self.uiManager.get_root_container().get_size()) / 1.5).data())
        self.filePicker.element.allow_existing_files_only = False
        self.filePicker.element.allow_picking_directories = False
        self.filePicker.element.current_directory_path += '/'
        # print(self.filePicker.element.file_path_text_line)
        # print(self.filePicker.element.current_file_path)
        for i in os.listdir(SETTINGS['saveLoc']):
            print(re.findall(r'[P][a][t][t][e][r][n]\d+', i[1]))
        # print(self.filePicker.element.last_valid_directory_path)

    def handleEvent(self, event):
        self.context = self.filePicker.handleEvent(event)
        if self.context is not None:
            self.allowPassing = True


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
'''

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


class Toolbar:
    def __init__(self, uiManager, pos, size):
        self.size = size
        # if size[0] is None:
        #     self.size[0] = 
        
        self.pos  = pos
        self.colors = None
        self.active = True
        self.allowPassing = False
        self.selected = 0

        self.toolbar = UIPanel(pygame.Rect(self.pos, self.size), 4, uiManager)

        self.toolbar.background_colour = [30, 30, 30]
        
        self.colorPicker = None

        # For remembering what button we're changing the color of when in the color picker
        self.index = None

        self.uiManager = uiManager

        self.buttonSize = [70, 40]
        spacing = (self.size[0] - (self.buttonSize[0] / 2)) / 10

        self.buttons = []

        for i in range(10):
            self.buttons.append(UIButton(pygame.Rect([(spacing * i) + (spacing / 4), (size[1] / 2) - (self.buttonSize[1] / 2)], self.buttonSize), str(i),  manager=uiManager, container=self.toolbar, allow_double_clicks=True))

    def toggle(self, state=None):
        if state is None:
            state = self.active

        if state:
            self.toolbar.disable()
            self.toolbar.hide()
            self.active = False
        else:
            self.toolbar.show()
            self.toolbar.enable()
            self.active = True

    def handleEvent(self, event):
        # for i in self.buttons:
        if event.type == pygame.USEREVENT:
            if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element in self.buttons:
                    self.selected = self.buttons.index(event.ui_element)
                    self.allowPassing = True
                    self.resetButtonColors()

            elif event.user_type == pygame_gui.UI_BUTTON_DOUBLE_CLICKED:
                if event.ui_element in self.buttons:
                    self.index = self.buttons.index(event.ui_element)
                    color = self.colors[self.index]
                    self.colorPicker = ColorPicker(self.uiManager, startingColor=color, title=f'Color #{self.index}')
                    for i in self.buttons:
                        i.disable()

        if self.colorPicker is not None:
            self.colorPicker.handleEvent(event)

            if  event.type == pygame.USEREVENT and \
               (event.user_type == pygame_gui.UI_WINDOW_CLOSE or \
                event.user_type == pygame_gui.UI_COLOUR_PICKER_COLOUR_PICKED) and \
                event.ui_element == self.colorPicker.element:

                self.colors[self.index] = self.colorPicker.getColor()
                self.index = None
                self.colorPicker = None
                self.allowPassing = True
                self.resetButtonColors()
                for i in self.buttons:
                    i.enable()

    def resetButtonColors(self):
        cnt = 0
        for color, button in zip(self.colors, self.buttons):
            colorSurface = pygame.Surface(self.buttonSize)
            colorSurface.fill(color)

            hoverColorSurface = colorSurface.copy() #pygame.Surface(self.buttonSize)
            hoverColor = [*color]
            hoverColor[0] /= 1.75
            hoverColor[1] /= 1.75
            hoverColor[2] /= 1.75
            hoverColorSurface.fill(hoverColor)
            # hoverColorSurface = colorSurface
            # hoverColorSurface.set_alpha(50)
            button.hovered_image = hoverColorSurface

            button.normal_image = colorSurface

            if self.selected == cnt:
                print('creating subsurface')
                tmp = hoverColorSurface.copy()
                selectedSurface = tmp.subsurface(hoverColorSurface.get_rect().inflate(-10, -10))
                selectedSurface.fill(color)
                button.normal_image = tmp
            else:
                pass


            # button.selected_image = hoverColorSurface
            # button.image = hoverColorSurface


            # self.uiManager.ui_theme.ui_element_colours['panel.button.normal_text'] = (255, 0, 0, 255)
            # self.uiManager.ui_theme.ui_element_colours['panel.button.active_text'] = (255, 0, 0, 255)
            # self.uiManager.ui_theme.ui_element_colours['panel.button.selected_text'] = (255, 0, 0, 255)
            

            # button.ui_theme = {'normal_bg': (69, 73, 78, 255), 'hovered_bg': (53, 57, 62, 255), 'disabled_bg': (37, 41, 46, 255), 
            # 'selected_bg': (25, 55, 84, 255), 'active_bg': (54, 88, 128, 255), 'normal_text': (0, 0, 255, 255), 
            # 'hovered_text': (255, 255, 255, 255), 'disabled_text': (109, 115, 111, 255), 'selected_text': (255, 255, 255, 255),
            # 'active_text': (187, 187, 187, 255), 'normal_border': (92, 96, 98, 255), 'hovered_border': (176, 176, 176, 255),
            # 'disabled_border': (128, 128, 128, 255), 'selected_border': (128, 128, 176, 255), 'active_border': (128, 128, 176, 255)}

            # {'normal_bg': (69, 73, 78, 255), 'hovered_bg': (53, 57, 62, 255), 'disabled_bg': (37, 41, 46, 255), 
            # 'selected_bg': (25, 55, 84, 255), 'active_bg': (54, 88, 128, 255), 'normal_text': (197, 203, 216, 255),
            # 'hovered_text': (255, 255, 255, 255), 'disabled_text': (109, 115, 111, 255), 'selected_text': (255, 255, 255, 255),
            # 'active_text': (187, 187, 187, 255), 'normal_border': (92, 96, 98, 255), 'hovered_border': (176, 176, 176, 255),
            # 'disabled_border': (128, 128, 128, 255), 'selected_border': (128, 128, 176, 255), 'active_border': (128, 128, 176, 255)}

            button.rebuild()
            # button.rebuild_from_changed_theme_data()
            cnt += 1

    def draw(self, surface):
        pass
        
    def updateContextData(self, context):
        assert(len(context) == 11)
        if self.colors != context[:-1] and not self.allowPassing:
            self.colors = [*context]
            self.selected = self.colors.pop()

            self.resetButtonColors()

    def passDataBack(self):
        if self.allowPassing:
            self.allowPassing = False
            return self.colors + [self.selected]
        else:
            return None



# Welcome
#************** Options: ***********************#
# Welcome text
# start button
# options menu button

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
