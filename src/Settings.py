from PyQSettings import PyQSettings, Option, OptionWidgets
from PyQt6.QtGui import QColor, QKeySequence, QBrush, QPen
from PyQt6.QtCore import QStandardPaths, Qt
from pathlib import Path

class Settings(PyQSettings):
    documentsPath = Path(QStandardPaths.standardLocations(QStandardPaths.StandardLocation.DocumentsLocation)[0]).resolve() / 'GeoDoodle'
    defaults = {
        # I would say 4, but moving the focus is very resource intensive with that many dots -- which I need to fix
        'min_scale': 8,
        'max_scale': Option(128, description='Recommended you only use powers of 2', widgetFunc=OptionWidgets.customSpinBox(min=1, max=2**10)),
        'scroll_sensitivity': 5,

        # 'max_scale': Option(128, description='Recommended you only use powers of 2', widgetFunc=lambda *a, **l: OptionWidgets.spinBox(*a, min=1, max=2**10, **k)),
        'paper/dot_size': 1, # Currently unused
        'paper/drag_delay': 7, # Currently unused
        'paper/antialiased': True,
        'paper/export_line_thickness': 2,
        'paper/bounds_size': 4,
        'paper/mirror_line_color': QColor(31, 43, 58),
        'paper/focus_size': 5,
        'paper/background_color': QColor(200, 160, 100),
        'paper/loop_focus': True,
        # Smooth translation is slower, because it has to regenerate or move all the dots every time, and
        #   it has to handle every scroll event instead of collecting them and then translating everyhting
        # TODO: figure out if this is actually being used anywhere (I don't think it is)
        'paper/smooth_translation': True,
        # Just kidding, don't use this, it's conceptually impossible, you'll see why.
        # Or at least, it was. It's still not particularly good
        'paper/use_custom_cursor': True,
        # In milliseconds
        'paper/cursor_snap_delay': 25,
        'paper/auto_imprint_pattern': True,
        'paper/dot_jump_amt': 2,
        'paper/selection_color':  QColor(97, 70, 255, 60),
        'paper/current_pen':      QPen(QColor(0, 0, 0)),
        'paper/dot_color':        QColor(0, 0, 0),
        'paper/focus_color':      QColor(37, 37, 37),
        'paper/bounds_color':     QColor(30, 30, 30, 200),
        'paper/bounds_line_pen':  QPen(QColor(32, 45, 57, 150)),
        'paper/mirror_line_pen':  QPen(QColor(32, 45, 57, 150)),
        'paper/active_copy_pen':  QPen(QColor(30, 30, 30)),

        'window/esc_quits': True,
        'window/resize_with_dotSpread': False,
        'window/color_button_0': QColor('black'),
        'window/color_button_1': QColor('red'),
        'window/color_button_2': QColor('green'),
        'window/color_button_3': QColor('yellow'),
        'window/color_button_4': QColor('orange'),
        'window/color_button_5': QColor('blue'),
        'window/color_button_6': QColor('purple'),
        'window/color_button_7': QColor('white'),
        'window/color_button_8': QColor('brown'),
        'window/color_button_9': QColor('pink'),

        # Pattern Params
        'pattern/xOverlap': 0,
        'pattern/yOverlap': 0,
        'pattern/skip_rows': 1,
        'pattern/skip_columns': 1,
        'pattern/skip_row_amt': 0,
        'pattern/skip_column_amt': 0,
        'pattern/flip_rows': 1,
        'pattern/flip_columns': 1,
        'pattern/flip_row_orient': 0,
        'pattern/flip_column_orient': 0,
        'pattern/rotate_rows': 1,
        'pattern/rotate_columns': 1,
        'pattern/rotate_row_amt': 0,
        'pattern/rotate_column_amt': 0,
        'pattern/shear_rows': 1,
        'pattern/shear_columns': 1,
        'pattern/shear_row_dir': 0,
        'pattern/shear_column_dir': 0,
        'pattern/shear_row_amt': 0,
        'pattern/shear_column_amt': 0,

        'pattern/include_halfsies': False,
        'pattern/simplify_patterns': 0,

        'controls/add_single_line':          QKeySequence(Qt.Key.Key_Space),
        'controls/add_another_line':         QKeySequence(Qt.Key.Key_C),
        'controls/move_up':                  QKeySequence(Qt.Key.Key_Up),
        'controls/jump_up':                  QKeySequence(Qt.Modifier.CTRL | Qt.Key.Key_Up),
        'controls/move_down':                QKeySequence(Qt.Key.Key_Down),
        'controls/jump_down':                QKeySequence(Qt.Modifier.CTRL | Qt.Key.Key_Down),
        'controls/move_left':                QKeySequence(Qt.Key.Key_Left),
        'controls/jump_left':                QKeySequence(Qt.Modifier.CTRL | Qt.Key.Key_Left),
        'controls/move_right':               QKeySequence(Qt.Key.Key_Right),
        'controls/jump_right':               QKeySequence(Qt.Modifier.CTRL | Qt.Key.Key_Right),
        'controls/scale_up':                 QKeySequence('='),
        'controls/scale_down':               QKeySequence('-'),
        'controls/rotate_selection':         QKeySequence('f'),
        'controls/increment_mirror':         QKeySequence(Qt.Key.Key_M),
        'controls/delete':                   QKeySequence(Qt.Key.Key_Q),
        'controls/rotate':                   QKeySequence(Qt.Key.Key_K),
        'controls/specific_erase':           QKeySequence(Qt.Key.Key_E),
        'controls/go_home':                  QKeySequence(Qt.Key.Key_H),
        'controls/cancel':                   QKeySequence(Qt.Key.Key_Escape),
        'controls/clear_selection':          QKeySequence(Qt.Key.Key_Delete),
        'controls/clear_everything':         QKeySequence(Qt.Modifier.CTRL | Qt.Key.Key_Q),
        'controls/copy':                     QKeySequence(Qt.Modifier.CTRL | Qt.Key.Key_C),
        'controls/cut':                      QKeySequence(Qt.Modifier.CTRL | Qt.Key.Key_X),
        'controls/paste':                    QKeySequence(Qt.Modifier.CTRL | Qt.Key.Key_V),
        'controls/undo':                     QKeySequence(Qt.Modifier.CTRL | Qt.Key.Key_Z),
        'controls/redo':                     QKeySequence(Qt.Modifier.CTRL | Qt.Modifier.SHIFT | Qt.Key.Key_Z),
        'controls/debug':                    QKeySequence(Qt.Key.Key_AsciiTilde),

        'files/savePath': documentsPath / 'saves', # Currently unused
        'files/exportPath': documentsPath / 'images', # Currently unused
        'files/loadDir': documentsPath / 'saves',
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.documentsPath.mkdir(parents=True, exist_ok=True)
        self['files/savePath'].mkdir(parents=True, exist_ok=True)
        self['files/exportPath'].mkdir(parents=True, exist_ok=True)
        self['files/loadDir'].mkdir(parents=True, exist_ok=True)
