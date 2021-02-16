# from Point import Pointf, Pointi, Point
from random import randint
import math, re
from time import process_time
from typing import Callable, Any, Iterable, Optional, Union
import atexit
# from Point import Pointf

from os.path import dirname, join
DIR  = dirname(dirname(__file__))
UI   = join(DIR, 'ui/')
DATA = join(DIR, 'data/')



# Override the debug parameters and display the file/function for each debug call
#   (useful for finding debug calls you left laying around and forgot about)
debugCount = 0

DISPLAY_FILE = False
DISPLAY_FUNC = False
DISPLAY_LINK = False
HIDE_TODO    = False

#* Setters for the gloabals
def displayAllFiles(to=True):
    global DISPLAY_FILE
    DISPLAY_FILE = to

def displayAllFuncs(to=True):
    global DISPLAY_FUNC
    DISPLAY_FUNC = to

def displayAllLinks(to=True):
    global DISPLAY_LINK
    DISPLAY_LINK = to

def hideAllTodos(to=True):
    global HIDE_TODO
    HIDE_TODO = to


#* Colors
# none, blue, green, orange, purple, cyan, alert red
colors = ['0', '34', '32', '33', '35', '36', '31']



# https://en.wikipedia.org/wiki/ANSI_escape_code#Colors
def _printColor(r, g, b, fg=True):
    """ Set fg to false to set the background color
    """
    try:
        if fg:
            print(f'\033[38;2;{r};{g};{b}m', end='')
        else:
            print(f'\033[48;2;{r};{g};{b}m', end='')
    except:
        _resetColor()


def printBasicColor(num, fg=True):
    """ Sets the terminal to one of, for now, 5 unique colors for debugging purpouses
        0 resets the terminal and -1 is alert red.
    """
    try:
        if not fg:
            num += 10
        print(f'\033[{colors[num]}m', end='')
    except:
        _resetColor()


def _resetColor():
    """ Resets the terminal to it's original color
    """

    print('\033[0m',  end='')
    print('\033[39m', end='')
    print('\033[49m', end='')
    # print(, end='')

    # try:
    #     # print('\033[39m', end='')
    #     # print('\033[49m', end='')
    #     pass
    # finally:
    #     # print(err)
    #     print('\033[39m', end='')
    #     print('\033[49m', end='')
    #     # _resetColor()


def _getMetaData(calls=1):
    """ Gets the meta data of the line you're calling this function from.
        Calls is for how many function calls to look back from.
    """
    from inspect import stack
    try:
        s = stack()[calls]
        return s
    except IndexError:
        return None


def _getLink(calls=0, full=False, customMetaData=None):
    if customMetaData is not None:
        d = customMetaData
    else:
        d = _getMetaData(calls+2)

    _printLink(d.filename, d.lineno, d.function if full else None)


KILL_IT = 6

# TODO This doesn't quite work properly
def _getListStr(v: Union[tuple, list, set, dict], limitToLine: bool=True, minItems: int=2, maxItems: int=10,
                color: int=0) -> str:
    """ "Cast" a tuple, list, set or dict to a string, automatically shorten
        it if it's long, and display how long it is.

        Params:
            limitToLine: if True, limit the length of list to a single line
            minItems: show at least this many items in the list
            maxItems: show at most this many items in the list
            color: a simple int color

        Note:
            If limitToLine is True, it will overrule maxItems, but *not* minItems
    """
    if type(v) in (tuple, list, set) and len(v) > minItems:
        from os import get_terminal_size
        from copy import deepcopy
        if type(v) is set:
            v = tuple(v)

        ellipsis = f', \033[0m...\033[{colors[color]}m '
        length = f'(len={len(v)})'

        if limitToLine:
            firstHalf  = str(v[0:round(minItems/2)])[:-1]
            secondHalf = str(v[-round(minItems/2)-1:-1])[1:]
            prevFirstHalf = firstHalf
            prevSecondHalf = secondHalf
            index = 0

            # The 46 is a fugde factor. I don't know why it needs to be there, but it works.
            while (6 + 54 + len(length) + len(firstHalf) + len(secondHalf)) < get_terminal_size().columns:
                index += 1
                firstHalf  = str(v[0:round((minItems+index)/2)])[:-1]
                secondHalf = str(v[-round((minItems+index)/2)-1:-1])[1:]
                prevFirstHalf = firstHalf
                prevSecondHalf = secondHalf
                if index > KILL_IT:
                    break

            firstHalf = prevFirstHalf
            secondHalf = prevSecondHalf

        else:
            firstHalf  = str(v[0:round(maxItems/2)])[:-1]
            secondHalf = str(v[-round(maxItems/2)-1:-1])[1:]

        return firstHalf + ellipsis + secondHalf + length

    else:
        return str(v) + f'(len={len(v)})'


