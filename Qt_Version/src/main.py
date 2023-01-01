import sys
from PyQt6.QtWidgets import QApplication
from Window import Window

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Window()
    window.show()
    app.exec()




"""
To find the polygon that encloses an area on a canvas, you can use a technique called "polygonization" or "contour tracing". This involves tracing the edges of the lines on the canvas to create a polygon that encloses the area. There are many different algorithms that can be used for this, but one common approach is to use a "marching squares" algorithm. This involves dividing the canvas into a grid of squares and then using a set of rules to determine which lines intersect each square, and then connecting those intersections to create a polygon.
 """

"""
import numpy as np
from PyQt6.QtGui import QImage

# Create a QImage representing the canvas
canvas_width = 100
canvas_height = 100
canvas_image = QImage(canvas_width, canvas_height, QImage.Format_ARGB32)

# Create a numpy array representing the lines on the canvas
lines = np.zeros((canvas_height, canvas_width))

# Set the pixels that represent the lines in the numpy array
# (In this example, we will use a simple horizontal line at y = 50)
line_y = 50
lines[line_y, :] = 1

# Create a numpy array to hold the polygon that encloses the lines
polygon = np.zeros((canvas_height, canvas_width))

# Create a numpy array that will hold the "state" of each square in the grid
# (This is used by the marching squares algorithm to determine which lines intersect each square)
grid_state = np.zeros((canvas_height - 1, canvas_width - 1))

# Loop over each square in the grid and determine its state
for y in range(canvas_height - 1):
    for x in range(canvas_width - 1):
        # Get the value of each corner of the square
        top_left = lines[y, x]
        top_right = lines[y, x + 1]
        bottom_left = lines[y + 1, x]
        bottom_right = lines[y + 1, x + 1]

        # Determine the state of the square based on the values of its corners
        # (This uses the "marching squares" rules to determine which lines intersect the square)
        state = 0
        if top_left == 1:
            state |= 1
        if top_right == 1:
            state |= 2
        if bottom_right == 1:
            state |= 4
        if bottom_left == 1:
            state |= 8
        grid_state[y, x] = state

# Loop over each square in the grid again, this time using the state of the square
# to determine which lines intersect it, and then adding those lines to the polygon
for y in range(canvas_height - 1):
    for x in range(canvas_width - 1):
        # Get the state of the current square
        state = grid_state[y, x]

        # Get the coordinates of the center of the square
        center_x = x + 0.5
        center_y = y + 0.5

        # Use the state of the square to determine which lines intersect it,
        # and add those lines to the polygon
        if state == 1:
            polygon[y, x] = 1
            polygon[y, x + 1] = 1
        elif state == 2:
            polygon[y, x + 1] = 1
            polygon[y + 1, x + 1] = 1
        elif state == 3:
            polygon[y, x] = 1
            polygon[y, x + 1] = 1
            polygon[y +
 """
