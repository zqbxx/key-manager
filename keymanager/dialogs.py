import os
import sys
from typing import Callable

from PySide2.QtCore import QPoint
from PySide2.QtGui import Qt, QStandardItemModel, QIcon, QStandardItem, QCursor
from PySide2.QtWidgets import QDialog, QFileDialog, QMessageBox, QAbstractItemView, QMenu, QInputDialog, QLineEdit, \
    QProgressDialog, QApplication
from keymanager import iconic
os.environ['QT_API'] = 'PySide2'
import qtawesome as qta
from keymanager.key import (
    Key,
    KEY_CACHE as key_cache,
    start_check_key_thread,
    add_key_invalidate_callback,
    KEY_CHECKER as key_checker, KeyTimeOutException)
from keymanager.ui._KeyCreateDialog import Ui_Dialog as UIKeyCreateDialog
from keymanager.ui._KeyMgrDialog import Ui_Dialog as UIKeyMgrDialog
from keymanager.ui._EncryptFileDialog import Ui_Dialog as UIEncryptFileDialog
from keymanager.encryptor import is_encrypt_data, encrypt_data, decrypt_data, not_encrypt_data
from keymanager.utils import read_file, write_file, ICON_COLOR as icon_color


class KeyCreateDialog(QDialog, UIKeyCreateDialog):

    def __init__(self, parent=None) -> None:
        super().__init__()

        self.parent = parent
        self.setupUi(self)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.btnFileChooser.clicked.connect(self.select_key_path)
        self.btnOk.clicked.connect(self.ok)
        self.btnCancel.clicked.connect(lambda : self.close())
        self.key: Key = None
        self.setWindowTitle('创建密钥')
        self.setModal(True)
        self.show()

    def select_key_path(self):
        file_path, _ = QFileDialog.getSaveFileName(self, '密钥文件位置')
        if file_path is None or len(file_path.strip()) == 0:
            return
        self.txtPath.setText(file_path)

    def check_input(self):
        name = self.txtName.text()
        path = self.txtPath.text()
        password1 = self.txtPassword1.text()
        password2 = self.txtPassword2.text()

        illegal, msg = Key.is_password_illegal(password1)

        if illegal:
            QMessageBox.critical(self, "错误", msg)
            return False

        if password1 != password2:
            QMessageBox.critical(self, "错误", "两次输入的密码不一致")
            return False

        if len(name.strip()) == 0:
            QMessageBox.critical(self, "错误", "名称不能为空")
            return False

        if len(path.strip()) == 0:
            QMessageBox.critical(self, "错误", "路径不能为空")
            return False

        if os.path.exists(path):
            QMessageBox.critical(self, "错误", "目标文件已经存在")
            return False

        return True

    def ok(self):

        if not self.check_input():
            return

        name = self.txtName.text()
        path = self.txtPath.text()
        password1 = self.txtPassword1.text()
        password2 = self.txtPassword2.text()

        self.key = Key()
        self.key.name = name
        self.key.key = os.urandom(32)

        try:
            self.key.save(path, password1)
        except Exception as e:
            QMessageBox.critical(self, "错误", str(e))
            return

        QMessageBox.information(self, '保存成功', '密钥文件已经保存到<br/>' + path)

        self.close()


