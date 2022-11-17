import copy
import importlib

from PySide6.QtGui import QIcon

from keymanager import _HEAD_MARKER_BYTE_SIZE
import appdirs
import os


ICON_COLOR = {
    'color':  '#0099CC',
    'active': '#0099CC',
}


def write_file(path: str, bs: bytes):
    with open(path, 'wb') as f:
        f.write(bs)


def read_file(path: str):
    with open(path, 'rb') as f:
        return f.read()


def read_header(path: str):
    with open(path, 'rb') as f:
        return f.read(_HEAD_MARKER_BYTE_SIZE)


def get_user_data_dir():
    user_dir = appdirs.user_data_dir('keymanager', 'wx_c')
    if not os.path.exists(user_dir):
        os.makedirs(user_dir)
    return os.path.abspath(user_dir)


def get_md5_data_dir():
    md5_dir = os.path.join(get_user_data_dir(), 'md5')
    if not os.path.exists(md5_dir):
        os.makedirs(md5_dir)
    return md5_dir


icons = {
    'add_key': {
        'names':('ei.key','ri.add-circle-fill',),
        'options':[{'rotated':-45,'offset': (-0.1, -0.15), 'scale_factor':0.9, 'color': ICON_COLOR['color']},
                   {'scale_factor': 0.68, 'offset': (0.25, 0.2), 'color': '#59a869'}]
    },
    'create_key': {
        'names':('ei.key','ph.star-four-fill','ph.star-four-fill',),
        'options':[{'rotated':-45,'offset': (-0.1, -0.15), 'scale_factor':0.9, 'color': ICON_COLOR['color']},
                   {'scale_factor': 0.5, 'offset': (0.22, 0.2), 'color': '#f5c43c'},
                   {'scale_factor': 0.3, 'offset': (0.4, 0), 'color': '#f5c43c'}],

    },
    'manage_key': {
        'names': ('ei.key',),
        'options':[{'rotated': -45, 'scale_factor': 1.1, 'color': ICON_COLOR['color']}],
    },

    'remove_key': {
        'names':('ei.key','fa.remove',),
        'options':[{'rotated':-45,'offset': (-0.1, -0.15), 'scale_factor':0.9, 'color': ICON_COLOR['color']},
                   {'scale_factor': 0.68, 'offset': (0.25, 0.2), 'color': '#db5860'}]
    }

}

external_module_name = ''
get_icon_func_name = ''
get_icon_opt_func_name = ''
get_icon_name_func_name = ''

def getIconConfig(name: str):

    from typing import List, Any

    try:
        external = importlib.import_module(external_module_name)
        module = external.__dict__
        getIconExternal = module[get_icon_func_name]
        getIconOptExternal = module[get_icon_opt_func_name]
        getIconNameExternal = module[get_icon_name_func_name]
    except:
        def _1(_: str) -> QIcon: ...
        def _2(_: str) -> tuple[str, str]: ...
        def _3(_: str) -> tuple[dict[str, Any]]: ...
        getIconExternal = _1
        getIconNameExternal = _2
        getIconOptExternal = _3

    if name not in icons:
        return None

    icon_config = icons[name]

    names = getIconNameExternal(name)

    if names is None:
        names = icon_config['names']

    options = getIconOptExternal(name)

    if options is None:
        options = icon_config['options']
    elif len(options) != len(icon_config['options']):
        raise Exception('图标的option长度不一致')
    else:
        newopt:List[dict[str, str]] = []
        for e, c in zip(options, icon_config['options']):
            option:dict = copy.deepcopy(c)
            option.update(copy.deepcopy(e))
            newopt.append(option)
        options = newopt

    return {'names': names, 'options': options}


def getIcon(name: str):
    import qtawesome as qta
    icon_config = getIconConfig(name)
    return qta.icon(*icon_config['names'], options=icon_config['options'])
