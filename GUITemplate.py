#!/usr/bin/env python3

from PyQt5 import QtCore, QtGui, QtWidgets
from functools import partial


class Window(object):

    def __init__(self):
        self.qtranslate = QtCore.QCoreApplication.translate
        self.buttons = {'btn_session': 'Generate Session Tokens',
                        'btn_attendee': 'Generate Attendee Tokens',
                        'btn_schedule': 'Launch Schedule Manager',
                        'btn_monitor': 'Monitor Attendance'}
        self.centralwidget_name = 'dashboard'

    def setup_dashboard(self, dashboard_window):
        dashboard_window.setObjectName(self.centralwidget_name)
        dashboard_window.resize(1000, 518)
        self.centralwidget = QtWidgets.QWidget(dashboard_window)
        dashboard_window.setCentralWidget(self.centralwidget)

    def setup_cam(self):
        self.frame_cam = QtWidgets.QLabel(self.centralwidget)
        self.frame_cam.setGeometry(QtCore.QRect(20, 20, 640, 478))
        self.frame_cam.setFrameShape(QtWidgets.QFrame.Box)

    def setup_btn(self):
        _btn_offset_x_ = 20
        _btn_height_ = 108
        _btn_offset_margin_ = 15

        for btn_name, btn_text in self.buttons.items():
            setattr(self, btn_name, QtWidgets.QPushButton(self.centralwidget))
            button = getattr(self, btn_name)
            button.setGeometry(QtCore.QRect(675, _btn_offset_x_, 305, _btn_height_))
            button.setText(self.qtranslate(self.centralwidget_name, btn_text))
            _btn_offset_x_ = _btn_offset_x_ + _btn_height_ + _btn_offset_margin_

            ##### Lambda function doesn't work - was overwriting pointer object for some reason.
            ##### Avoid using exec() function - although it works - is not safe against command injection.
            # exec('button.clicked.connect(lambda: btn_text_func("' + btn_text + '"))')
            ########## ADD TO WIKI!
            button.clicked.connect(partial(btn_sample_func, button))


def btn_sample_func(btn):
    print(btn.text())


if __name__ == '__main__':
    application = QtWidgets.QApplication([])
    main_window = QtWidgets.QMainWindow()
    dashboard_window = Window()

    dashboard_window.setup_dashboard(main_window)
    dashboard_window.setup_cam()
    dashboard_window.setup_btn()

    main_window.show()
    application.exec_()
