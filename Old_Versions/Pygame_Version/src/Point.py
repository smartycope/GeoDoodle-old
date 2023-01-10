class Point:
    def __init__(self, x = None, y = None):
        if type(x) == Point and y is None:
            self.x = x.x
            self.y = x.y
        elif (type(x) == tuple or type(x) == list) and y is None:
            self.x = x[0]
            self.y = x[1]
        else:
            if x is None:
                self.x = None
            else:
                self.x = int(x)
                
            if y is None:
                self.y = None
            else:
                self.y = int(y)
    def __eq__(self, a):
        try:
            return self.x == a.x and self.y == a.y
        except:
            return False
    def __str__(self):
        return f'({self.x}, {self.y})'
    def __getitem__(self, key):
        if key == 0:
            return self.x
        elif key == 1:
            return self.y
        else:
            raise IndexError
    def __setitem__(self, key, value):
        if key == 0:
            self.x = value
        elif key == 1:
            self.y = value
        else:
            raise IndexError
    def __add__(self, value):
        if type(value) == Point:
            return Point(self.x + value.x, self.y + value.y)
        else:
            try:
                return Point(self.x + value, self.y + value)
            except:
                raise ValueError
    def __sub__(self, value):
        if type(value) == Point:
            return Point(self.x - value.x, self.y - value.y)
        else:
            try:
                return Point(self.x - value, self.y - value)
            except:
                raise ValueError
    def __mul__(self, value):
        if type(value) == Point:
            return Point(self.x * value.x, self.y * value.y)
        else:
            try:
                return Point(self.x * value, self.y * value)
            except:
                raise ValueError
    def __truediv__(self, value):
        if type(value) == Point:
            return Point(self.x / value.x, self.y / value.y)
        else:
            try:
                return Point(self.x / value, self.y / value)
            except:
                raise ValueError
    def __mod__(self, value):
        if type(value) == Point:
            return Point(self.x % value.x, self.y % value.y)
        else:
            try:
                return Point(self.x % value, self.y % value)
            except:
                raise ValueError
    def __iadd__(self, value):
        if type(value) == Point:
            self.x += value.x
            self.y += value.y
        else:
            try:
                self.x += value
                self.y += value
            except:
                raise ValueError
        return self
    def __isub__(self, value):
        if type(value) == Point:
            self.x -= value.x
            self.y -= value.y
        else:
            try:
                self.x -= value
                self.y -= value
            except:
                raise ValueError
        return self
    def __imul__(self, value):
        if type(value) == Point:
            self.x *= value.x
            self.y *= value.y
        else:
            try:
                self.x *= value
                self.y *= value
            except:
                raise ValueError
        return self
    def __idiv__(self, value):
        if type(value) == Point:
            self.x /= value.x
            self.y /= value.y
        else:
            try:
                self.x /= value
                self.y /= value
            except:
                raise ValueError
        return self
    def __imod__(self, value):
        if type(value) == Point:
            self.x %= value.x
            self.y %= value.y
        else:
            try:
                self.x %= value
                self.y %= value
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
    def data(self):
        return [self.x, self.y]