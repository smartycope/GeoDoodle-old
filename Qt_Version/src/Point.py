from Cope import debug
from enum import Enum, auto
from copy import copy
from random import randint
import math

def translate(value, fromStart, fromEnd, toStart, toEnd):
    return ((abs(value - fromStart) / abs(fromEnd - fromStart)) * abs(toEnd - toStart)) + toStart


class AbstractPoint:
    def __init__(self, x=None, y=None):
        raise NotImplementedError
    def _initCopy(self, x, y):
        return type(self)(x, y)
    def init(self, castType, x, y, system=None):
        self.castType = castType
        try:
            if y is None:
                self.x, self.y = self._interpretParams(x)
            else:
                self.x, self.y = self.castType(x), self.castType(y)
        except ValueError:
            self.x, self.y = x, y
    def _interpretParams(self, value):
        try:
            if (hasattr(value, 'x') and hasattr(value, 'y')) and not \
               (callable(getattr(value, 'x')) and callable(getattr(value, 'y'))):
                return self.castType(value.x), self.castType(value.y)
            elif (hasattr(value, 'x') and hasattr(value, 'y')) and \
                 (callable(getattr(value, 'x')) and callable(getattr(value, 'y'))):
                return self.castType(value.x()), self.castType(value.y())
            elif hasattr(value, '__getitem__'):
                return self.castType(value[0]), self.castType(value[1])
            else:
                return self.castType(value), self.castType(value)
        except:
            raise ValueError
    def __eq__(self, value):
        try:
            x, y = self._interpretParams(value)
            return self.x == x and self.y == y
        except:
            return False
    def __str__(self):
        return f'({self.x}, {self.y})'
    def __repr__(self):
        return f'({self.x}, {self.y})'
    def __getitem__(self, key):
        if key == 0:
            return self.castType(self.x)
        elif key == 1:
            return self.castType(self.y)
        else:
            raise IndexError
    def __setitem__(self, key, value):
        if key == 0:
            self.x = self.castType(value)
        elif key == 1:
            self.y = self.castType(value)
        else:
            raise IndexError
    def __add__(self, value):
        x, y = self._interpretParams(value)
        return self._initCopy(self.x + x, self.y + y)
    def __sub__(self, value):
        x, y = self._interpretParams(value)
        return self._initCopy(self.x - x, self.y - y)
    def __mul__(self, value):
        x, y = self._interpretParams(value)
        return self._initCopy(self.x * x, self.y * y)
    def __truediv__(self, value):
        x, y = self._interpretParams(value)
        return self._initCopy(self.x / x, self.y / y)
    def __mod__(self, value):
        x, y = self._interpretParams(value)
        return self._initCopy(self.x % x, self.y % y)
    def __iadd__(self, value):
        x, y = self._interpretParams(value)
        self.x += x
        self.y += y
        return self
    def __isub__(self, value):
        x, y = self._interpretParams(value)
        self.x -= x
        self.y -= y
        return self
    def __imul__(self, value):
        x, y = self._interpretParams(value)
        self.x *= x
        self.y *= y
        return self
    def __idiv__(self, value):
        x, y = self._interpretParams(value)
        self.x /= x
        self.y /= y
        return self
    def __imod__(self, value):
        x, y = self._interpretParams(value)
        self.x %= x
        self.y %= y
        return self
    def __neg__(self):
        self.x = -self.x
        self.y = -self.y
        return self
    def __pos__(self):
        self.x = abs(self.x)
        self.y = abs(self.y)
        return self
    def __invert__(self):
        self.x = ~self.x
        self.y = ~self.y
        return self
    def __hash__(self):
        return hash((self.x, self.y))
    def translate(self,  fromEndX, fromEndY, fromStartX=0, fromStartY=0, toStartX=-1, toStartY=-1, toEndX=1, toEndY=1):
        """ Clamp a point in place from between (fromStartX/Y and fromEndX/Y) to (toStartX/Y and toEndX/Y)
        """
        raise UserError("Translate doesn't work yet")
        self.x = ((abs(self.x - fromStartX) / abs(fromEndX - fromStartX)) * abs(toEndX - toStartX)) + toStartX
        self.y = ((abs(self.y - fromStartY) / abs(fromEndY - fromStartY)) * abs(toEndY - toStartY)) + toStartY
    def translated(self, fromEndX, fromEndY, fromStartX=0, fromStartY=0, toStartX=-1, toStartY=-1, toEndX=1, toEndY=1):
        """ Clamp the point from between (fromStartX/Y and fromEndX/Y) to (toStartX/Y and toEndX/Y)
        """
        raise UserError("Translated doesn't work yet")
        return self._initCopy(((abs(self.x - fromStartX) / abs(fromEndX - fromStartX)) * abs(toEndX - toStartX)) + toStartX, \
                          ((abs(self.y - fromStartY) / abs(fromEndY - fromStartY)) * abs(toEndY - toStartY)) + toStartY)
    def flip(self):
        x = self.x
        self.x = self.y
        self.y = x
    def flipped(self):
        return self._initCopy(self.y, self.x)
    def data(self):
        return (self.x, self.y)
    def copy(self):
        return self._initCopy(self.x, self.y)


