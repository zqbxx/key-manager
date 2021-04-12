# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'EncryptFileDialog.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        if not Dialog.objectName():
            Dialog.setObjectName(u"Dialog")
        Dialog.resize(400, 103)
        self.horizontalLayout = QHBoxLayout(Dialog)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName(u"gridLayout")
        self.label = QLabel(Dialog)
        self.label.setObjectName(u"label")

        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)

        self.label_2 = QLabel(Dialog)
        self.label_2.setObjectName(u"label_2")

        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)

        self.tbSelectDir = QToolButton(Dialog)
        self.tbSelectDir.setObjectName(u"tbSelectDir")

        self.gridLayout.addWidget(self.tbSelectDir, 1, 2, 1, 1)

        self.tbSelectFiles = QToolButton(Dialog)
        self.tbSelectFiles.setObjectName(u"tbSelectFiles")

        self.gridLayout.addWidget(self.tbSelectFiles, 0, 2, 1, 1)

        self.txtInputFile = QLineEdit(Dialog)
        self.txtInputFile.setObjectName(u"txtInputFile")
        self.txtInputFile.setReadOnly(True)

        self.gridLayout.addWidget(self.txtInputFile, 0, 1, 1, 1)

        self.txtOutputDir = QLineEdit(Dialog)
        self.txtOutputDir.setObjectName(u"txtOutputDir")
        self.txtOutputDir.setReadOnly(True)

        self.gridLayout.addWidget(self.txtOutputDir, 1, 1, 1, 1)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer)

        self.btnOk = QPushButton(Dialog)
        self.btnOk.setObjectName(u"btnOk")
        self.btnOk.setMaximumSize(QSize(80, 16777215))

        self.horizontalLayout_2.addWidget(self.btnOk)

        self.btnCancel = QPushButton(Dialog)
        self.btnCancel.setObjectName(u"btnCancel")
        self.btnCancel.setMaximumSize(QSize(80, 16777215))

        self.horizontalLayout_2.addWidget(self.btnCancel)


        self.gridLayout.addLayout(self.horizontalLayout_2, 2, 0, 1, 3)


        self.horizontalLayout.addLayout(self.gridLayout)


        self.retranslateUi(Dialog)

        QMetaObject.connectSlotsByName(Dialog)
    # setupUi

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QCoreApplication.translate("Dialog", u"Dialog", None))
        self.label.setText(QCoreApplication.translate("Dialog", u"\u56fe\u7247", None))
        self.label_2.setText(QCoreApplication.translate("Dialog", u"\u8f93\u51fa\u76ee\u5f55", None))
        self.tbSelectDir.setText(QCoreApplication.translate("Dialog", u"...", None))
        self.tbSelectFiles.setText(QCoreApplication.translate("Dialog", u"...", None))
        self.btnOk.setText(QCoreApplication.translate("Dialog", u"\u786e\u5b9a", None))
        self.btnCancel.setText(QCoreApplication.translate("Dialog", u"\u53d6\u6d88", None))
    # retranslateUi

