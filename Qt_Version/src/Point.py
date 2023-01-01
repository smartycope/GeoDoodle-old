import math
# from Transformation import Transformation
from copy import copy
from random import randint
import numpy as np

from Cope import debug, depricated, untested, todo
from PyQt6.QtCore import QPoint, QPointF, QSize, QSizeF

class Point(QPointF):
    castType = float
    def _initCopy(self, x, y):
        return type(self)(x, y)
    def __init__(self, x=0, y=None):
        def setxy(x, y):
            super(Point, self).__init__(x, y)
            self.x, self.y = x, y
        try:
            if y is None:
                setxy(*self._interpretParams(x))
            else:
                setxy(self.castType(x), self.castType(y))
        except ValueError:
            setxy(x, y)
    def _interpretParams(self, value):
        # We were given 1 value
        try:
            # It has an x and y, and they're NOT functions
            if (hasattr(value, 'x') and hasattr(value, 'y')) and not \
               (callable(getattr(value, 'x')) and callable(getattr(value, 'y'))):
                return self.castType(value.x), self.castType(value.y)
            # It has an x and y, and they ARE functions
            elif (hasattr(value, 'x') and hasattr(value, 'y')) and \
                 (callable(getattr(value, 'x')) and callable(getattr(value, 'y'))):
                return self.castType(value.x()), self.castType(value.y())
            # It's a numpy array
            elif isinstance(value, np.ndarray):
                # [[x],
                #  [y]]
                if np.shape(value) in ((2, 1), (3, 1)):
                    return self.castType(value[0, 0]), self.castType(value[1, 0])
                # [x, y]
                elif np.shape(value) in ((1, 2), (1, 3)):
                    return self.castType(value[0]), self.castType(value[1])
                else:
                    raise ValueError(f"Unable to interpret {value} as a Point")
            # It has the x[] operator overloaded
            elif hasattr(value, '__getitem__') and not isinstance(value, (np.floating, np.integer)):
                return self.castType(value[0]), self.castType(value[1])
            # It's of type QSize
            elif isinstance(value, (QSize, QSizeF)):
                return self.castType(value.width()), self.castType(value.height())
            # It's a scalar
            else:
                return self.castType(value), self.castType(value)
        except:
            raise ValueError(f"Unable to interpret {value} of type {type(value)} as a Point")

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
    def __div__(self, value):
        x, y = self._interpretParams(value)
        return self._initCopy(self.x / x, self.y / y)
    def __truediv__(self, value):
        x, y = self._interpretParams(value)
        return self._initCopy(self.x / x, self.y / y)
    def __mod__(self, value):
        x, y = self._interpretParams(value)
        return self._initCopy(self.x % x, self.y % y)
    def __floordiv__(self, value):
        x, y = self._interpretParams(value)
        return self._initCopy(self.x // x, self.y // y)
    def __divmod__(self, value):
        x, y = self._interpretParams(value)
        NotImplemented
        # return self._initCopy(self.x.__divmod__, y)
    def __pow__(self, value):
        x, y = self._interpretParams(value)
        return self._initCopy(self.x ** x, self.y ** y)
    def __matmul__(self, mat):
        debug(mat)
        return self._initCopy(mat @ self.asArray(), None)

    def __radd__(self, value):
        x, y = self._interpretParams(value)
        return self._initCopy(x + self.x, y + self.y)
    def __rsub__(self, value):
        x, y = self._interpretParams(value)
        return self._initCopy(x - self.x, y - self.y)
    def __rmul__(self, value):
        x, y = self._interpretParams(value)
        return self._initCopy(x * self.x, y * self.y)
    def __rdiv__(self, value):
        x, y = self._interpretParams(value)
        return self._initCopy(y / self.x, y / self.y)
    def __rtruediv__(self, value):
        x, y = self._interpretParams(value)
        return self._initCopy(x / self.x, y / self.y)
    def __rmod__(self, value):
        x, y = self._interpretParams(value)
        return self._initCopy(x % self.x, y % self.y)
    def __rfloordiv__(self, value):
        x, y = self._interpretParams(value)
        return self._initCopy(x // self.x, y // self.y)
    def __rdivmod__(self, value):
        x, y = self._interpretParams(value)
        NotImplemented
        # return self._initCopy(self.x.__divmod__, y)
    def __rpow__(self, value):
        x, y = self._interpretParams(value)
        return self._initCopy(x ** self.x, y ** self.y)
    def __rmatmul__(self, mat):
        debug(mat)
        return self._initCopy(self.asArray() @ mat, None)

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
        return debug(self, clr=3)
    def __itruediv__(self, value):
        x, y = self._interpretParams(value)
        self.x /= x
        self.y /= y
        return self
    def __imod__(self, value):
        x, y = self._interpretParams(value)
        self.x %= x
        self.y %= y
        return self
    def __ifloordiv__(self, value):
        x, y = self._interpretParams(value)
        self.x //= x
        self.y //= y
        return self
    def __idivmod__(self, value):
        x, y = self._interpretParams(value)
        NotImplemented
    def __ipow__(self, value):
        x, y = self._interpretParams(value)
        self.x **= x
        self.y **= y
        return self
    def __imatmul__(self, mat):
        debug(mat)
        transformed = mat @ self.asArray()
        self.x = transformed[0, 0]
        self.y = transformed[1, 0]
        return self

    def __neg__(self):
        # debug(trace=True)
        # self.x = -self.x
        # self.y = -self.y
        return self._initCopy(-self.x, -self.y)
    def __abs__(self):
        # self.x = abs(self.x)
        # self.y = abs(self.y)
        # return self
        return self._initCopy(abs(self.x), abs(self.y))
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
    def __round__(self, n=None):
        self.x = round(self.x, n)
        self.y = round(self.y, n)
        return self
    def __ceil__(self, n=0):
        return self._initCopy(math.ceil(self.x), math.ceil(self.y))
    def __floor__(self, n=0):
        return self._initCopy(math.floor(self.x), math.floor(self.y))
    def __trunc__(self, n=0):
        return self._initCopy(math.trunc(self.x), math.trunc(self.y))

    # These are already methods of QPointF
    # def transpose(self):
        # x = self.x
        # self.x = self.y
        # self.y = x
    # def transposed(self):
        # return self._initCopy(self.y, self.x)
    def data(self):
        return (self.x, self.y)
    def copy(self):
        return self._initCopy(self.x, self.y)
    def asArray(self, vertical=True):
        if vertical:
            return np.array([[self.x], [self.y], [1]], dtype=self.castType)
        else:
            return np.array([self.x, self.y, 1], dtype=self.castType)

    def transformed(self, mat:np.ndarray) -> 'Point':
        new = mat @ self.asArray()
        return self._initCopy(new[0, 0], new[1, 0])
    def transform(self, mat:np.ndarray):
        new = mat @ self.asArray()
        self.x = new[0, 0]
        self.y = new[1, 0]

    @property
    def width(self):
       return self.x
    @width.setter
    def width(self, to):
       self.x = to
    @property
    def height(self):
       return self.y
    @height.setter
    def height(self, to):
       self.y = to

    def serialize(self):
        return [self.x, self.y]
    @staticmethod
    def deserialize(obj):
        return Point(obj)

@untested
def randomPointf(minX=0, maxX=100, minY=0, maxY=100):
    # TODO This only returns integers at the moment
    raise NotImplementedError
    return Pointf(randint(minX, maxX), randint(minY, maxY))

@untested
def randomPointi(minX=0, maxX=100, minY=0, maxY=100):
    return Pointi(randint(minX, maxX), randint(minY, maxY))

@untested
def isAdj(p1, p2):
    return math.isclose(p1.x, p2.x, abs_tol=1) and math.isclose(p1.y, p2.y, abs_tol=1)

# I'm pretty sure QPoint already implements this somewhere
@depricated
def dist(p1, p2):
    return math.hypot(p2.x - p1.x, p2.y - p1.y)


# I put so much effort into these, I hate to just delete them
'''
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
        # return GLPoint(translate(self.x, 0, width,  -1, 1),
                    #    translate(self.y, 0, height, -1, 1),
                    #    width, height)
        return GLPoint((self.x - (width  / 2)) / (width  / 2),
                       (self.y - (height / 2)) / (height / 2),
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
        # return GLPoint((self.x * self.dotSpread) + self.centerDot.x,
                    #    (self.y * self.dotSpread) + self.centerDot.y,
                    #    width, height)
    def asInf(self, centerDot=None, dotSpread=None):
        if not centerDot:
            centerDot = self.centerDot
        if not dotSpread:
            dotSpread = self.dotSpread
        return InfPoint(self.x, # + (self.centerDot.x - centerDot.x),
                        self.y, # + (self.centerDot.y - centerDot.y),
                        centerDot, dotSpread)
'''