class Size(AbstractPoint):
    def _interpretParams(self, value):
        try:
            if (hasattr(value, 'x') and hasattr(value, 'y')) and not \
               (callable(getattr(value, 'x')) and callable(getattr(value, 'y'))):
                return self.castType(value.x), self.castType(value.y)
            elif (hasattr(value, 'width') and hasattr(value, 'height')) and \
                 (callable(getattr(value, 'width')) and callable(getattr(value, 'height'))):
                return self.castType(value.width()), self.castType(value.height())
            elif hasattr(value, '__getitem__'):
                return self.castType(value[0]), self.castType(value[1])
            else:
                return self.castType(value), self.castType(value)
        except:
            raise ValueError
    def init(self, castType, x, y):
        super().init(castType, x, y)
        self.width =  copy(self.x)
        self.height = copy(self.y)
    def __init__(self, width=None, height=None):
        super().__init__(width, height)

class Sizei(Size):
    def __init__(self, width=None, height=None):
        super().init(int, width, height)

class Sizef(Size):
    def __init__(self, width=None, height=None):
        super().init(float, width, height)



class Point(AbstractPoint):
    def datai(self):
        return (int(self.x), int(self.y))
    def dataf(self):
        return (float(self.x), float(self.y))

class Pointi(Point):
    def __init__(self, x=None, y=None):
        super().init(int, x, y)

class Pointf(Point):
    def __init__(self, x=None, y=None):
        super().init(float, x, y)



class CoordPoint(AbstractPoint):
    def asTL(self, width, height):
        raise NotImplementedError
    def asGL(self, width, height):
        raise NotImplementedError
    def asInf(self, centerDot, dotSpread):
        raise NotImplementedError

class TLPoint(CoordPoint):
    """ Top left origin, from 0-width/height, unit is pixels
    """
    def __init__(self, x=None, y=None, width=None, height=None):
        # Because I want it to be in the order I want it, dang it
        if width is None:
            raise TypeError("__init__() missing 1 required argument: 'width'")
        if height is None:
            raise TypeError("__init__() missing 1 required argument: 'height'")
        self.width = width
        self.height = height
        super().init(int, x, y)
    def _initCopy(self, x, y):
        return TLPoint(x, y, self.width, self.height)
    def asTL(self, width=None, height=None):
        if not width:
            width = self.width
        if not height:
            height = self.height
        return TLPoint(self.x * (self.width  / width),
                       self.y * (self.height / height),
                       width, height)
    def asGL(self, width=None, height=None):
        if not width:
            width = self.width
        if not height:
            height = self.height
        return GLPoint(translate(self.x, 0, width,  -1, 1),
                       translate(self.y, 0, height, -1, 1),
                       width, height)
    def asInf(self, centerDot, dotSpread):
        return InfPoint((self.x - centerDot.x) / dotSpread,
                        (self.y - centerDot.y) / dotSpread,
                         centerDot, dotSpread)

