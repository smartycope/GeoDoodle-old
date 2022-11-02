from PyQt6.QtCore import QSettings, QStandardPaths
from PyQt6.QtGui import QColor
from pathlib import Path
from Cope import debug
_type = type

class UnsetSettingWarning(Warning):
    pass

class PyQSettings(QSettings):
    """ A Python-oriented wrapper of the QSettings class.
    """
    defaults = {}
    def __getattr__(self, attr):
        return self.value(attr, self.getDefault(attr), type=_type(self.getDefault(attr)))

    def __setattr__(self, attr, value):
        self.setValue(attr, value)

    def setDefault(self, attr):
        return self.setValue(attr, self.getDefault(attr))

    def getDefault(self, attr):
        if attr not in self.defaults.keys():
            raise UnsetSettingWarning(f"Setting {attr} doesn't have a default!")
        return self.defaults[attr]

    def value(self, attr, default=None, type=None):
        if type is None:
            type = _type(self.getDefault(attr))
        if default is None:
            default = self.getDefault(attr)
        return super().value(attr, default, type=type)

class Settings(PyQSettings):
    documentsPath = Path(QStandardPaths.standardLocations(QStandardPaths.StandardLocation.DocumentsLocation)[0]).resolve() / 'GeoDoodle'
    defaults = {
        # This probably should be under paper, but I don't want to, I use it too much
        'dotSpread': 16,
        'paper/dot_size': 1, # Currently unused
        'paper/drag_delay': 7, # Currently unused
        'paper/antialiased': True,
        'paper/export_line_thickness': 2,
        'paper/bounds_size': 4,
        'paper/mirror_line_color': QColor(31, 43, 58),
        'paper/focus_size': 5,
        'paper/default_background': QColor(200, 160, 100),
        # Smooth translation is slower, because it has to regenerate or move all the dots every time, and
        #   it has to handle every scroll event instead of collecting them and then translating everyhting
        'paper/smooth_translation': True,
        # Just kidding, don't use this, it's conceptually impossible, you'll see why.
        'paper/use_custom_cursor': True,
        'paper/auto_imprint_pattern': True,

        'window/esc_quits': True,
        'window/resize_with_dotSpread': False,

        'pattern/xOverlap': 0,
        'pattern/yOverlap': 0,
        'pattern/include_halfsies': False,
        'pattern/skip_rows': 1,
        'pattern/skip_columns': 1,
        'pattern/skip_row_amt': 0,
        'pattern/skip_column_amt': 0,
        'pattern/flip_rows': 1,
        'pattern/flip_columns': 1,
        'pattern/flip_row_orient': None,
        'pattern/flip_column_orient': None,

        'savePath': documentsPath / 'saves', # Currently unused
        'exportPath': documentsPath / 'images', # Currently unused
        'loadDir': documentsPath / 'saves', # Currently unused
    }

# Testing
# settings = Settings("GeoDoodle")
# settings.dotSpread = 16
# debug(settings.dotSpread)
# debug(settings.value('dotSpread'))
# debug(settings.value('dotSpread', type=float))
# debug(settings.value('paper/antialiased'))
# settings.antialiased
# print(settings.dotSpread)
