from pathlib import Path
from Settings import Settings

class _Singleton():
    dir = Path(__file__).resolve().parent.parent

    debugging = __debug__ and True
    testing   = debugging and False

    assets = dir / 'assets/'
    ui = dir / 'ui/'

    mainWindow = None

    settings = Settings('GeoDoodle')

    VERT = 1
    HORZ = 2

Singleton = _Singleton()
