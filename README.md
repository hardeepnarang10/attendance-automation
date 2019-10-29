## Description
Attendance Monitor and Control System (A.M.C. System) is an attempt to automate the process of attendance. It uses computer webcam to scan for QR codes, where based on it's authentication and validation algorithm, decides to either record or ignore the decoded data.

It is a cost efficient, yet fully functional method of attendance automation which integrates as front interface for monitoring and recording with already existing cloud storage.

It features time-bound attendance monitor, encrypted session generator, attendee QR code generator, schedule generator, ability to configure AMC system values, feedback mechanism, record exporter, along with direct mailing capability, with robust connection loss recovery.




## Quick Background

My college has this peculiar method of record keeping - first onto a sheet of paper (which were oftentimes compiled by students themselves, or the faculty during their lecture), then onto a register, after which each faculty member would manually enter their lecture's record into an excel sheet and upload that to our colleges' database.

Clearly this is not the most sophisticated or efficient method of recording attendance. And since it is to be expected that no institute would allow a non-faculty member direct-or-connection access to their central database, this left little room for improvement to be brought about by a student like myself.

So I worked out a solution which would not only allow for monitoring attendance, but also record keeping without direct interaction with the main server or their database. This solution needed to be legacy-compatible, so it could be installed without changing the structure of the current system.




## Solution

AMC system is integrated with the time-slots, which are pairs of start and end time of a lecture. This enables the system to account for attendance per lecture. Furthermore, to prevent exploit from students scanning and walking away before a faculty comes in, the system is equipped with authentication and validation mechanism.

It'll only accept input (which it further evaluates for a match in attendee record), after a faculty scans their own QR code, setting the system state to 'activated'. These codes are session tokens assigned to faculty members. Session tokens are both encrypted, and are only valid for a day. Each day, new set of tokens are generated and sent over mail to the respective faculties. These need not be printed - and can be scanned directly from their phone screens.

Since the system is integrated with time-slots, attendance can only be registered during the lecture, not before or after. Also, it sends off a high-frequency warning beep before a set period of time against lecture end time, as a reminder that last few minutes are left before lecture is over. Once the lecture is over, it flushes the attendance record to an excel sheet, a copy of which is sent over as attachment to the faculty taking the lecture, one copy is saved to the filesystem, and when all the lectures in a day are over, or if monitor mode is stopped before that, then a collective record of all the lectures taken throughout the day get saved locally with a copy sent over as email attachment to the head faculty of the department.

The state of the system is reset back to 'deactivated' and the cycle of authentication is repeated.

The mail that is sent over to the faculty taking the lecture, contains meta info on number of attendees, along with an excel sheet logging their names and roll numbers. So the faculty can do a simple headcount to match number of attendees in the log vs the number actually present, to catch the case if a student tries to play around with the system by scanning multiple QR codes to mark someone else's attendance. In case of mismatch, they may decide a necessary course of action.




## Upgrade Option

In case QR code system doesn't serve to suffice, there is an option for easy upgrade to biometric scanning, which doesn't deal with issues of proxies and duplicity. The core of the application is the the automation algorithm which can be used interchangeably with biometric scanning.

Of course this upgrade comes at the cost of having to train the biometric model with each entry containing multiple biometric scans of the same person, without certainty of accurate recognition.




## Requirements

- Python3.7+ (and all required python3 modules)
  (<a href="https://www.python.org/ftp/python/3.7.4/python-3.7.4.exe">Download Python 3.7.4</a>)
- Pip Modules:
  - colorama==0.4.1
  - numpy==1.17.3
  - opencv-python==4.1.1.26
  - pandas==0.25.2
  - Pillow==6.2.0
  - PyQt5==5.13.1
  - PyQt5-sip==12.7.0
  - python-dateutil==2.8.0
  - pytz==2019.3
  - pyzbar==0.1.8
  - qrcode==6.1
  - six==1.12.0
  - XlsxWriter==1.2.2
- Visual C++ Redistributable Packages (x64 or x86)
  (<a href="https://www.microsoft.com/en-US/download/details.aspx?id=40784">Download Here</a>)



## Instructions

(Make sure you have python, above mentioned pip modules, and visual C++ redistributable packages installed on your system)

**Check 'Add Python 3.x to PATH' during installation**.

1. <a href="https://github.com/hardeepnarang10/attendance-automation/archive/master.zip">Download</a> and extract the zip file.

2. Install requirements (navigate to root directory on command line). Run command:

   ```bash
   pip install -r requirements.txt
   ```

3. Go to 'resources' folder and edit all the JSON files. (You may use the dummy files for testing - check 'dummy-data' directory) (Use <a href="http://jsoneditoronline.org/">this online editor</a> to check formatting errors)

4. From root as present working directory, run the following command:

   ```python
   python application.py
   ```

5. In the window that opens, click on 'Configure AMC values'. Enter required values. Restart application using the above command.

6. Generate Session Tokens and Attendee Tokens and distribute them as per your requirement.

7. Make sure you have a webcam connected and installed on your system. AMC System uses primary camera for capturing sessions, make sure its not being used by another application. (Try connecting through different ports if you're using an external webcam)

8. Start Attendance Monitor.



## Version

AMC System v2.0.0 is its first public release (see commit: [61c13ab](https://github.com/hardeepnarang10/attendance-automation/commit/61c13abe1ac3bbd9f1cc65746896f0a0992ed5d5)).



## Contributions

Contributions are welcome. Make a [pull request](../../pulls).




## License

This project is available for free use under GNU General Public License v3.0.

