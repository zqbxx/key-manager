# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'KeyMgrDialog.ui'
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
from PySide6.QtWidgets import (QAbstractButton, QApplication, QDialog, QDialogButtonBox,
    QHBoxLayout, QListView, QSizePolicy, QToolButton,
    QVBoxLayout, QWidget)

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        if not Dialog.objectName():
            Dialog.setObjectName(u"Dialog")
        Dialog.resize(524, 356)
        self.verticalLayout = QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.widget = QWidget(Dialog)
        self.widget.setObjectName(u"widget")
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.widget.sizePolicy().hasHeightForWidth())
        self.widget.setSizePolicy(sizePolicy)
        self.widget.setMinimumSize(QSize(0, 25))
        self.horizontalLayout = QHBoxLayout(self.widget)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.tbCreate = QToolButton(self.widget)
        self.tbCreate.setObjectName(u"tbCreate")
        sizePolicy1 = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Maximum)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.tbCreate.sizePolicy().hasHeightForWidth())
        self.tbCreate.setSizePolicy(sizePolicy1)
        self.tbCreate.setMinimumSize(QSize(50, 25))

        self.horizontalLayout.addWidget(self.tbCreate)

        self.tbAdd = QToolButton(self.widget)
        self.tbAdd.setObjectName(u"tbAdd")
        self.tbAdd.setMinimumSize(QSize(50, 25))

        self.horizontalLayout.addWidget(self.tbAdd)

        self.tbRemove = QToolButton(self.widget)
        self.tbRemove.setObjectName(u"tbRemove")
        self.tbRemove.setMinimumSize(QSize(50, 25))

        self.horizontalLayout.addWidget(self.tbRemove)


        self.verticalLayout.addWidget(self.widget, 0, Qt.AlignLeft)

        self.keyListView = QListView(Dialog)
        self.keyListView.setObjectName(u"keyListView")

        self.verticalLayout.addWidget(self.keyListView)

        self.buttonBox = QDialogButtonBox(Dialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)

        self.verticalLayout.addWidget(self.buttonBox)


        self.retranslateUi(Dialog)
        self.buttonBox.accepted.connect(Dialog.accept)
        self.buttonBox.rejected.connect(Dialog.reject)

        QMetaObject.connectSlotsByName(Dialog)
    # setupUi

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QCoreApplication.translate("Dialog", u"Dialog", None))
        self.tbCreate.setText(QCoreApplication.translate("Dialog", u"\u65b0\u5efa", None))
        self.tbAdd.setText(QCoreApplication.translate("Dialog", u"\u6dfb\u52a0", None))
        self.tbRemove.setText(QCoreApplication.translate("Dialog", u"\u5220\u9664", None))
    # retranslateUi