def _getTypename(var):
    if type(var) in (tuple, list, set):
        returnMe = type(var).__name__
        while type(var) in (tuple, list, set):
            try:
                var = var[0]
            except (KeyError, IndexError, TypeError):
                returnMe += '('
                break
            returnMe += '(' + type(var).__name__

        cnt = 0
        for i in returnMe:
            if i == '(':
                cnt += 1
        return returnMe + (')'*cnt)
    else:
        return type(var).__name__


def _printLink(filename, lineNum, function=None):
    """ Print a VSCodium clickable file and line number
        If function is specified, a full python error message style line is printed
    """
    try:
        _printColor(40, 43, 46)
        if function is None: #    \|/  Oddly enough, this double quote is nessicary
            print('\t', filename, '", line ', lineNum, '\033[0m', sep='')
        else:
            print('\tFile "', filename, '", line ', lineNum, ', in ', function, sep='')

        _resetColor()
    finally:
        _resetColor()
    _resetColor()
    print('\033[0m', end='')


def basicColoredPrint(string, color, fg, **kwargs):
    printBasicColor(color, fg=fg)
    print(string, **kwargs)
    _resetColor()


def coloredPrint(string, r, g, b, fg):
    _printColor(r, g, b, fg=fg)
    try:
        print(string)
        _resetColor()
    except:
        _resetColor()
    finally:
        _resetColor()


def _printDebugCount(leftAdjust=2):
    global debugCount
    debugCount += 1
    print(f'{str(debugCount)+":":<{leftAdjust+2}}', end='')



# TODO This is not done
def copesNameof(calls=0, full=True, displayParamParams=False, customMetaData=None):
    if customMetaData is not None:
        line = customMetaData.code_context[0]
    else:
        line = _getMetaData(calls+2).code_context[0]

    #* First strip it down to just what it's parameters it was called with
    line = re.sub(r'\s+', '', line)
    line = re.sub(r'\bdebug\b', '', line)
    line = line[1:-1]

    #* Now split all the parameters, and throw away any that are keyword arguements
    chunks = [re.split(r',', i) for i in re.split(r'\(|\)', line)]
    for cnt, i in enumerate(chunks[-1]):
        if '=' in i:
            chunks[-1].pop(cnt)







    return line

"        debug(classs.method(methodParam1, methodParam2, kwMethodParam=False), secondVar, showFunc=True, color = 6)\n"

# print(copesNameof())


# TODO This has not been written
def getVarName(useBackup=True, calls=0, full=True, customMetaData=None):
    if customMetaData is not None:
        line = customMetaData.code_context[0]
    else:
        line = _getMetaData(calls+2).code_context[0]



class _None(): pass