class KeyMgrDialog(QDialog, UIKeyMgrDialog):

    def __init__(self, parent=None, model=True) -> None:
        super().__init__()

        self.parent = parent
        self.setupUi(self)
        self.setWindowTitle('密钥管理')
        self.setModal(model)

        self.key_list = key_cache.get_key_list()
        self.list_model = None
        self.setup_key_list(self.key_list)

        self.tbCreate.clicked.connect(self.create_key_action)
        self.tbCreate.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.tbCreate.setIcon(qta.icon('ei.file-new', color=icon_color['color'], color_active=icon_color['active']))

        self.tbAdd.clicked.connect(self.add_key_action)
        self.tbAdd.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.tbAdd.setIcon(qta.icon('fa.plus', color=icon_color['color'], color_active=icon_color['active']))

        self.tbRemove.clicked.connect(self.remove_key_action)
        self.tbRemove.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.tbRemove.setIcon(qta.icon('fa.minus', color=icon_color['color'], color_active=icon_color['active']))

        add_key_invalidate_callback(self.key_invalidate)

    def setup_key_list(self, key_list):
        self.keyListView.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.list_model = QStandardItemModel(self.keyListView)
        for key in key_list:
            item = self.make_item(key)
            self.list_model.appendRow(item)
        self.keyListView.setModel(self.list_model)
        self.keyListView.setContextMenuPolicy(Qt.CustomContextMenu)
        self.keyListView.customContextMenuRequested[QPoint].connect(self.context_menu)

    def key_invalidate(self, invalidate_key: Key):
        for i in range(self.list_model.rowCount()):
            key = self.list_model.item(i).data()
            if key.id == invalidate_key.id:
                #self.list_model.item(i).setIcon(qta.icon('fa.warning', color=icon_color))
                self.update_key_icon(self.list_model.item(i))
                return

    def update_key_icon(self, item):
        key = item.data()
        if key.timeout:
            item.setIcon(qta.icon('fa.warning', scale_factor=0.8, color=icon_color['color'], color_active=icon_color['active']))
        elif key_cache.is_cur_key(key):
            item.setIcon(qta.icon('fa.check', scale_factor=0.8, color=icon_color['color'], color_active=icon_color['active']))
        else:
            item.setIcon(QIcon(qta.icon('fa5s.key', scale_factor=0.7, color=icon_color['color'], color_active=icon_color['active'])))

    def make_item(self, key):
        item = QStandardItem(key.name)
        item.setData(key)
        #item.setIcon(QIcon(qta.icon('fa5s.key', color=icon_color)))
        self.update_key_icon(item)
        return item

    def get_selected_item(self):
        selected = self.keyListView.selectedIndexes()
        if not selected:
            return

        index = selected[0]
        item = self.list_model.item(index.row())
        return item

    def context_menu(self, point):

        selected = self.keyListView.selectedIndexes()
        if not selected:
            return

        index = selected[0]
        item = self.list_model.item(index.row())
        key = item.data()

        pop_menu = QMenu()

        _set_default_key_action = pop_menu.addAction(qta.icon('fa.check', color=icon_color['color'], color_active=icon_color['active']), '设为默认')
        if key_cache.is_cur_key(key) or key.timeout:
            _set_default_key_action.setEnabled(False)

        pop_menu.addSeparator()
        _encrypt_files_action = pop_menu.addAction(qta.icon('ei.lock', color=icon_color['color'], color_active=icon_color['active']), "加密文件")
        _decrypt_files_action = pop_menu.addAction(qta.icon('ei.unlock', color=icon_color['color'], color_active=icon_color['active']), "解密文件")
        pop_menu.addSeparator()

        _reload_key_action = pop_menu.addAction(qta.icon('fa.refresh', color=icon_color['color'], color_active=icon_color['active']), "重新加载")
        _reload_key_action.setEnabled(key.timeout)

        selected_action = pop_menu.exec_(QCursor.pos())
        if selected_action == _encrypt_files_action:
            self.encrypt_files_action()
        elif selected_action == _set_default_key_action:
            self.set_default_key_action()
        elif selected_action == _reload_key_action:
            self.reload_key_action()
        elif selected_action == _decrypt_files_action:
            self.decrypt_files_action()

    def set_default_key_action(self, item=None):

        item = self.get_selected_item()
        self._set_default_key(item)
        for i in range(self.list_model.rowCount()):
            self.update_key_icon(self.list_model.item(i))
            #self.list_model.item(i).setIcon(qta.icon('fa5s.key', color=icon_color))

    def create_key_action(self):
        dialog = KeyCreateDialog(parent=self)
        dialog.activateWindow()
        dialog.exec()
        key = dialog.key
        if key is None:
            return
        item = self.make_item(key)
        self._add_key(item, key)

    def _add_key(self, item, key):
        self.list_model.appendRow(item)
        key_cache.add_key(key)

    def _remove_key(self, index):
        self.list_model.removeRow(index)
        key_cache.remove_key(index)

    def _set_default_key(self, item):
        key_cache.set_current_key(item.data())
        self.update_key_icon(item)

    def add_key_action(self):
        file_name, _ = QFileDialog.getOpenFileName(self, '选择密钥文件')

        if len(file_name.strip()) == 0:
            return

        password = None
        if Key.need_password(file_name):
            ok_pressed = True
            while ok_pressed:
                password, ok_pressed = QInputDialog.getText(self, "需要密码", "输入密码：", QLineEdit.Password, "")
                if ok_pressed:
                    illegal, msg = Key.is_password_illegal(password)
                    if illegal:
                        QMessageBox.information(self, '错误', msg)
                        continue
                    break
                else:
                    return

        key = Key()
        try:
            key.load(file_name, password)
        except Exception as e:
            QMessageBox.critical(self, '错误', '不是有效的密钥文件<br/>' + str(e))
            return

        row_len = self.list_model.rowCount()
        for i in range(0, row_len):
            item: QStandardItem = self.list_model.item(i, 0)
            k: Key = item.data()
            if k.id == key.id:
                QMessageBox.information(self, '信息', '相同的密钥已经加载')
                return

        item = self.make_item(key)
        self._add_key(item, key)

        return

    def remove_key_action(self):
        selected = self.keyListView.selectedIndexes()
        if not selected:
            return
        index = selected[0]
        self._remove_key(index.row())
        QMessageBox.information(self, '信息', '密钥已经移除')

    def encrypt_files_action(self):
        item = self.get_selected_item()
        key = item.data()
        ef_dialog = EncryptFileDialog(self)
        ef_dialog.set_key(key)
        ef_dialog.exec()

    def decrypt_files_action(self):
        item = self.get_selected_item()
        key = item.data()
        ef_dialog = EncryptFileDialog(self,
                                      win_title='解密文件',
                                      before_process=is_encrypt_data,
                                      processor=decrypt_data,
                                      success_msg='解密完成',
                                      select_file_dlg_title='选择需要解密的文件',)
        ef_dialog.set_key(key)
        ef_dialog.exec()

    def reload_key_action(self):
        item = self.get_selected_item()
        key: Key = item.data()
        password = None
        if Key.need_password(key.path):
            ok_pressed = True
            while ok_pressed:
                password, ok_pressed = QInputDialog.getText(self, "需要密码", "输入密码：", QLineEdit.Password, "")
                if ok_pressed:
                    illegal, msg = Key.is_password_illegal(password)
                    if illegal:
                        QMessageBox.information(self, '错误', msg)
                        continue
                    break
                else:
                    return

        try:
            key.load(key.path, password)
        except Exception as e:
            QMessageBox.critical(self, '错误', '不是有效的密钥文件<br/>' + str(e))
            return

        self.update_key_icon(item)


