#!/usr/bin/env python3

from PyQt5 import QtCore, QtGui, QtWidgets
from functools import partial
import cv2
from datetime import datetime, timedelta
from hashlib import sha256
from pyzbar.pyzbar import decode
from qrcode import QRCode, constants
from os.path import abspath, dirname, join
from json import loads
from math import floor

global is_not_win
is_not_win = False

# Configure platform-specific values
try:
    # Only available on windows
    from winsound import Beep

except ModuleNotFoundError:
    # global is_not_win
    is_not_win = True


class Faculty:

    def __init__(self, filepath, token):

        # Set class-wide attributes
        # Assign parameters to class-wide variables
        self.token_size = token
        self.filepath = filepath

        # Create shell containers for class-wide use
        self.database = dict()
        self.session_faculty = dict()

        # Set static properties
        self.date = int(datetime.now().month + datetime.now().day + datetime.now().year)

        # Call methods in sequence
        self.read_db()
        self.generate_sessions()

    # Read database file to shell container
    def read_db(self):

        try:
            with open(self.filepath, mode='r') as faculty_file:
                self.database = loads(faculty_file.read())
                faculty_file.close()
        except FileNotFoundError:
            print('Required resources not complete! Check requirements.')
            exit(-404)

    # Generate sessions for present day
    def generate_sessions(self):

        # Hashing algorithm
        for faculty in self.database:

            # Mangle numerical part of faculty id with string part after having multiplied former with present date
            mangler = faculty['Code'][:3] + str(int(faculty['Code'][3:]) * self.date)

            # Stable hash creates instance of sha256() - onto hashing function
            stable_hash = sha256()

            # Pass mangler as c-string
            stable_hash.update(mangler.encode())

            # Generate hash-bytes
            hash_bytes = stable_hash.digest()

            # Convert hash bytes to integer; limit them by stable modulus hashing against token_size integer
            faculty['session'] = int.from_bytes(hash_bytes, byteorder='big', signed=False) % self.token_size

    # Authenticate session input
    def auth(self, token):

        # Check length of token against length of token_size(known); check if token is all digits
        if len(token) <= len(str(self.token_size)) and token.isdigit():

            # Check is token is a sub-string of database - optimization
            if str(token) in str(self.database):
                faculty = dict()

                # Fetch first result whose hash matches with token
                for faculty_member in self.database:
                    if int(token) == int(faculty_member['session']):
                        faculty = faculty_member
                        break

                # Assign session faculty in first iteration only
                if not str(faculty) == str(self.session_faculty):
                    self.session_faculty = faculty.copy()
                    return self.session_faculty


class Student:

    def __init__(self, filepath, output_dir):

        # Set class-wide attributes
        # Assign parameters to class-wide variables
        self.data_file = filepath
        self.output_dir = output_dir

        # Create shell containers for class-wide use
        self.database = list()
        self.student_list = list()

        # Call method in sequence
        self.read_db()

    # Read database file to shell container; sort list
    def read_db(self):

        try:
            with open(self.data_file, mode='r') as database:
                self.database = loads(database.read())
                database.close()
        except FileNotFoundError:
            print('Required resources not complete! Check requirements.')
            exit(-404)

        # Sort database by roll_number in increasing order
        self.database = sorted(self.database, key=lambda i: i['Roll_Number'])

    # Validate attendee entry against database - uses binary search algorithm
    def validate(self, roll, name, base_list=None, left_index=0, right_index=None):

        # Case when called from outer scope
        if not base_list and not left_index and not right_index:
            base_list = self.database
            right_index = len(self.database) - 1

        # Check base case
        if right_index >= left_index:

            # Find middle of array length and floor it down to integer
            mid = floor((left_index + right_index) / 2)

            # If element is present at the middle itself
            try:
                if int(base_list[mid]['Roll_Number']) == int(roll) and str(base_list[mid]['Name']) == str(name):
                    return base_list[mid]

                # If element is smaller than mid, check left_index subarray
                elif int(base_list[mid]['Roll_Number']) > int(roll):
                    return self.validate(base_list=base_list, left_index=left_index, right_index=mid-1,
                                         roll=roll, name=name)

                # Else check right subarray
                else:
                    return self.validate(base_list=base_list, left_index=mid+1, right_index=right_index,
                                         roll=roll, name=name)

            except ValueError:
                return None

        else:
            # Element is not present in the array
            return None

    # Generate attendee QR code
    def code_generator(self, main_application):

        # Generate QR code for each attendee in dataset
        for each_attendee in self.database:

            # Print attendee data
            print(list(each_attendee.values()))

            # Set QR code instance properties and save it to output_dir folder
            qr = QRCode(
                version=1,
                error_correction=constants.ERROR_CORRECT_H,
                box_size=10,
                border=4,
            )
            qr.add_data(list(each_attendee.values()))
            qr.make(fit=True)

            img = qr.make_image(fill_color="black", back_color="white")

            img.save(join(self.output_dir, each_attendee['Roll_Number'] + ' - ' +
                          each_attendee['Name'] + '.png'), 'PNG')

            # Unfreeze event loop - tell it to process events
            main_application.processEvents()