# TODO: somehow round any float to a given length, including those printed in iterables
# TODO make it so if the first is a variable you can't get (or just any variable), and the
#   second is a string literal, set the string literal as the name of the first variable
# TODO If there's multiple variables passed in, and it cant get one of them, it gives up.
#   Call the varname function seperately for each variable.
def debug(var=None, *more_vars, name=None, merge: bool=False, repr: bool=False, calls: int=1,
          color: int=None, background: bool=False, showFunc: bool=False, showFile: bool=False,
          limitToLine: bool=True, minItems: int=2, maxItems: int=10, clickable: bool=False,
          _tries: int=0) -> None:
    """Print variable names and values for easy debugging.

        Call with no parameters to tell if its getting called at all, and call with a only a string to just display the string

        The format goes: Global_debug_counter[file->function()->line_number]: prefix data_type variable_name = variable_value

        Args:
            var: The variable or variables to print
            prefix: An additional string to print for each line
            merge: Put all the variables on the same line
            repr: Use __repr__() instead of __str__()
            calls: If you're passing in a return from a function, say calls=1
            color: 0-5. 5 different preset colors for easy distinction
            background: Use the background color instead of the forground color
            showFunc: Display what function you're calling from
            showFile: Display waht file you're calling from

        Usage:
            debug() -> prints 'HERE! HERE!' in bright red for you
            debug('I got to this point') -> prints that message for you
            debug(var) -> prints the type(var) var = {var}
            debug(func()) -> prints what the function returns
            debug(var, var1, var2) -> prints each var on their own line
            debug(var, name='variable') -> prints type(var) variable = {var}
            debug(var, var1, var2, name=('variable', 'variable2', 'variable3')) ->
                prints each var on their own line with the appropriate name
    """
    from varname import nameof, VarnameRetrievingError
    from os.path import basename

    global debugCount, DISPLAY_FUNC, DISPLAY_FILE, DISPLAY_LINK

    # +1 call because it itself is a function
    metaData = _getMetaData(calls+1)
    cantGetName = metaData == None
    clr = 1 if color is None else color
    # codeLine = metaData.code_context[1]
    # The max amount of nested function calls you can pass to this function
    hopelessThreashold = 2
    if maxItems < 0:
        maxItems = 1000000


    #* Set the stuff in the [] (the "context")
    if metaData is not None:
        context = str(metaData.lineno)
        if showFunc or DISPLAY_FUNC:
            context = metaData.function + '()->' + context

        if showFile or DISPLAY_FILE:
            context = basename(metaData.filename) + '->' + context

        context = f'[{context}] '
    else:
        context = ': '


    #* Only print the "HERE! HERE!" message
    if var is None:
        _printDebugCount()
        basicColoredPrint(context + 'HERE! HERE!', -1 if color is None else color, fg=not background, end='')
        # if clickable or DISPLAY_LINK:
        _getLink(customMetaData=metaData)
        return


    #* Seperate the variables into a tuple of (typeStr, varString)
    variables = ()
    for v in (var, *more_vars):
        if type(v) in (tuple, list, set, dict):
            variables += ((_getTypename(v), _getListStr(v, limitToLine, minItems, maxItems, color=clr)),)
        else:
            variables += ((_getTypename(v), str(v)),)


    #* Actually get the names
        # Try to get the full variable name.
        #   If you can't, try to get what name you can.
        #   If you still cant, see if it's because the user passed in a string literal.
        #       If so, just print that and be done.
        #   If not, then set cantGetName to True
    if name is None:
        try:
            varNames = nameof(*[i[1] for i in variables], caller=calls+1, full=True)
        except VarnameRetrievingError:
            try:
                varNames = nameof(*[i[1] for i in variables], caller=calls+1)
            except VarnameRetrievingError:
                if type(var) is str:
                    _printDebugCount()
                    basicColoredPrint(context + var, clr, fg=not background)
                    if clickable or DISPLAY_LINK:
                        _getLink(customMetaData=metaData)
                    return
                else:
                    cantGetName = True
                    varNames = ['?'] * len(variables)
    else:
        varNames = name


    #* Make sure the varNames is a tuple
    if type(varNames) is list:
        varNames = tuple(varNames)
    elif type(varNames) is not tuple:
        varNames = (varNames, )


    #* Try again with an additional call
    if cantGetName and _tries < hopelessThreashold:
        # pass
        debug(var, *more_vars, name=name, repr=repr, merge=merge, calls=calls+1, color=color, background=background,
              showFunc=showFunc, showFile=showFile, _tries=_tries+1, minItems=minItems, maxItems=maxItems,
              limitToLine=limitToLine)


    #* If we've given up, or if we got the name and we're printing...
    elif (cantGetName and _tries >= hopelessThreashold) or not cantGetName:
        #* Merge the names with the values
        nameWithValues = [f"{var_name} = {variables[i][1]!r}" if repr \
                     else f"{var_name} = {variables[i][1]}" \
                      for i, var_name in enumerate(varNames)]

        #* Either put everything on it's own line, or print out multiple lines
        if merge:
            _printDebugCount()
            basicColoredPrint(context + ', '.join(nameWithValues), clr, fg=not background)
        else:
            for cnt, name_and_value in enumerate(nameWithValues):
                _printDebugCount()
                basicColoredPrint(context + variables[cnt][0] + ' ' + name_and_value, clr, fg=not background)

            # debugCount -= 1


        if clickable or (cantGetName and name is None) or DISPLAY_LINK:
            _getLink(customMetaData=metaData)
            # _printLink(metaData.filename, metaData.lineno)



