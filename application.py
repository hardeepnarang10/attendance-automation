#!/usr/bin/env python3

from PyQt5 import QtCore, QtGui, QtWidgets
from functools import partial
import cv2


class Utility:

    pass

    # Implement feedback mechanism

    # Implement warning and flush system

    # Implement attendance export channeling - flush() should trigger export

    # Implement secondary-class frame update: Maybe functionality to show simple text on frame

    # Implement function to check time-status; controller needs to be in-sync with time delta


class Monitor(Utility):

    # Start attendance monitor - write authentication check and control here
    def monitor_cam(self):

        # Setup video capture stream from specified capture device
        self.capture = cv2.VideoCapture(self.capture_device, cv2.CAP_DSHOW)

        # Change START on btn_monitor to STOP
        self.btn_monitor.setText(self.qtranslate(self.centralwidget_name, 'STOP'))

        # If self.monitor is True, attendance monitor starts
        while self.monitor:

            # Capture frames from self.capture source
            _, frame = self.capture.read()

            # cv2 records frames from camera which are vertically flipped: we need to flip them back
            frame = cv2.flip(frame, 1)

            # cv2 frames are numpy.ndarray type objects: convert them to QImage
            qimage = QtGui.QImage(frame, frame.shape[1], frame.shape[0], frame.shape[1] * 3,
                                  QtGui.QImage.Format_RGB888).rgbSwapped()

            # Further convert QImage to QPixmap object
            cam_pixmap = QtGui.QPixmap(qimage)

            # Render QPixmap to camera container(QFrame object)
            self.frame_cam.setPixmap(cam_pixmap)

            # Check if main window is closed: stops attendance monitor if it is
            if not self.main_window.isVisible():
                self.stop_monitor()

            # Tell event loop to process events
            self.application.processEvents()

    # Stop attendance monitor
    def stop_monitor(self):
        self.monitor = False
        self.cam_on = False
        self.capture.release()
        # cv2.destroyAllWindows()

        # Clear camera frame - QFrame and reset btn_monitor text
        self.frame_cam.clear()
        self.btn_monitor.setText(self.qtranslate(self.centralwidget_name, 'START'))

    # Trigger to start/stop monitor cam
    def monitor_trigger(self):

        # Check status of attendance monitor to determine further action
        if self.cam_on:
            print('Turning off monitor mode...')  # Not the best place to put this message - only for debugging
            self.stop_monitor()

        else:
            print('Turning on monitor mode...')  # Again not the best place - Put these messages in start/stop funcs
            self.monitor = True
            self.cam_on = True
            self.monitor_cam()


class Application(Monitor):

    def __init__(self):

        # Initialize PyQt5 application and main window
        self.application = QtWidgets.QApplication([])
        self.main_window = QtWidgets.QMainWindow()

        # Define interface variables
        self.qtranslate = QtCore.QCoreApplication.translate
        self.buttons = {'btn_session': 'Generate Session Tokens',
                        'btn_attendee': 'Generate Attendee Tokens',
                        'btn_schedule': 'Launch Schedule Manager',
                        'btn_monitor': 'Monitor Attendance'}
        self.centralwidget_name = 'dashboard'
        self.monitor = bool()
        self.cam_on = bool()

        # Specify video input stream/source
        self.capture_device = 0     # 0 means capture from internal camera device

        # Sequential function calls
        # Interface setup functions
        self.setup_dashboard(self.main_window)
        self.setup_cam()
        self.setup_btn()

        # Trigger setup functions
        self.connect_slots()

        # Translate components
        self.btn_monitor.setText(self.qtranslate(self.centralwidget_name, 'START'))

        # Show main window
        self.main_window.show()

        # Run event loop
        self.application.exec_()

    # Setup main_window
    def setup_dashboard(self, dashboard_window):
        dashboard_window.setObjectName(self.centralwidget_name)
        dashboard_window.resize(1000, 518)

        # Set dashboard_window as central widget (root) which further contains (encloses) other widgets
        self.centralwidget = QtWidgets.QWidget(dashboard_window)
        dashboard_window.setCentralWidget(self.centralwidget)

    # Setup camera frame
    def setup_cam(self):
        self.frame_cam = QtWidgets.QLabel(self.centralwidget)
        self.frame_cam.setGeometry(QtCore.QRect(20, 20, 640, 478))

        # Give frame a box enclosure (boundary)
        self.frame_cam.setFrameShape(QtWidgets.QFrame.Box)

    # Setup right pane buttons
    def setup_btn(self):

        # Set measurements: button offset, length, margin
        _btn_offset_x_ = 20
        _btn_height_ = 108
        _btn_offset_margin_ = 15

        # Initialize button objects using self.buttons dict() items
        for btn_name, btn_text in self.buttons.items():

            # Bind button object as an attribute of class instance
            setattr(self, btn_name, QtWidgets.QPushButton(self.centralwidget))

            # Fetch button object from class instance object
            button = getattr(self, btn_name)
            button.setGeometry(QtCore.QRect(675, _btn_offset_x_, 305, _btn_height_))
            button.setText(self.qtranslate(self.centralwidget_name, btn_text))
            _btn_offset_x_ = _btn_offset_x_ + _btn_height_ + _btn_offset_margin_

    # Connect push button slots
    def connect_slots(self):

        # Attach monitor_trigger() as signal to btn_monitor click event
        self.btn_monitor.clicked.connect(partial(self.monitor_trigger))


if __name__ == '__main__':

    # Execute GUI from this entry point
    application = Application()