class Token:

    def __init__(self, faculty_path, output_dir, token_size):

        # Set class-wide attributes
        # Assign parameters to class-wide variables
        self.token_size = token_size
        self.faculty_path = faculty_path
        self.output_dir = output_dir

        # Create shell containers for class-wide use
        self.database = list()

        # Set static properties
        self.date = int(datetime.now().month + datetime.now().day + datetime.now().year)

        # Call methods in sequence
        self.read_db()

    # Read database file to shell container
    def read_db(self):
        with open(self.faculty_path, mode='r') as database:
            self.database = loads(database.read())
            database.close()

    # Generate sessions for present day; generate QR codes session token; mail QR codes to respective faculty
    def generate_session(self, main_application):

        # Iterate for each faculty entry in self.database:
        for faculty in self.database:

            # Mangle numerical part of faculty id with string part after having multiplied former with present date
            mangler = (faculty['Code'])[:3] + str(int(faculty['Code'][3:]) * self.date)

            # Stable hash creates instance of sha256() - onto hashing function
            stable_hash = sha256()

            # Pass mangler as c-string
            stable_hash.update(mangler.encode())

            # Generate hash-bytes
            hash_bytes = stable_hash.digest()

            # Convert hash bytes to integer; limit them by stable modulus hashing against token_size integer
            faculty['session'] = int.from_bytes(hash_bytes, byteorder='big', signed=False) % self.token_size

            # Print faculty data - without the actual tokens
            print(list(faculty.values())[0:-1])

            # Set QR code instance properties and save it to output_dir folder
            qr = QRCode(version=1, box_size=10, border=4,
                        error_correction=constants.ERROR_CORRECT_H,)
            qr.add_data(faculty['session'])
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")

            # Name of token file (image file, png extension) and path
            token_name = faculty['Code'] + '_' + faculty['Name'].replace(' ', '_') + '.png'
            img_path = join(self.output_dir, token_name)

            # Save token file in PNG format
            img.save(img_path, 'PNG')

            # Unfreeze event loop - tell it to process events
            main_application.processEvents()


