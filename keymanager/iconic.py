import PySide2
from PySide2.QtCore import QSize, Qt, QRect, QPoint
from PySide2.QtGui import QPixmap, QPainter, QIcon
import os
os.environ['QT_API'] = 'PySide2'
import qtawesome as qta
from qtawesome import IconicFont


width = 32
height = 32

# 解决nuitka编译后qtawesome报错
# NotImplementedError pure virtual method 'QIconEngine.paint()' not implemented.
class PySide2IconicFont(IconicFont):

    def _icon_by_painter(self, painter, options):
        size = QSize(width, height)
        pm = QPixmap(size)
        pm.fill(Qt.transparent)
        painter.paint(self, QPainter(pm), QRect(QPoint(0, 0), size), PySide2.QtGui.QIcon.Mode.Normal,
                      PySide2.QtGui.QIcon.State.Off, options)
        return QIcon(pm)


from qtawesome import _resource, has_valid_font_ids


def _instance():
    """
    Return the singleton instance of IconicFont.

    Functions ``icon``, ``load_font``, ``charmap``, ``font`` and
    ``set_defaults`` all rebind to methods of the singleton instance of IconicFont.
    """
    if (
            _resource['iconic'] is not None
            and not has_valid_font_ids(_resource['iconic'])
    ):
        # Reset cached instance
        _resource['iconic'] = None

    if _resource['iconic'] is None:
        _resource['iconic'] = PySide2IconicFont(
            ('fa',
             'fontawesome4.7-webfont.ttf',
             'fontawesome4.7-webfont-charmap.json'),
            ('fa5',
             'fontawesome5-regular-webfont.ttf',
             'fontawesome5-regular-webfont-charmap.json'),
            ('fa5s',
             'fontawesome5-solid-webfont.ttf',
             'fontawesome5-solid-webfont-charmap.json'),
            ('fa5b',
             'fontawesome5-brands-webfont.ttf',
             'fontawesome5-brands-webfont-charmap.json'),
            ('ei', 'elusiveicons-webfont.ttf', 'elusiveicons-webfont-charmap.json'),
            ('mdi', 'materialdesignicons5-webfont.ttf',
             'materialdesignicons5-webfont-charmap.json'),
            ('mdi6', 'materialdesignicons6-webfont.ttf',
             'materialdesignicons6-webfont-charmap.json'),
            ('ph', 'phosphor.ttf', 'phosphor-charmap.json'),
            ('ri', 'remixicon.ttf', 'remixicon-charmap.json'),
            ('msc', 'codicon.ttf', 'codicon-charmap.json'),
        )
    return _resource['iconic']


qta._instance = _instance