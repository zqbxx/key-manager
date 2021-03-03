import os
import sys
from PyQt5.QtWidgets import QApplication, QMenu

from PyQt5.QtCore import Qt, QThread, QPoint
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QCursor, QIcon
from PyQt5.QtWidgets import (
    QDialog,
    QProgressDialog,
    QFileDialog,
    QMessageBox,
    QAbstractItemView,
    QInputDialog,
    QLineEdit,
)

import qtawesome as qta

from keymanager.key import Key, KEY_CACHE as key_cache
from keymanager.ui._KeyCreateDialog import Ui_Dialog as UIKeyCreateDialog
from keymanager.ui._KeyMgrDialog import Ui_Dialog as UIKeyMgrDialog
from keymanager.ui._EncryptFileDialog import Ui_Dialog as UIEncryptFileDialog
from keymanager.encryptor import is_encrypt_data, encrypt_data_with_head
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
            QMessageBox.critical(self, "错误", repr(e))
            return

        QMessageBox.information(self, '保存成功', '密钥文件已经保存到<br/>' + path)

        self.close()


class KeyMgrDialog(QDialog, UIKeyMgrDialog):

    def __init__(self, parent=None) -> None:
        super().__init__()

        self.parent = parent
        self.setupUi(self)
        self.setWindowTitle('密钥管理')
        self.setModal(True)

        self.key_list = key_cache.get_key_list()
        self.setup_key_list(self.key_list)

        self.tbCreate.clicked.connect(self.create_key_action)
        self.tbCreate.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.tbCreate.setIcon(qta.icon('ei.file-new', color=icon_color))

        self.tbAdd.clicked.connect(self.add_key_action)
        self.tbAdd.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.tbAdd.setIcon(qta.icon('fa.plus', color=icon_color))

        self.tbRemove.clicked.connect(self.remove_key_action)
        self.tbRemove.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.tbRemove.setIcon(qta.icon('fa.minus', color=icon_color))

    def setup_key_list(self, key_list):
        self.keyListView.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.list_model = QStandardItemModel(self.keyListView)
        for key in key_list:
            item = self.make_item(key)
            self.list_model.appendRow(item)
        self.keyListView.setModel(self.list_model)
        self.keyListView.setContextMenuPolicy(Qt.CustomContextMenu)
        self.keyListView.customContextMenuRequested[QPoint].connect(self.context_menu)

    def make_item(self, key):
        item = QStandardItem(key.name)
        item.setData(key)
        item.setIcon(QIcon(qta.icon('fa5s.key', color=icon_color)))
        return item

    def context_menu(self, point):

        pop_menu = QMenu()
        set_default_action = pop_menu.addAction(qta.icon('fa.check', color=icon_color), '设为默认')
        encrypt_action = pop_menu.addAction(qta.icon('ei.lock', color=icon_color), "加密文件")
        decrypt_action = pop_menu.addAction(qta.icon('ei.unlock', color=icon_color), "解密文件")

        selected_action = pop_menu.exec_(QCursor.pos())
        if selected_action == encrypt_action:
            self.encrypt_files_action()
        elif selected_action == set_default_action:
            self.set_default_key_action()

    def set_default_key_action(self):

        selected = self.keyListView.selectedIndexes()
        if selected:
            index = selected[0]
            for i in range(self.list_model.rowCount()):
                self.list_model.item(i).setIcon(qta.icon('fa5s.key', color=icon_color))
            selected_item = self.list_model.item(index.row())
            self._set_default_key(selected_item)

    def create_key_action(self):
        dialog = KeyCreateDialog(parent=self)
        dialog.exec()
        key = dialog.key
        if key is None:
            return
        item = self.make_item(key)
        self._add_key(item, key)

    def _add_key(self, item, key):
        self.list_model.appendRow(item)
        self.key_list.append(key)

    def _remove_key(self, index):
        self.list_model.removeRow(index)
        del self.key_list[index]

    def _set_default_key(self, item):
        item.setIcon(qta.icon('fa.check', color=icon_color))
        key_cache.set_current_key(item.data())

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
            QMessageBox.critical(self, '错误', '不是有效的密钥文件<br/>' + repr(e))
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
        selected = self.keyListView.selectedIndexes()
        if not selected:
            return
        index = selected[0]
        item = self.list_model.item(index.row())
        key = item.data()
        ef_dialog = EncryptFileDialog(self)
        ef_dialog.set_key(key)
        ef_dialog.exec()


class EncryptFileDialog(QDialog, UIEncryptFileDialog):

    def __init__(self, parent=None) -> None:
        super().__init__()
        self.setWindowTitle('加密文件')
        self.parent = parent
        self.setupUi(self)
        self.setAttribute(Qt.WA_DeleteOnClose)

        self.tbSelectDir.clicked.connect(self.select_output_dir)
        self.tbSelectFiles.clicked.connect(self.select_files)

        self.btnOk.clicked.connect(self.encrypt)
        self.btnCancel.clicked.connect(lambda: self.close())

        self.key = None
        self.file_list = None
        self.output_dir_path = None

    def set_key(self, key: Key):
        self.key = key

    def select_files(self):
        self.file_list, _ = QFileDialog.getOpenFileNames(self,
                                                    caption='选择需要加密的文件',
                                                    filter='All Files (*);;Text Files (*.txt)')
        if len(self.file_list) == 0:
            return

        self.txtInputFile.setText(';'.join(self.file_list))

    def select_output_dir(self):
        self.output_dir_path = QFileDialog.getExistingDirectory(None, '选择输出目录', "C:/")
        if self.output_dir_path == '' or not os.path.exists(self.output_dir_path):
            return
        self.txtOutputDir.setText(self.output_dir_path)

    def check_input(self):
        print('check input')

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

    def encrypt(self):
        print('en')
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

                    if not is_encrypt_data(file_content):
                        encrypt_content = encrypt_data_with_head(self.key.key, file_content)
                        output_file = os.path.join(self.output_dir_path, n)
                        write_file(output_file, encrypt_content)

                pd.setValue(pd.value() + 1)

            if not pd.wasCanceled():
                QMessageBox.information(pd, '处理完成', '加密完成')
            else:
                QMessageBox.information(pd, '已经终止', '用户取消')
        except Exception as e:
            pass
            QMessageBox.critical(pd, '处理失败', repr(e))
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
                    encrypt_content = encrypt_data_with_head(key.key, file_content)
                    output_file = os.path.join(dir_path, n)
                    write_file(output_file, encrypt_content)

            pd.setValue(pd.value() + 1)

        if not pd.wasCanceled():
            QMessageBox.information(pd, '处理完成', '加密完成')
        else:
            QMessageBox.information(pd, '已经终止', '用户取消')

    except Exception as e:
        pass
        QMessageBox.critical(pd, '处理失败', repr(e))

    pd.close()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    kmd = KeyMgrDialog()
    kmd.show()
    sys.exit(app.exec_())