def debugged(var=_None, name=None, merge: bool=False, repr: bool=False, calls: int=1,
             color: int=None, background: bool=False, showFunc: bool=False, showFile: bool=False,
             limitToLine: bool=True, minItems: int=2, maxItems: int=10, clickable: bool=False):
    """ An inline version of debug
    """

    debug(var, name=name, merge=merge, repr=repr, calls=calls+1,
          color=color, background=background, showFunc=showFunc, showFile=showFile,
          limitToLine=limitToLine, minItems=minItems, maxItems=maxItems, clickable=clickable)

    _resetColor()

    return var



def todo(featureName, link=True):
    if not HIDE_TODO:
        _printDebugCount()
        print(f'{featureName} hasn\'t been implemented yet!')
        if link:
            _getLink(calls=1)



def reprise(obj, *args, **kwargs):
    """ Sets the __repr__ function to the __str__ function of a class.
        Useful for custom classes with overloaded string functions
    """
    obj.__repr__ = obj.__str__
    return obj



def percent(percentage):
    ''' Usage:
        if (percent(50)):
            <code that has a 50% chance of running>
    '''
    return randint(1, 100) < percentage



def closeEnough(a, b, tolerance):
    return a <= b + tolerance and a >= b - tolerance



def findClosestPoint(target, comparatorList):
    """ Finds the closest point in the list to what it's given
    """
    finalDist = 1000000

    for i in comparatorList:
        current = getDist(target, i)
        if current < finalDist:
            finalDist = current

    return finalDist



def findClosestXPoint(target, comparatorList, offsetIndex = 0):
    finalDist = 1000000
    result = 0

    # for i in range(len(comparatorList) - offsetIndex):
    for current in comparatorList:
        # current = comparatorList[i + offsetIndex]
        currentDist = abs(target.x - current.x)
        if currentDist < finalDist:
            result = current
            finalDist = currentDist

    return result



def getPointsAlongLine(p1, p2):
    p1 = Pointi(p1)
    p2 = Pointi(p2)

    returnMe = []

    dx = p2.x - p1.x
    dy = p2.y - p1.y

    for x in range(p1.x, p2.x):
        y = p1.y + dy * (x - p1.x) / dx
        returnMe.append(Pointf(x, y))

    return returnMe



def rotatePoint(p, angle, pivotPoint, radians = False):
    if not radians:
        angle = math.radians(angle)
    # p -= pivotPoint
    # tmp = pygame.math.Vector2(p.data()).normalize().rotate(amount)
    # return Pointf(tmp.x, tmp.y) + pivotPoint

    dx = p.x - pivotPoint.x
    dy = p.y - pivotPoint.y
    newX = dx * math.cos(angle) - dy * math.sin(angle) + pivotPoint.x
    newY = dx * math.sin(angle) + dy * math.cos(angle) + pivotPoint.y

    return Pointf(newX, newY)



def getMidPoint(p1, p2):
    assert type(p1) == type(p2)
    # return Pointf((p1.x + p2.x) / 2, (p1.y + p2.y) / 2)
    return p1._initCopy((p1.x + p2.x) / 2, (p1.y + p2.y) / 2)


timingData = {}

