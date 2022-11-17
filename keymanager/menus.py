from functools import partial

from PySide6.QtGui import QAction
from PySide6.QtWidgets import QMenu, QMessageBox, QInputDialog, QLineEdit
import qtawesome as qta

from keymanager.dialogs import show_add_key_dialog, KeyMgrDialog, KeyCreateDialog
from keymanager.key import KEY_CACHE, Key
from keymanager.utils import getIcon

SHORTCUTS = {
    'add_key': 'Ctrl+Shift+A',
    'manage_key': 'Ctrl+Shift+M',
    'create_key': 'Ctrl+Shift+C',
}


def add_keymanager_menu(sub_menu:QMenu, parent):

    add_key_action = QAction('添加密钥', parent)
    add_key_action.setShortcut(SHORTCUTS['add_key'])
    add_key_action.triggered.connect(partial(add_key, parent=parent))
    add_key_action.setIcon(getIcon('add_key'))

    create_key_action = QAction('创建密钥', parent)
    create_key_action.setShortcut(SHORTCUTS['create_key'])
    create_key_action.triggered.connect(partial(create_key, parent=parent))

    create_key_action.setIcon(getIcon('create_key'))

    manage_key_action = QAction('管理密钥', parent)
    manage_key_action.setShortcut(SHORTCUTS['manage_key'])
    manage_key_action.triggered.connect(open_mgr)
    manage_key_action.setIcon(getIcon('manage_key'))

    sub_menu.addAction(add_key_action)
    sub_menu.addAction(create_key_action)
    sub_menu.addAction(manage_key_action)

    choose_key_menus = sub_menu.addMenu('密钥选择')

    sub_menu.addMenu(choose_key_menus)

    choose_key_menus.aboutToShow.connect(partial(config_menu, key_menu=choose_key_menus, parent=parent))

    return sub_menu


def config_menu(key_menu:QMenu, parent):
    key_menu.clear()
    desc = QAction(qta.icon('fa.info-circle'), '选择一个密钥', parent)
    desc.setEnabled(False)
    key_menu.addAction(desc)
    key_menu.addSeparator()

    cache = KEY_CACHE

    key_list = cache.get_key_list()
    current_key = cache.get_cur_key()

    for key in key_list:
        key_check_action = QAction(key.name, parent)
        if not key.timeout:
            key_check_action.triggered.connect(partial(select_key, key=key))
        else:
            key_check_action.triggered.connect(partial(reload_key, key=key, parent=parent))
        key_menu.addAction(key_check_action)

        if current_key is not None and key.id == current_key.id:
            if key.timeout:
                key_check_action.setIcon(
                    qta.icon('fa.check', 'fa.warning',
                             options=[{'scale_factor': 1},
                                      {'scale_factor': 0.5, 'offset': (0.25, 0.2), 'color': '#993324'}])
                )
            else:
                key_check_action.setIcon(qta.icon('fa.check'))
        else:
            if key.timeout:
                key_check_action.setIcon(qta.icon('fa.warning', options=[{'color': '#993324'}]))

    if len(key_list) == 0:
        no_key_action = QAction('<没有已经加载的密钥>', parent)
        no_key_action.setEnabled(False)
        key_menu.addAction(no_key_action)


def add_key(parent):
    key:Key = show_add_key_dialog(parent)
    if key is not None:
        result = QMessageBox.question(parent, '成功', '是否设置为激活的密钥？', QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if result == QMessageBox.StandardButton.Yes:
            activate_key(key, parent)
        else:
            QMessageBox.information(parent, '成功', '密钥已加载成功')


def create_key(parent):
    cache = KEY_CACHE
    createDialog = KeyCreateDialog(parent)
    createDialog.setWindowIcon(getIcon('create_key'))
    createDialog.exec()
    key = createDialog.key
    if key is None:
        return
    cache.add_key(key)
    result = QMessageBox.question(parent, '成功', '密钥创建成功，是否设置为激活的密钥？',
                                  QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
    if result == QMessageBox.StandardButton.Yes:
        activate_key(key, parent)
    else:
        QMessageBox.information(parent, '成功', '密钥已加载成功')


def activate_key(key, parent):
    select_key(key)
    cache = KEY_CACHE
    current_key = cache.get_cur_key()
    if current_key.id == key.id:
        QMessageBox.information(parent, '成功', '密钥已加载成功并激活')
    else:
        QMessageBox.critical(parent, '错误', '密钥激活失败，未知原因')


def open_mgr(parent=None):
    kmd = KeyMgrDialog()
    kmd.setWindowIcon(getIcon('manage_key'))
    kmd.exec()
    kmd.destroy()


def select_key(key: Key):
    cache = KEY_CACHE
    cache.set_current_key(key)


def reload_key(key: Key, parent):
    password = None
    if Key.need_password(key.path):
        ok_pressed = True
        while ok_pressed:
            password, ok_pressed = QInputDialog.getText(parent, "需要密码", "输入密码：", QLineEdit.Password, "")
            if ok_pressed:
                illegal, msg = Key.is_password_illegal(password)
                if illegal:
                    QMessageBox.information(parent, '错误', msg)
                    continue
                break
            else:
                return

    try:
        key.load(key.path, password)
        current_key = KEY_CACHE.get_cur_key()
        if current_key.id != key.id:
            result = QMessageBox.question(parent, '成功', '是否设置为激活的密钥？', QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if result == QMessageBox.StandardButton.Yes:
                activate_key(key, parent)
                QMessageBox.information(parent, '成功', '密钥已加载成功并激活')
            else:
                QMessageBox.information(parent, '成功', '密钥已加载成功')
        else:
            QMessageBox.information(parent, '成功', '密钥已重新加载成功')
    except Exception as e:
        QMessageBox.critical(parent, '错误', '不是有效的密钥文件<br/>' + str(e))
        return

def set_add_key_shortcut(shortcut:str):
    SHORTCUTS['add_key'] = shortcut


def set_manage_key_shortcut(shortcut:str):
    SHORTCUTS['manage_key'] = shortcut


def set_create_key_shortcut(shortcut:str):
    SHORTCUTS['create_key'] = shortcut