class Timer:

    def __init__(self, filepath):

        # Read lecture breakpoints to a container dict()
        try:
            with open(filepath, mode='r') as breakpoints:
                self.lecture = loads(breakpoints.read())
                breakpoints.close()
        except FileNotFoundError:
            print('Required resources not complete! Check requirements.')
            exit(-404)

        # Read key name from timing.json file
        key_name = list(self.lecture.keys())[0]

        # Create list of time slots as tuple pairs from timing breakpoints
        self.timing_list = [(i, j) for i, j in zip(self.lecture[key_name][:-1],
                                                   self.lecture[key_name][1:])]

    # Determine time slot of current lecture
    def lecture_time(self):

        present = (datetime.now().year, datetime.now().month, datetime.now().day)

        # Iterate over each time slot to determine if it encompasses current time
        for entry in self.timing_list:

            # Process time slot format for timing info
            start_time, end_time = entry[0], entry[1]
            start_hour = int(start_time[:start_time.index(':')])
            start_minute = int(start_time[(start_time.index(':') + 1):])
            end_hour = int(end_time[:end_time.index(':')])
            end_minute = int(end_time[(end_time.index(':')+1):])

            start = datetime(year=present[0], month=present[1], day=present[2], hour=start_hour, minute=start_minute)
            end = datetime(year=present[0], month=present[1], day=present[2], hour=end_hour, minute=end_minute)

            # Return matching time slot along with lecture end time
            if start < datetime.now() < end:
                return datetime(present[0], present[1], present[2],
                                hour=end_hour, minute=end_minute), self.timing_list.index(entry), entry

        # Else return None if loop runs through


class Scheduler:

    def __init__(self, path_timing, path_lecture):

        # Set class-wide attributes
        # Assign parameters to class-wide variables
        self.path_timing = path_timing
        self.path_lecture = path_lecture

        self.temp_key = 'start'

        # Create shell containers for class-wide use
        self.timing = dict()
        self.lecture_table = dict()

        # Call methods in sequence
        self.structure()

    # Read timing and lecture files; create timing structure
    def structure(self):
        with open(self.path_timing, mode='r') as time_points:
            self.timing = loads(time_points.read())
            time_points.close()

        # Read key name from timing.json file
        key_name = list(self.timing.keys())[0]

        # Create list of time slots as tuple pairs from timing breakpoints and add to self.timing dictionary
        self.timing[self.temp_key] = [(i, j) for i, j in zip(self.timing[key_name][:-1],
                                                             self.timing[key_name][1:])]

        try:
            with open(self.path_lecture, mode='r') as table:
                self.lecture_table = loads(table.read())
                table.close()
        except FileNotFoundError:
            print('Required resources not complete! Check requirements.')
            exit(-404)

    # Return subject name from lecture table
    def lecture(self, section, index):

        # Fetch lecture table only for the given section
        lecture_schedule = self.lecture_table[section]

        # Return subject name index present day with index lecture number
        try:
            return lecture_schedule[list(lecture_schedule.keys())[datetime.today().weekday()]][index]
        except IndexError:
            return None


class Attribute:

    # Meta class
    # Pre-set attributes that define behaviour of application; Used by all other classes
    def __init__(self):

        self.tokenLimit = 1000000000000
        self.warning_period_minutes = 1
        self.isAuthenticated = False
        self.isWarned = False
        self.isFlushed = False
        self.host_faculty = dict()
        self.attendees = list()
        self.lecture_time = list()
        self.lecture_number = int()


class Object:

    # Meta class
    # Instantiate objects as utilities needed by other classes
    def __init__(self):

        # Meta - assign folder names containing other folders or file; fetch their absolute path
        self.json_folder_name = 'resource'
        self.database_folder_name = 'database'

        self.json_folder_path = abspath(join(dirname(__file__), self.json_folder_name))
        self.database_folder_path = abspath(join(dirname(__file__), self.database_folder_name))

        # Assign filename containing operational info; fetch their path - uses meta
        self.file_faculty = 'faculty.json'
        self.file_student = 'student.json'
        self.file_lecture = 'lecture.json'
        self.file_timing = 'timing.json'

        self.path_faculty = join(self.json_folder_path, self.file_faculty)
        self.path_student = join(self.json_folder_path, self.file_student)
        self.path_lecture = join(self.json_folder_path, self.file_lecture)
        self.path_timing = join(self.json_folder_path, self.file_timing)

        # Assign folders to export to; fetch path - uses meta
        self.token_folder_name = 'session'
        self.attendee_folder_name = 'attendees'

        self.token_folder_path = join(self.database_folder_path, self.token_folder_name)
        self.attendee_folder_path = join(self.database_folder_path, self.attendee_folder_name)

        # Instantiate objects
        # Create instance of Attribute class to fetch attributes from
        self.attribute = Attribute()

        # Instantiate objects using __init__() and attribute object values
        self.faculty = Faculty(filepath=self.path_faculty, token=self.attribute.tokenLimit)
        self.student = Student(filepath=self.path_student, output_dir=self.attendee_folder_path)
        self.timer = Timer(filepath=self.path_timing)
        self.scheduler = Scheduler(path_lecture=self.path_lecture, path_timing=self.path_timing)
        self.token = Token(faculty_path=self.path_faculty, output_dir=self.token_folder_path,
                           token_size=self.attribute.tokenLimit)

    # Function when called returns instance of attribute object used in this class
    def return_attribute_obj(self):
        return self.attribute


