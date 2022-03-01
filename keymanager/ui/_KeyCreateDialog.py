# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'KeyCreateDialog.ui'
##
## Created by: Qt User Interface Compiler version 6.2.3
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QDialog, QGridLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QSizePolicy,
    QSpacerItem, QVBoxLayout, QWidget)

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        if not Dialog.objectName():
            Dialog.setObjectName(u"Dialog")
        Dialog.resize(400, 150)
        self.verticalLayout = QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName(u"gridLayout")
        self.label_3 = QLabel(Dialog)
        self.label_3.setObjectName(u"label_3")

        self.gridLayout.addWidget(self.label_3, 1, 0, 1, 1)

        self.label = QLabel(Dialog)
        self.label.setObjectName(u"label")

        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)

        self.txtName = QLineEdit(Dialog)
        self.txtName.setObjectName(u"txtName")

        self.gridLayout.addWidget(self.txtName, 0, 1, 1, 1)

        self.txtPassword2 = QLineEdit(Dialog)
        self.txtPassword2.setObjectName(u"txtPassword2")
        self.txtPassword2.setEchoMode(QLineEdit.Password)

        self.gridLayout.addWidget(self.txtPassword2, 2, 1, 1, 1)

        self.btnFileChooser = QPushButton(Dialog)
        self.btnFileChooser.setObjectName(u"btnFileChooser")
        self.btnFileChooser.setMinimumSize(QSize(30, 0))
        self.btnFileChooser.setMaximumSize(QSize(30, 16777215))

        self.gridLayout.addWidget(self.btnFileChooser, 3, 2, 1, 1)

        self.label_4 = QLabel(Dialog)
        self.label_4.setObjectName(u"label_4")

        self.gridLayout.addWidget(self.label_4, 2, 0, 1, 1)

        self.txtPassword1 = QLineEdit(Dialog)
        self.txtPassword1.setObjectName(u"txtPassword1")
        self.txtPassword1.setEchoMode(QLineEdit.Password)

        self.gridLayout.addWidget(self.txtPassword1, 1, 1, 1, 1)

        self.label_2 = QLabel(Dialog)
        self.label_2.setObjectName(u"label_2")

        self.gridLayout.addWidget(self.label_2, 3, 0, 1, 1)

        self.txtPath = QLineEdit(Dialog)
        self.txtPath.setObjectName(u"txtPath")

        self.gridLayout.addWidget(self.txtPath, 3, 1, 1, 1)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.btnOk = QPushButton(Dialog)
        self.btnOk.setObjectName(u"btnOk")

        self.horizontalLayout.addWidget(self.btnOk)

        self.btnCancel = QPushButton(Dialog)
        self.btnCancel.setObjectName(u"btnCancel")

        self.horizontalLayout.addWidget(self.btnCancel)


        self.gridLayout.addLayout(self.horizontalLayout, 4, 0, 1, 3)


        self.verticalLayout.addLayout(self.gridLayout)

        QWidget.setTabOrder(self.txtName, self.txtPassword1)
        QWidget.setTabOrder(self.txtPassword1, self.txtPassword2)
        QWidget.setTabOrder(self.txtPassword2, self.txtPath)
        QWidget.setTabOrder(self.txtPath, self.btnFileChooser)
        QWidget.setTabOrder(self.btnFileChooser, self.btnOk)
        QWidget.setTabOrder(self.btnOk, self.btnCancel)

        self.retranslateUi(Dialog)

        QMetaObject.connectSlotsByName(Dialog)
    # setupUi

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QCoreApplication.translate("Dialog", u"Dialog", None))
        self.label_3.setText(QCoreApplication.translate("Dialog", u"\u5bc6\u78011", None))
        self.label.setText(QCoreApplication.translate("Dialog", u"\u540d\u79f0", None))
        self.btnFileChooser.setText(QCoreApplication.translate("Dialog", u"...", None))
        self.label_4.setText(QCoreApplication.translate("Dialog", u"\u5bc6\u78012", None))
        self.label_2.setText(QCoreApplication.translate("Dialog", u"\u8def\u5f84", None))
        self.btnOk.setText(QCoreApplication.translate("Dialog", u"\u4fdd\u5b58", None))
        self.btnCancel.setText(QCoreApplication.translate("Dialog", u"\u53d6\u6d88", None))
    # retranslateUi