#* A function decorator that prints how long it takes for a function to run
def timeFunc(func, accuracy=5):
    def wrap(*params, **kwparams):
        global timingData

        t = process_time()

        returns = func(*params, **kwparams)

        t2 = process_time()

        elapsed_time = round(t2 - t, accuracy)
        name = func.__name__

        try:
            timingData[name] += (elapsed_time,)
        except KeyError:
            timingData[name] = (elapsed_time,)

        _printDebugCount()
        # print(name, ' ' * (10 - len(name)), 'took', elapsed_time if elapsed_time >= 0.00001 else 0.00000, '\ttime to run.')
        print(f'{name:<12} took {elapsed_time:.{accuracy}f} seconds to run.')
        #  ' ' * (15 - len(name)),
        return returns
    return wrap


#* I realized *after* I wrote this that this is a essentially profiler. Oops.
def _printTimingData(accuracy=5):
    global timingData
    if len(timingData):
        print()

        maxName = len(max(timingData.keys(), key=len))
        maxNum  = len(str(len(max(timingData.values(), key=lambda x: len(str(len(x)))))))
        for name, times in reversed(sorted(timingData.items(), key=lambda x: sum(x[1]))):
            print(f'{name:<{maxName}} was called {len(times):<{maxNum}} times taking {sum(times)/len(times):.{accuracy}f} seconds on average for a total of {sum(times):.{accuracy}f} seconds.')

atexit.register(_printTimingData)



class getTime:
    """ A class to use with a with statement like so:
        with getTime('sleep'):
            time.sleep(10)
        It will then print how long the enclosed code took to run.
    """
    def __init__(self, name, accuracy=5):
        self.name = name
        self.accuracy = accuracy

    def __enter__(self):
        self.t = process_time()

    def __exit__(self, *args):
        # args is completely useless, not sure why it's there.
        t2 = process_time()
        elapsed_time = round(t2 - self.t, self.accuracy)
        print(self.name, ' ' * (15 - len(self.name)), 'took', f'{elapsed_time:.{self.accuracy}f}', '\ttime to run.')



def center(string):
    """ Centers a string for printing in the terminal
    """
    from os import get_terminal_size
    for _ in range(int((get_terminal_size().columns - len(string)) / 2)): string = ' ' + string
    return string



def isPowerOf2(x):
    return (x != 0) and ((x & (x - 1)) == 0)



def isBetween(val, start, end, beginInclusive=False, endInclusive=False):
    return (val >= start if beginInclusive else val > start) and \
           (val <= end   if endInclusive   else val < end)



def collidePoint(topLeft: 'Point', size: Union[tuple, list], target, inclusive=True):
    return isBetween(target.x, topLeft.x, size[0], beginInclusive=inclusive, endInclusive=inclusive) and \
           isBetween(target.y, topLeft.y, size[1], beginInclusive=inclusive, endInclusive=inclusive)



def insertChar(string, index, char):
    return string[:index] + char + string[index+1:]



def constrain(val, low, high):
    return min(high, max(low, val))



def rgbToHex(rgb):
    """translates an rgb tuple of int to a tkinter friendly color code"""
    return f'#{int(rgb[0]):02x}{int(rgb[1]):02x}{int(rgb[2]):02x}'



def darken(rgb, amount):
    """ Make amount negative to lighten
    """

    return tuple([constrain(i+amount, 0, 255) for i in rgb])


'''
def tlOriginToCenterOrigin(p: Point, width, height):
    return Pointf(p.x - (width / 2), p.y - (height / 2))
'''

'''
def clampPoint(p: Point, width, height):
    return p._initCopy(p.x / (width / 2), p.y / (height / 2))
'''


def clampColor(*rgba):
    """ Clamp a 0-255 color to a float between 1 and 0.
        Helpful for openGL commands.
    """
    if len(rgba) == 1 and type(rgba[0]) in (tuple, list):
        return tuple(c / 255 for c in rgba[0])
    else:
        return tuple(c / 255 for c in rgba)


def invertColor(*rgba):
    """ Inverts a color
    """
    if len(rgba) == 1 and type(rgba[0]) in (tuple, list):
        return tuple(255 - c for c in rgba[0])
    else:
        return tuple(255 - c for c in rgba)

'''
def toOpenGLCoord(p: Point, width, height):
    return Pointf((p.x - (width / 2)) / (width / 2), (p.y - (height / 2)) / (height / 2))
'''
'''
def toTLCoord(p: Point, width, height):
    return Pointi((p.x * (width / 2)) + (width / 2), (p.y * (height / 2)) + (height / 2))
'''