class EncryptFileDialog(QDialog, UIEncryptFileDialog):

    def __init__(self,
                 parent=None,
                 win_title='加密文件',
                 before_process: Callable = not_encrypt_data,
                 processor: Callable = encrypt_data,
                 success_msg: str = '加密完成',
                 select_file_dlg_filter: str = 'All Files (*);;Text Files (*.txt)',
                 select_file_dlg_title: str = '选择需要加密的文件',
                 select_output_dir_title: str = '选择输出目录',) -> None:
        super().__init__()

        self.parent = parent
        self.before_process = before_process
        self.processor = processor
        self.success_msg = success_msg
        self.select_file_dlg_filter = select_file_dlg_filter
        self.select_file_dlg_title = select_file_dlg_title
        self.select_output_dir_title = select_output_dir_title

        self.setupUi(self)
        self.setWindowTitle(win_title)
        self.setup_events()
        self.setAttribute(Qt.WA_DeleteOnClose)

        self.key = None
        self.file_list = None
        self.output_dir_path = None

    def setup_events(self):
        self.tbSelectDir.clicked.connect(self.select_output_dir)
        self.tbSelectFiles.clicked.connect(self.select_files)
        self.btnOk.clicked.connect(self.do_it)
        self.btnCancel.clicked.connect(lambda: self.close())

    def set_key(self, key: Key):
        self.key = key

    def select_files(self):
        self.file_list, _ = QFileDialog.getOpenFileNames(self,
                                                    caption=self.select_file_dlg_title,
                                                    filter=self.select_file_dlg_filter)
        if len(self.file_list) == 0:
            return

        self.txtInputFile.setText(';'.join(self.file_list))

    def select_output_dir(self):
        self.output_dir_path = QFileDialog.getExistingDirectory(None, self.select_output_dir_title, "C:/")
        if self.output_dir_path == '' or not os.path.exists(self.output_dir_path):
            return
        self.txtOutputDir.setText(self.output_dir_path)

    def check_input(self):

        if self.output_dir_path is None or self.output_dir_path == '':
            QMessageBox.information(self, '', '输出目录不能为空')
            return False

        if not os.path.exists(self.output_dir_path):
            QMessageBox.information(self, '', '输出目录不存在')
            return False

        if self.file_list is None or len(self.file_list) == 0:
            QMessageBox.information(self, '', '必须选择至少一个文件')
            return False

        return True

    def do_it(self):
        if not self.check_input():
            return
        pd = QProgressDialog(self)
        pd.setMinimumDuration(10)
        pd.setAutoClose(True)
        pd.setAutoReset(False)
        pd.setLabelText('正在处理')
        pd.setCancelButtonText('取消')
        pd.setRange(0, len(self.file_list))
        pd.setValue(0)
        pd.setWindowModality(Qt.WindowModal)
        pd.show()

        try:
            for index, file_path in enumerate(self.file_list):

                if pd.wasCanceled():
                    break

                pd.setLabelText('正在处理 {}/{}'.format(str(index + 1), len(self.file_list)))

                if os.path.exists(file_path):

                    p, n = os.path.split(file_path)
                    file_content = read_file(file_path)

                    if self.before_process(file_content):
                        encrypt_content = self.processor(self.key.key, file_content)
                        output_file = os.path.join(self.output_dir_path, n)
                        write_file(output_file, encrypt_content)

                pd.setValue(pd.value() + 1)

            if not pd.wasCanceled():
                QMessageBox.information(pd, '处理完成', self.success_msg)
            else:
                QMessageBox.information(pd, '已经终止', '用户取消')
        except Exception as e:
            pass
            QMessageBox.critical(pd, '处理失败', str(e))
        pd.close()
        self.close()


