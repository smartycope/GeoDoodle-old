class Point:
    def __init__(self, x = -1, y = -1):
        self.x = int(x)
        self.y = int(y)
    def __eq__(self, a):
        try:
            return self.x == a.x and self.y == a.y
        except:
            return False
    def __str__(self):
        return f'({self.x}, {self.y})'
    def data(self):
        return [self.x, self.y]