class Utility:

    # Non-visual feedback - audio
    def beep(self, frequency=2500, duration=300):
        global is_not_win
        if not is_not_win:
            Beep(frequency, duration)  # Based on Windows API - Single platform support
        else:
            print('\a')  # Cross platform. Limited control over frequency and duration

    # Warn using feedback mechanism - audio
    def warn(self):
        self.attribute.isWarned = True
        self.attribute.isFlushed = False
        self.console_output('Warning Generated!')
        self.beep(frequency=5000, duration=2000)

    # Flush attendance if lecture over, or on program close
    def flush(self):

        # If system isn't authenticated, return execution sequence
        if not self.attribute.isAuthenticated:
            return

        # If host faculty present, starts export procedure
        if self.attribute.host_faculty:

            # Collective dictionary with lecture record
            attendance = dict()

            # Assign copies of dictionary not alias
            attendance['host'] = self.attribute.host_faculty.copy()
            attendance['attendees'] = self.attribute.attendees.copy()

            # Export attendance; return unique subject key
            key = self.export_attendance(attendance)

            # If key returned, add attendance entry to total lecture record of day with key as index
            if key:
                self.attribute.attendance_all[key] = attendance.copy()
            else:
                return

        # Set flags for warning and flush state; clear exported lecture records
        self.attribute.isFlushed = True
        self.attribute.isAuthenticated = False
        self.attribute.host_faculty.clear()
        self.attribute.attendees.clear()
        self.obj.student.student_list.clear()

        # Print message and give feedback
        self.console_output('Attendance Flushed!')
        self.beep(frequency=3500, duration=1000)

    # Set authentication flags; provide authentication feedback
    def auth(self, faculty_data):
        self.attribute.isAuthenticated = True
        self.attribute.host_faculty = faculty_data
        print(f"Lecture held by: {faculty_data['Name']} ({faculty_data['Code']})")
        self.beep(frequency=2500, duration=1250)

    # Print text on frame
    def frame_text(self, frame, text, font=cv2.FONT_HERSHEY_PLAIN):
        cv2.putText(
            img=frame,
            text=text,
            org=(5, 30),
            fontFace=font,
            fontScale=1.5,
            color=(255, 0, 0),
            thickness=3)

    # Add attendee record; give feedback
    def attend(self, attendee):
        if str(attendee) not in str(self.attribute.attendees):
            self.attribute.attendees.append(attendee)
            self.beep(frequency=2500, duration=300)

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

            time_check = self.time_check()
            if time_check == -1:
                return

            # Capture frames from self.capture source and flips them correctly
            _, frame = self.capture.read()
            frame = cv2.flip(frame, 1)

            # Check for qr codes in frame
            self.processor(frame)

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

        # Remove this later
        print(self.attribute.attendees)

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

    # Checks present time on each iteration
    def time_check(self):

        # Time-checks and operations:
        # First perform check for current time vs time slots in time table
        # Then obtain current time window with start and end element
        # On change in lecture_number, reset isWarned attribute; change self.lecture_time
        if self.obj.timer.lecture_time():

            # Obtain current lecture end (datetime object), lecture number, and lecture time slot
            self.attribute.lecture_end, lecture_num, self.attribute.lecture_tuple = self.obj.timer.lecture_time()

            # Evaluate if lecture number has changed
            if not self.attribute.lecture_number == lecture_num:

                # Update lecture time slot on lecture number change; reset isWarned flag
                self.attribute.lecture_time = list(self.attribute.lecture_tuple)
                self.attribute.isWarned = False

            # Update current lecture_number
            self.attribute.lecture_number = lecture_num

        else:

            # If current time doesn't match a time slot, college is over
            print('Outside college working hours!')
            self.monitor = False
            self.stop_monitor()

            # Return a value to signal the loop
            return -1

        # Update seconds left to warn and flush - based on time slots in lecture table
        # Fire time-based events: warn() and flush()
        warn_time = self.attribute.lecture_end - timedelta(minutes=self.attribute.warning_period_minutes)
        warn_delay = (warn_time - datetime.now()).total_seconds()
        flush_delay = (self.attribute.lecture_end - datetime.now()).total_seconds()
        if not self.attribute.isWarned and (0 <= warn_delay <= 1):
            self.warn()
        elif not self.attribute.isFlushed and (0 <= flush_delay <= 1):
            self.flush()

    # Process frame for QR Code
    def processor(self, frame):

        decoded_list = decode(frame)

        # If frame doesn't contain QR Code, return flow of execution
        if not decoded_list:
            return
        else:
            decoded = decoded_list[0]

            # Decoded object is bytes type
            qr_data = decoded.data.decode('utf-8')

            # Authentication tokens are all digits, and have less number of digits than tokenLimit.
            # Also, only check if not authenticaed already
            if qr_data.isdigit() and len(qr_data) <= len(str(self.attribute.tokenLimit
                                                             )) and not self.attribute.isAuthenticated:

                # Authenticate faculty
                session_faculty = self.obj.faculty.auth(qr_data)

                # If authenticated successfully, call self.auth() with returned data
                if session_faculty: self.auth(session_faculty)

            # If already authenticated and qrdata is all digits, print 'active session' message
            elif qr_data.isdigit() and self.attribute.isAuthenticated:
                self.frame_text(frame=frame, text='Session Activated!')

            # If authenticated, and input is string, check if attendee is in database
            elif self.attribute.isAuthenticated and not qr_data.isdigit():
                qr_data_list = qr_data.strip('][').replace("'", '').split(', ')

                # Check input data signature. Ignore bad input.
                try:
                    verified_student = self.obj.student.validate(roll=qr_data_list[0], name=qr_data_list[1])
                except IndexError:
                    return

                # If attendee data in database, print message and call attend()
                if verified_student:
                    image_text = qr_data_list[0] + ': ' + qr_data_list[1].replace('  ', ' ')
                    self.frame_text(frame=frame, text=image_text)
                    self.attend(verified_student)


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
        self.attach_btn()

        # Import attributes
        self.obj = Object()
        self.attribute = self.obj.return_attribute_obj()

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

    # Create shell button instance - use this to bridge static slots with dynamic buttons
    def attach_btn(self):
        self.button_session = self.btn_session
        self.button_attendee = self.btn_attendee
        self.button_schedule = self.btn_schedule
        self.button_monitor = self.btn_monitor

    # Connect push button slots
    def connect_slots(self):

        # Attach token_generator() as signal to button_session click event
        self.button_session.clicked.connect(partial(self.obj.token.generate_session, self.application))

        # Attach code_generator() as signal to button_monitor_attendee click event
        self.button_attendee.clicked.connect(partial(self.obj.student.code_generator,
                                                     self.application))

        # Attach monitor_trigger() as signal to btn_monitor click event
        self.button_monitor.clicked.connect(partial(self.monitor_trigger))


if __name__ == '__main__':

    # Execute GUI from this entry point
    application = Application()
