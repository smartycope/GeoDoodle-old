import sys
from PyQt5.QtWidgets import QApplication
from Game import Game

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Game()
    window.show()
    app.exec()
