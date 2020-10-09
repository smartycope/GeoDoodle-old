class Color:
    def __init__(self, r = 0, g = 0, b = 0, a = 255):
        self.r = r
        self.g = g
        self.b = b
        self.a = a
        self.color = (self.r, self.g, self.b, self.a)
    
def namedColor(color):
    color = color.lower()
    if color == 'red':
        return Color(255, 0, 0)
    if color == 'blue':
        return Color(0, 0, 255)
    if color == 'green':
        return Color(0, 255, 0)
    if color == 'white':
        return Color(255, 255, 255)
    if color == 'black':
        return Color()
    if color == 'paper':
        return Color(200, 160, 100)
