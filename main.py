from Game import Game
import argparse

description = 'GeoDoodle is a graph paper-like program for doodling cool patterns.'

parser = argparse.ArgumentParser(description=description)
parser.add_argument('-v' , '--verbose'                                             , action='store_true')
parser.add_argument('-o' , '--open'     , help='Open a .gdl file'                  , type=str, nargs='?')
parser.add_argument('-c' , '--controls' , help='Display in-game controls and exit' , action='store_true')
parser.add_argument(       '--credits'  , help='Display credits and exit'          , action='store_true')

args = parser.parse_args()
args.verbose = True

controls = '''
Move the mouse around and click to draw patterns

wasd / Arrow Keys:  Move the focus
q / Middle Click:   Delete all the lines at that point
Q:                  Delete all lines
e:                  Press twice along a line to erase that specific line
f:                  Toggle fullscreen
c / Right Click:    Finish the current line and start a new one
u / Ctrl + z:       Undo the last line
m:                  Increase mirroring
r:                  Repeat the pattern everywhere (Coming Soon!)
S / Ctrl + s:       Save the pattern as a .gdl file
O / Ctrl + o:       Open a .gdl file
E / Ctrl + e:       Export pattern as an image
Esc:                Close the program or menu
More Coming Soon!'''

credits = '''
Originally made by Copeland Carter, with plentiful help from Brigham Keys, Esq., 
and built on a framework made by James Helfrich

Remade in Python by Copeland Carter

Brigham, if you're reading this right now, you're an idiot.

This software is open source under the GPL. No rights reserved.'''


if args.controls:
    print(controls)
elif args.credits:
    print(credits)
else:
    # game = Game(1366, 768, 'GeoDoodle', args=args)
    game = Game(900, 550, 'GeoDoodle', args=args)
    game.run()
    game.exit()






# Default settings:
'''
{
    "dotSpread": 22,
    "offScreenAmount": 10,
    "dotSize": 2,
    "lineThickness": 2,
    "exportLineThickness": 3,
    "dotColor": [0, 0, 0],
    "focusColor": [0, 0, 255],
    "backgroundColor": [200, 160, 100],
    "defaultLineColor": [0, 0, 0],
    "dragDelay": 11,
    "FPS": 30,
    "focusRadius": 6,
    "themeFile": "theme_1.json",
    "iconFile": "icon3.png",
    "keyRepeatInterval": 20,
    "keyRepeatDelay": 200
}
'''


# paper color: [200, 160, 100]
# breeze dark: [30, 30, 30]
