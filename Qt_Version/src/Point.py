class Point:
    def __init__(self, castType, x, y):
        self.castType = castType
        if type(x) in (Pointi, Pointf) and y is None:
            self.x = self.castType(x.x)
            self.y = self.castType(x.y)
        elif type(x) in (tuple, list) and y is None:
            self.x = self.castType(x[0])
            self.y = self.castType(x[1])
        else:
            try:
                self.x = x.x()
                self.y = x.y()
            except AttributeError:
                if x is None:
                    self.x = None
                else:
                    self.x = self.castType(x)
                if y is None:
                    self.y = None
                else:
                    self.y = self.castType(y)
    def __eq__(self, a):
        try:
            return self.x == a.x and self.y == a.y
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
        if type(value) == Pointi or type(value) == Pointf:
            return Pointi(self.x + value.x, self.y + value.y)
        elif type(value) in [list, tuple]:
            return Pointi(self.x + value[0], self.y + value[1])
        else:
            try:
                return Pointi(self.x + value, self.y + value)
            except:
                raise ValueError
    def __sub__(self, value):
        if type(value) == Pointi or type(value) == Pointf:
            return Pointi(self.x - value.x, self.y - value.y)
        elif type(value) in [list, tuple]:
            return Pointi(self.x - value[0], self.y - value[1])
        else:
            try:
                return Pointi(self.x - value, self.y - value)
            except:
                raise ValueError
    def __mul__(self, value):
        if type(value) == Pointi or type(value) == Pointf:
            return Pointi(self.x * value.x, self.y * value.y)
        elif type(value) in [list, tuple]:
            return Pointi(self.x * value[0], self.y * value[1])
        else:
            try:
                return Pointi(self.x * value, self.y * value)
            except:
                raise ValueError
    def __truediv__(self, value):
        if type(value) == Pointi or type(value) == Pointf:
            return Pointi(self.x / value.x, self.y / value.y)
        elif type(value) in [list, tuple]:
            return Pointi(self.x / value[0], self.y / value[1])
        else:
            try:
                return Pointi(self.x / value, self.y / value)
            except:
                raise ValueError
    def __mod__(self, value):
        if type(value) == Pointi or type(value) == Pointf:
            return Pointi(self.x % value.x, self.y % value.y)
        elif type(value) in [list, tuple]:
            return Pointi(self.x % value[0], self.y % value[1])
        else:
            try:
                return Pointi(self.x % value, self.y % value)
            except:
                raise ValueError
    def __iadd__(self, value):
        if type(value) == Pointi or type(value) == Pointf:
            self.x += self.castType(value.x)
            self.y += self.castType(value.y)
        elif type(value) in [list, tuple]:
            self.x += self.castType(value[0])
            self.y += self.castType(value[1])
        else:
            try:
                self.x += self.castType(value)
                self.y += self.castType(value)
            except:
                raise ValueError
        return self
    def __isub__(self, value):
        if type(value) == Pointi or type(value) == Pointf:
            self.x -= self.castType(value.x)
            self.y -= self.castType(value.y)
        elif type(value) in [list, tuple]:
            self.x -= self.castType(value[0])
            self.y -= self.castType(value[1])
        else:
            try:
                self.x -= self.castType(value)
                self.y -= self.castType(value)
            except:
                raise ValueError
        return self
    def __imul__(self, value):
        if type(value) == Pointi or type(value) == Pointf:
            self.x *= self.castType(value.x)
            self.y *= self.castType(value.y)
        elif type(value) in [list, tuple]:
            self.x *= self.castType(value[0])
            self.y *= self.castType(value[1])
        else:
            try:
                self.x *= self.castType(value)
                self.y *= self.castType(value)
            except:
                raise ValueError
        return self
    def __idiv__(self, value):
        if type(value) == Pointi or type(value) == Pointf:
            self.x /= self.castType(value.x)
            self.y /= self.castType(value.y)
        elif type(value) in [list, tuple]:
            self.x /= self.castType(value[0])
            self.y /= self.castType(value[1])
        else:
            try:
                self.x /= self.castType(value)
                self.y /= self.castType(value)
            except:
                raise ValueError
        return self
    def __imod__(self, value):
        if type(value) == Pointi or type(value) == Pointf:
            self.x %= self.castType(value.x)
            self.y %= self.castType(value.y)
        elif type(value) in [list, tuple]:
            self.x %= self.castType(value[0])
            self.y %= self.castType(value[1])
        else:
            try:
                self.x %= self.castType(value)
                self.y %= self.castType(value)
            except:
                raise ValueError
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
    def data(self):
        return [self.x, self.y]
    def datai(self):
        return [int(self.x), int(self.y)]
    def dataf(self):
        return [float(self.x), float(self.y)]


class Pointi(Point):
    def __init__(self, x=None, y=None):
        super().__init__(int, x, y)

class Pointf(Point):
    def __init__(self, x=None, y=None):
        super().__init__(float, x, y)



from random import randint
import math

# TODO This only returns integers at the moment
def randomPointf(minX=0, maxX=100, minY=0, maxY=100):
    return Pointf(randint(minX, maxX), randint(minY, maxY))

def randomPointi(minX=0, maxX=100, minY=0, maxY=100):
    return Pointi(randint(minX, maxX), randint(minY, maxY))


def isAdj(p1, p2):
    return math.isclose(p1.x, p2.x, abs_tol=1) and math.isclose(p1.y, p2.y, abs_tol=1)


def dist(p1, p2):
    return math.hypot(p2.x - p1.x, p2.y - p1.y)