def open_encrypt_files_dialog(key: Key,
                              progress_title='正在处理',
                              caption_files='选择需要加密的文件',
                              caption_output_dir='选择输出目录',
                              file_filter='All Files (*);;Text Files (*.txt)',
                              parent=None):
    file_list, _ = QFileDialog.getOpenFileNames(parent, caption=caption_files, filter=file_filter)

    if len(file_list) == 0:
        return

    dir_path = QFileDialog.getExistingDirectory(None, caption_output_dir, "C:/")

    if dir_path == '' or not os.path.exists(dir_path):
        return

    pd = QProgressDialog(parent)
    pd.setMinimumDuration(1000)
    pd.setAutoClose(True)
    pd.setAutoReset(False)
    pd.setLabelText('正在处理')
    pd.setCancelButtonText('取消')
    pd.setRange(0, len(file_list))
    pd.setValue(0)
    pd.setWindowModality(Qt.WindowModal)
    pd.show()

    try:
        for index, file_path in enumerate(file_list):

            if pd.wasCanceled():
                break

            pd.setLabelText('正在处理 {}/{}'.format(str(index + 1), len(file_list)))

            if os.path.exists(file_path):

                p, n = os.path.split(file_path)
                file_content = read_file(file_path)

                if not is_encrypt_data(file_content):
                    encrypt_content = encrypt_data(key.key, file_content)
                    output_file = os.path.join(dir_path, n)
                    write_file(output_file, encrypt_content)

            pd.setValue(pd.value() + 1)

        if not pd.wasCanceled():
            QMessageBox.information(pd, '处理完成', '加密完成')
        else:
            QMessageBox.information(pd, '已经终止', '用户取消')

    except Exception as e:
        pass
        QMessageBox.critical(pd, '处理失败', str(e))

    pd.close()


if __name__ == '__main__':
    key_checker['timeout'] = 60
    start_check_key_thread()
    app = QApplication(sys.argv)
    kmd = KeyMgrDialog()
    kmd.show()
    sys.exit(app.exec_())