class GLPoint(CoordPoint):
    """ Center origin, from -1-1, unit is float, bounded by canvas size (window size)
    """
    def __init__(self, x=None, y=None, width=None, height=None):
        # Because I want it to be in the order I want it, dang it
        if width is None:
            raise TypeError("__init__() missing 1 required argument: 'width'")
        if height is None:
            raise TypeError("__init__() missing 1 required argument: 'height'")
        self.width = width
        self.height = height
        super().init(float, x, y)
    def _initCopy(self, x, y):
        return GLPoint(x, y, self.width, self.height)
    def asTL(self, width=None, height=None):
        if not width:
            width = self.width
        if not height:
            height = self.height
        return TLPoint(translate(self.x, -1, 1, 0, self.width),
                       translate(self.y, -1, 1, 0, self.height),
                       width, height)
    def asGL(self, width=None, height=None):
        if not width:
            width = self.width
        if not height:
            height = self.height
        return GLPoint(self.x * (self.width  / width),
                       self.y * (self.height / height),
                       width, height)
    def asInf(self, centerDot, dotSpread):
        return self.asTL(self.width, self.height).asInf(centerDot, dotSpread)
        # return InfPoint(translate((self.x - centerDot.x) / dotSpread, 0, self.width,  -1, 1),
        #                 translate((self.y - centerDot.y) / dotSpread, 0, self.height, -1, 1),
        #                 centerDot, dotSpread)

class InfPoint(CoordPoint):
    """ Center dot origin, from -inf-inf, unit is dots
    """
    def __init__(self, x=None, y=None, centerDot=None, dotSpread=None):
        # Because I want it to be in the order I want it, dang it
        if centerDot is None:
            raise TypeError("__init__() missing 1 required argument: 'centerDot'")
        if dotSpread is None:
            raise TypeError("__init__() missing 1 required argument: 'dotSpread'")
        self.centerDot = centerDot
        self.dotSpread = dotSpread
        super().init(int, x, y)
    def _initCopy(self, x, y):
        return InfPoint(x, y, self.centerDot, self.dotSpread)
    def asTL(self, width, height):
        return TLPoint((self.x * self.dotSpread) + self.centerDot.x,
                       (self.y * self.dotSpread) + self.centerDot.y,
                       width, height)
    def asGL(self, width, height):
        return self.asTL(width, height).asGL(width, height) # I'm really lazy
    def asInf(self, centerDot=None, dotSpread=None):
        if not centerDot:
            centerDot = self.centerDot
        if not dotSpread:
            dotSpread = self.dotSpread
        return InfPoint(self.x + (self.centerDot.x - centerDot.x),
                        self.y + (self.centerDot.y - centerDot.y),
                        centerDot, dotSpread)





# TODO This only returns integers at the moment
def randomPointf(minX=0, maxX=100, minY=0, maxY=100):
    raise NotImplementedError
    return Pointf(randint(minX, maxX), randint(minY, maxY))


def randomPointi(minX=0, maxX=100, minY=0, maxY=100):
    return Pointi(randint(minX, maxX), randint(minY, maxY))


def isAdj(p1, p2):
    return math.isclose(p1.x, p2.x, abs_tol=1) and math.isclose(p1.y, p2.y, abs_tol=1)


def dist(p1, p2):
    return math.hypot(p2.x - p1.x, p2.y - p1.y)

'''

from Cope import debug

w=100
h=100
cd=TLPoint(50, 50, w, h)
ds=10

assert cd.x % ds == 0
assert cd.y % ds == 0

tlp = TLPoint(20, 30, w, h)
glp = GLPoint(-.2, .6, w, h)
ifp = InfPoint(-3, 5, cd, ds)

assert tlp.x == 20
assert tlp.y == 30
assert glp.x == -.2
assert glp.y == .6
assert ifp.x == -3
assert ifp.y == 5

assert tlp.data() == (tlp.x, tlp.y) == (20, 30)
assert glp.data() == (glp.x, glp.y) == (-.2, .6)
assert ifp.data() == (ifp.x, ifp.y) == (-3, 5)

assert tlp.asTL(w, h)    == tlp.asTL()  == TLPoint(20, 30, w, h)
assert glp.asGL(w, h)    == glp.asGL()  == GLPoint(-.2, .6, w, h)
assert ifp.asInf(cd, ds) == ifp.asInf() == InfPoint(-3, 5, cd, ds)

debug(tlp.asGL(w, h))
debug(tlp.asInf(cd, ds))

debug(glp.asTL(w, h))
debug(glp.asInf(cd, ds)) #

debug(ifp.asTL(w, h))
debug(ifp.asGL(w, h))
'''