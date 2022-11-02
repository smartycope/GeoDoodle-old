from pathlib import Path
from Settings import Settings

class _Singleton():
    dir = Path(__file__).resolve().parent.parent

    debugging = __debug__ and False
    testing   = debugging and False

    assets = dir / 'assets/'
    ui = dir / 'ui/'

    mainWindow = None

    settings = Settings('GeoDoodle')

Singleton = _Singleton()
