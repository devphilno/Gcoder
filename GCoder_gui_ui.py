# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'GCoder_gui.ui'
##
## Created by: Qt User Interface Compiler version 6.10.2
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
from PySide6.QtWidgets import (QApplication, QComboBox, QDialog, QLabel,
    QLineEdit, QPushButton, QSizePolicy, QTextEdit,
    QWidget)

class Ui_GCoder(object):
    def setupUi(self, GCoder):
        if not GCoder.objectName():
            GCoder.setObjectName(u"GCoder")
        GCoder.resize(514, 524)
        self.legcode = QLineEdit(GCoder)
        self.legcode.setObjectName(u"legcode")
        self.legcode.setGeometry(QRect(20, 150, 371, 22))
        self.pbsend = QPushButton(GCoder)
        self.pbsend.setObjectName(u"pbsend")
        self.pbsend.setGeometry(QRect(400, 150, 75, 24))
        self.telog = QTextEdit(GCoder)
        self.telog.setObjectName(u"telog")
        self.telog.setGeometry(QRect(20, 180, 371, 301))
        self.label = QLabel(GCoder)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(28, 20, 461, 111))
        self.label.setPixmap(QPixmap(u"Gcoder_banner.png"))
        self.cbCOM = QComboBox(GCoder)
        self.cbCOM.setObjectName(u"cbCOM")
        self.cbCOM.setGeometry(QRect(400, 210, 91, 22))
        self.pbload = QPushButton(GCoder)
        self.pbload.setObjectName(u"pbload")
        self.pbload.setGeometry(QRect(400, 180, 75, 24))
        self.pbexport = QPushButton(GCoder)
        self.pbexport.setObjectName(u"pbexport")
        self.pbexport.setGeometry(QRect(400, 460, 75, 24))

        self.retranslateUi(GCoder)

        QMetaObject.connectSlotsByName(GCoder)
    # setupUi

    def retranslateUi(self, GCoder):
        GCoder.setWindowTitle(QCoreApplication.translate("GCoder", u"GCoder", None))
        self.pbsend.setText(QCoreApplication.translate("GCoder", u"send", None))
        self.label.setText("")
        self.pbload.setText(QCoreApplication.translate("GCoder", u"load", None))
        self.pbexport.setText(QCoreApplication.translate("GCoder", u"Export", None))
    # retranslateUi

