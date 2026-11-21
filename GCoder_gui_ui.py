# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'GCoder_gui.ui'
##
## Created by: Qt User Interface Compiler version 6.11.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QAction, QBrush, QColor, QConicalGradient,
    QCursor, QFont, QFontDatabase, QGradient,
    QIcon, QImage, QKeySequence, QLinearGradient,
    QPainter, QPalette, QPixmap, QRadialGradient,
    QTransform)
from PySide6.QtWidgets import (QApplication, QComboBox, QFrame, QLabel,
    QLineEdit, QMainWindow, QMenu, QMenuBar,
    QPushButton, QSizePolicy, QStatusBar, QTextEdit,
    QToolButton, QWidget)

class Ui_GCoder(object):
    def setupUi(self, GCoder):
        if not GCoder.objectName():
            GCoder.setObjectName(u"GCoder")
        GCoder.resize(542, 550)
        self.mb_settings_PunchSetup = QAction(GCoder)
        self.mb_settings_PunchSetup.setObjectName(u"mb_settings_PunchSetup")
        self.mb_file_export_PunchSettings = QAction(GCoder)
        self.mb_file_export_PunchSettings.setObjectName(u"mb_file_export_PunchSettings")
        self.mb_file_import_PunchSettings = QAction(GCoder)
        self.mb_file_import_PunchSettings.setObjectName(u"mb_file_import_PunchSettings")
        self.mb_settings_SetCurrentPunchPosition = QAction(GCoder)
        self.mb_settings_SetCurrentPunchPosition.setObjectName(u"mb_settings_SetCurrentPunchPosition")
        self.centralwidget = QWidget(GCoder)
        self.centralwidget.setObjectName(u"centralwidget")
        self.legcode = QLineEdit(self.centralwidget)
        self.legcode.setObjectName(u"legcode")
        self.legcode.setGeometry(QRect(20, 150, 371, 22))
        self.pbsend = QPushButton(self.centralwidget)
        self.pbsend.setObjectName(u"pbsend")
        self.pbsend.setGeometry(QRect(400, 150, 75, 24))
        self.telog = QTextEdit(self.centralwidget)
        self.telog.setObjectName(u"telog")
        self.telog.setGeometry(QRect(20, 180, 371, 301))
        self.label = QLabel(self.centralwidget)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(28, 20, 461, 111))
        self.label.setPixmap(QPixmap(u"Gcoder_banner.png"))
        self.cbCOM = QComboBox(self.centralwidget)
        self.cbCOM.setObjectName(u"cbCOM")
        self.cbCOM.setGeometry(QRect(400, 210, 91, 22))
        self.pbload = QPushButton(self.centralwidget)
        self.pbload.setObjectName(u"pbload")
        self.pbload.setGeometry(QRect(400, 180, 75, 24))
        self.pbexport = QPushButton(self.centralwidget)
        self.pbexport.setObjectName(u"pbexport")
        self.pbexport.setGeometry(QRect(400, 460, 75, 24))
        self.tb_refresh_com = QToolButton(self.centralwidget)
        self.tb_refresh_com.setObjectName(u"tb_refresh_com")
        self.tb_refresh_com.setGeometry(QRect(500, 210, 21, 20))
        icon = QIcon(QIcon.fromTheme(QIcon.ThemeIcon.ViewRefresh))
        self.tb_refresh_com.setIcon(icon)
        self.pb_increment = QPushButton(self.centralwidget)
        self.pb_increment.setObjectName(u"pb_increment")
        self.pb_increment.setGeometry(QRect(400, 250, 91, 26))
        self.frame = QFrame(self.centralwidget)
        self.frame.setObjectName(u"frame")
        self.frame.setGeometry(QRect(400, 380, 131, 71))
        self.frame.setAutoFillBackground(False)
        self.frame.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame.setFrameShadow(QFrame.Shadow.Raised)
        self.cb_PunchChanger = QComboBox(self.frame)
        self.cb_PunchChanger.setObjectName(u"cb_PunchChanger")
        self.cb_PunchChanger.setGeometry(QRect(10, 30, 111, 26))
        self.label_2 = QLabel(self.frame)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setGeometry(QRect(10, 10, 111, 16))
        GCoder.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(GCoder)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 542, 33))
        self.menusettings = QMenu(self.menubar)
        self.menusettings.setObjectName(u"menusettings")
        self.menufile = QMenu(self.menubar)
        self.menufile.setObjectName(u"menufile")
        self.menuexport = QMenu(self.menufile)
        self.menuexport.setObjectName(u"menuexport")
        self.menuimport = QMenu(self.menufile)
        self.menuimport.setObjectName(u"menuimport")
        GCoder.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(GCoder)
        self.statusbar.setObjectName(u"statusbar")
        GCoder.setStatusBar(self.statusbar)

        self.menubar.addAction(self.menufile.menuAction())
        self.menubar.addAction(self.menusettings.menuAction())
        self.menusettings.addAction(self.mb_settings_PunchSetup)
        self.menusettings.addAction(self.mb_settings_SetCurrentPunchPosition)
        self.menufile.addAction(self.menuexport.menuAction())
        self.menufile.addAction(self.menuimport.menuAction())
        self.menuexport.addAction(self.mb_file_export_PunchSettings)
        self.menuimport.addAction(self.mb_file_import_PunchSettings)

        self.retranslateUi(GCoder)

        QMetaObject.connectSlotsByName(GCoder)
    # setupUi

    def retranslateUi(self, GCoder):
        GCoder.setWindowTitle(QCoreApplication.translate("GCoder", u"GCoder", None))
        self.mb_settings_PunchSetup.setText(QCoreApplication.translate("GCoder", u"punch setup", None))
        self.mb_file_export_PunchSettings.setText(QCoreApplication.translate("GCoder", u"punch settings (JSON)", None))
        self.mb_file_import_PunchSettings.setText(QCoreApplication.translate("GCoder", u"punch settings (JSON)", None))
        self.mb_settings_SetCurrentPunchPosition.setText(QCoreApplication.translate("GCoder", u"set current punch positon", None))
        self.pbsend.setText(QCoreApplication.translate("GCoder", u"send", None))
        self.label.setText("")
        self.pbload.setText(QCoreApplication.translate("GCoder", u"load", None))
        self.pbexport.setText(QCoreApplication.translate("GCoder", u"Export", None))
        self.tb_refresh_com.setText("")
        self.pb_increment.setText(QCoreApplication.translate("GCoder", u"increment S1", None))
        self.label_2.setText(QCoreApplication.translate("GCoder", u"current active punch", None))
        self.menusettings.setTitle(QCoreApplication.translate("GCoder", u"settings", None))
        self.menufile.setTitle(QCoreApplication.translate("GCoder", u"file", None))
        self.menuexport.setTitle(QCoreApplication.translate("GCoder", u"export", None))
        self.menuimport.setTitle(QCoreApplication.translate("GCoder", u"import", None))
    # retranslateUi