def translate(value, fromStart, fromEnd, toStart, toEnd):
    return ((abs(value - fromStart) / abs(fromEnd - fromStart)) * abs(toEnd - toStart)) + toStart


def frange(start, stop, skip=1.0, accuracy=10000000000000000):
    return [x / accuracy for x in range(int(start*accuracy), int(stop*accuracy), int(skip*accuracy))]



#* API Specific functions

#* Tkinter (ttk specifically)

# import tkinter as tk
# import tkinter.ttk as ttk
# from contextlib import redirect_stdout
# import ttkthemes

def stylenameElementOptions(stylename):
    '''Function to expose the options of every element associated to a widget
       stylename.'''
    with open('tmp.del', 'a') as f:
        with redirect_stdout(f):
            print('\n-----------------------------------------------------------------------------\n')
            try:
                # Get widget elements
                style = ttk.Style()
                layout = str(style.layout(stylename))
                print('Stylename = {}'.format(stylename))
                print('Layout    = {}'.format(layout))
                elements=[]
                for n, x in enumerate(layout):
                    if x=='(':
                        element=""
                        for y in layout[n+2:]:
                            if y != ',':
                                element=element+str(y)
                            else:
                                elements.append(element[:-1])
                                break
                print('\nElement(s) = {}\n'.format(elements))
                # Get options of widget elements
                for element in elements:
                    print('{0:30} options: {1}'.format(
                        element, style.element_options(element)))
            except tk.TclError:
                print('_tkinter.TclError: "{0}" in function'
                    'widget_elements_options({0}) is not a regonised stylename.'
                    .format(stylename))


# for i in ['TButton', 'TCheckbutton', 'TCombobox', 'TEntry', 'TFrame', 'TLabel', 'TLabelFrame', 'TMenubutton', 'TNotebook', 'TPanedwindow', 'Horizontal.TProgressbar', 'Vertical.TProgressbar', 'TRadiobutton', 'Horizontal.TScale', 'Vertical.TScale', 'Horizontal.TScrollbar', 'Vertical.TScrollbar', 'TSeparator', 'TSizegrip', 'Treeview', 'TSpinbox']:
#     stylenameElementOptions('test.' + i)

# stylenameElementOptions('me.TButton')




#* Pygame






'''
from Point import *
import os, math
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame
import time

class Pointer:
    def __init__(self, val):
        self.value = val

    def get(self):



def loadAsset(dir, name, extension='png'):
    return loadImage(dir + name + '.' + extension)



def getDist(a, b):
    return math.sqrt(((b.x - a.x)**2) + ((b.y - a.y)**2))


def getGroundPoints(groundPoints):
    returnMe = []
    for i in range(len(groundPoints) - 1):
        returnMe += getPointsAlongLine(groundPoints[i], groundPoints[i + 1])

    return returnMe



def portableFilename(filename):
    return os.path.join(*filename.split('/'))


def loadImage(filename):
    # if pygame.image.get_extended():
    filename = '/' + portableFilename(DATA + '/' + filename)

    image = pygame.image.load(filename)
    # self.image = self.image.convert()
    image = image.convert_alpha()
    # else:
    #     assert(not f"Cannot support the file extension {}")
    return image


def drawAllGroundPoints(surface, gp):
    for i in gp:
        pygame.gfxdraw.pixel(surface, *i.datai(), [255, 0, 0])


def rotateSurface(surface, angle, pivot, offset):
    """Rotate the surface around the pivot point.

    Args:
        surface (pygame.Surface): The surface that is to be rotated.
        angle (float): Rotate by this angle.
        pivot (tuple, list, pygame.math.Vector2): The pivot point.
        offset (pygame.math.Vector2): This vector is added to the pivot.
    """
    rotated_image = pygame.transform.rotozoom(surface, -angle, 1)  # Rotate the image.
    rotated_offset = offset.rotate(angle)  # Rotate the offset vector.
    # Add the offset vector to the center/pivot point to shift the rect.
    rect = rotated_image.get_rect(center=pivot+rotated_offset)
    return rotated_image, rect  # Return the rotated image and shifted rect.


'''