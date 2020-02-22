"""Imports roster data from SQLRunner/Powerschool SIS.

This module defines the class responsible for importing data originating from
Powerschool. The data itself is exported by SQLRunner (an internal application
that negotiates a secure tunnel to Powerschool and runs queries) to CSV files
stored on an SFTP Server.

To use this module you'll want to import DJOImport, create a new class instance,
and then run the `import_all()` method.
"""

from base64 import decodebytes
from io import BytesIO

import paramiko

from paperlesspermission.models import Guardian, Student, Faculty, Course, Section
from paperlesspermission.utils import bytes_io_to_tsv_dict_reader


class DJOImport():
    """Imports data from SQLRunner/Powerschool into Paperless Permission.

    Attributes:
        fs_classes (io.BytesIO): TSV file containing class data
        fs_faculty (io.BytesIO): TSV file containing faculty data
        fs_student (io.BytesIO): TSV file containing student data
        fs_parent (io.BytesIO): TSV file containing parent data
        fs_enrollment (io.BytesIO): TSV file containing enrollment data
    """

    def __init__(self, fs_classes, fs_faculty, fs_student, fs_parent, fs_enrollment):
        self.fs_classes = fs_classes
        self.fs_faculty = fs_faculty
        self.fs_student = fs_student
        self.fs_parent = fs_parent
        self.fs_enrollment = fs_enrollment

    @classmethod
    def GetFromSFTP(cls, hostname, username, password, ssh_fingerprint):
        """Constructor for `DJOImport` class that pull from remote SFTP server.

        This constructor takes SFTP connection information and pulls the TSV
        files needed to actually import data into the application.

        You will need to do some work to find the ssh-rsa key fingerprint of the
        server that you wish to connect to. We cannot guarantee that the running
        computer will have connected to this server before, so need to provide
        and validate the fingerprint ourself.

        On a Linux or BSD computer, use the following command to find the
        fingerprint data for your server (this example uses example.com as the
        hostname):

            $ ssh-keyscan example.com

        There may be several lines returned. You want the one that looks like
        this (the first line is a comment returned by the server and may be
        different):

            # example.com SSH-2.0-OpenSSH_7.6p1 Ubuntu-4ubuntu0.3
            example.com ssh-rsa AAAAB3NzaC1yc2DBWAKFDAQABA...

        The long string after `ssh-rsa` is the string that you want to pass to
        `ssh_fingerprint`.

        Parameters:
            hostname (String): Host to connect to SFTP Dropsite
            username (String): Username used to connect to SFTP Dropsite
            password (String): Password used to connect to SFTP Dropsite
            ssh_fingerprint (String): Obtained with `ssh-keyscan [hostname]` Use
                the value starting with `AAAA` after `ssh-rsa`. This value is
                used to authenticate the remote server and to prevent
                man-in-the-middle attacks.
        """

        # Take the given ssh_fingerprint and decode the RSA Key from it.
        key_fingerprint_data = ssh_fingerprint.encode()
        key = paramiko.RSAKey(data=decodebytes(key_fingerprint_data))

        ssh_client = paramiko.client.SSHClient()

        hostkeys = ssh_client.get_host_keys()
        hostkeys.add(hostname, 'ssh-rsa', key)

        fs_classes = BytesIO()
        fs_faculty = BytesIO()
        fs_student = BytesIO()
        fs_parent = BytesIO()
        fs_enrollment = BytesIO()

        try:
            ssh_client.connect(hostname, username=username,
                               password=password, look_for_keys=False, allow_agent=False)
            sftp_client = ssh_client.open_sftp()
            sftp_client.chdir('ps_data_export')

            sftp_client.getfo('fs_classes.txt', fs_classes)
            sftp_client.getfo('fs_faculty.txt', fs_faculty)
            sftp_client.getfo('fs_student.txt', fs_student)
            sftp_client.getfo('fs_parent.txt', fs_parent)
            sftp_client.getfo('fs_enrollment.txt', fs_enrollment)

            return cls(fs_classes, fs_faculty, fs_student, fs_parent, fs_enrollment)
        finally:
            ssh_client.close()

    def import_faculty(self):
        """Parses the fs_faculty file and imports to the database.

        Chances are you should be running import_all instead.
        """

        faculty_reader = bytes_io_to_tsv_dict_reader(self.fs_faculty)

        # Keep track of all written Faculty objects so we can later hide old
        # records that have been removed from the upstream data source.
        written_ids = []

        for row in faculty_reader:
            try:
                faculty_obj = Faculty.objects.get(person_id=row['RECORDID'])

                faculty_obj.first_name = row['FIRST_NAME']
                faculty_obj.last_name = row['LAST_NAME']
                faculty_obj.email = row['EMAIL_ADDR']
                faculty_obj.preferred_name = row['PREFERREDNAME']

                faculty_obj.save()
            except Faculty.DoesNotExist:
                faculty_obj = Faculty(
                    person_id=row['RECORDID'],
                    first_name=row['FIRST_NAME'],
                    last_name=row['LAST_NAME'],
                    email=row['EMAIL_ADDR'],
                    notify_cell=False,
                    preferred_name=row['PREFERREDNAME']
                )
                faculty_obj.save()
            finally:
                written_ids.append(row['RECORDID'])

        # If we didn't see any given Faculty IDs when running this import, set
        # their `hidden` value to `False`. This will hide their information from
        # certain sections of the UI while retaining historical records.
        for record in Faculty.objects.all():
            if record.person_id not in written_ids:
                record.hidden = True
                record.save()

    def import_classes(self):
        """Parses all courses and sections.

        Chances are you should be running import_all instead.

        All enrollment data is imported with the fs_enrollment after
        fs_students.

        The fs_classes file defines each `Section` in the school. There is no
        separate file for `Courses`; instead the course data is duplicated with
        each `Section` row. To import the classes:

        For each Section Row:
          - Look at the course ID (DCID or CID). Is it in the database yet? If
            not, add it.
          - Once the `Course` is taken care of we can then add the Section.

        Just like every other import, we'll need to keep track of each Course
        and Section ID that we find. Once finished importing the data we need to
        run through all the existing Courses and Sections to set the hidden flag
        on any records that have been deleted from the upstream data source.
        """

        classes_reader = bytes_io_to_tsv_dict_reader(self.fs_classes)

        # Keep track of all written Courses and Section objects.
        written_courses = []
        written_sections = []

        for row in classes_reader:
            # Handle the Course, but skip this step if we've already seen this
            # course.
            if row['COURSE_NUMBER'] not in written_courses:
                try:
                    course = Course.objects.get(
                        course_number=row['COURSE_NUMBER'])
                    course.course_name = row['COURSE_NAME']
                    course.hidden = False
                    course.save()
                except Course.DoesNotExist:
                    course = Course(
                        course_number=row['COURSE_NUMBER'],
                        course_name=row['COURSE_NAME'],
                        hidden=False
                    )
                    course.save()
                finally:
                    written_courses.append(row['COURSE_NUMBER'])

            # Handle the Section
            try:
                section = Section.objects.get(section_id=row['RECORDID'])
                section.course = course
                section.section_number = row['SECTION_NUMBER']
                section.teacher = Faculty.objects.get(person_id=row['TEACHER'])
                section.coteacher = Faculty.objects.get(
                    person_id=row['COTEACHER']) if row['COTEACHER'] else None
                section.school_year = row['SCHOOLYEAR']
                section.room = row['ROOM']
                section.period = row['EXPRESSION']
                section.hidden = False
                section.save()
            except Section.DoesNotExist:
                section = Section(
                    section_id=row['RECORDID'],
                    course=course,
                    section_number=row['SECTION_NUMBER'],
                    teacher=Faculty.objects.get(person_id=row['TEACHER']),
                    coteacher=Faculty.objects.get(
                        person_id=row['COTEACHER']) if row['COTEACHER'] else None,
                    school_year=row['SCHOOLYEAR'],
                    room=row['ROOM'],
                    period=row['EXPRESSION'],
                    hidden=False
                )
                section.save()
            finally:
                written_sections.append(row['RECORDID'])

        # If we didn't see any given Course ID when running the import, set
        # their hidden value to `False`. This will hide their information from
        # certain sections of the UI while retaining historical records.
        for course in Course.objects.all():
            if course.course_number not in written_courses:
                course.hidden = True
                course.save()

        # Same thing, only for the Section objects.
        for section in Section.objects.all():
            if section.section_id not in written_sections:
                section.hidden = True
                section.save()

    def import_students(self):
        """Parses all students."""

        student_reader = bytes_io_to_tsv_dict_reader(self.fs_student)

        # Keep track of all written Students objects
        written_students = []

        for row in student_reader:
            try:
                student = Student.objects.get(person_id=row['RECORDID'])
                student.grade_level = row['GRADE_LEVEL']
                student.first_name = row['FIRST_NAME']
                student.last_name = row['LAST_NAME']
                student.email = row['EMAIL']
                student.notify_cell = False
                student.hidden = False
                student.save()
            except Student.DoesNotExist:
                student = Student(
                    person_id=row['RECORDID'],
                    first_name=row['FIRST_NAME'],
                    last_name=row['LAST_NAME'],
                    email=row['EMAIL'],
                    notify_cell=False,
                    hidden=False,
                    grade_level=row['GRADE_LEVEL']
                )
                student.save()
            finally:
                written_students.append(row['RECORDID'])

        # If we didn't see any given Student IDs when running this import, set
        # their `hidden` value to `False`. This will hide their information from
        # certain sections of the UI while retaining historical records.
        for student in Student.objects.all():
            if student.person_id not in written_students:
                student.hidden = True
                student.save()

    def import_guardians(self):
        """Parses all parents and guardians.

        Chances are you should be running import_all instead.

        The (simplified) structure of this table is as follows:

            STUDENT_NUMBER
            CNT1_ID
            CNT1_FNAME
            CNT1_LNAME
            CNT1_REL
            CNT1_CPHONE
            CNT1_EMAIL
            CNT2_ID
            CNT2_FNAME
            CNT2_LNAME
            CNT2_REL
            CNT2_CPHONE
            CNT2_EMAIL
            CNT3_ID
            CNT3_FNAME
            CNT3_LNAME
            CNT3_REL
            CNT3_CPHONE
            CNT3_EMAIL

        Each `CNT{number}` block is potentially a new guardian. That said, they
        are also duplicated for each student that shares parents/guardians.
        """

        guardian_reader = bytes_io_to_tsv_dict_reader(self.fs_parent)

        written_guardians = []

        def handle_guardian(row, i):
            """Utility function to handle CNT{i}.

            Parameters:
                row (dict): csv.DictReader row for a student
                i (int): Which CNT number to handle
            """
            cnt_n = 'CNT{0}'.format(i)

            # This section is skipped if the guardian ID has been seen before.
            # This prevents the students from being cleared from the guardians
            # after the initial import.
            if row[cnt_n + '_ID'] and row[cnt_n + '_ID'] not in written_guardians:
                try:
                    guardian = Guardian.objects.get(
                        person_id=row[cnt_n + '_ID'])
                    guardian.first_name = row[cnt_n + '_FNAME']
                    guardian.last_name = row[cnt_n + '_LNAME']
                    guardian.email = row[cnt_n + '_EMAIL']
                    guardian.cell_number = row[cnt_n + '_CPHONE']
                    guardian.notify_cell = bool(row[cnt_n + '_CPHONE'])
                    guardian.hidden = False
                    guardian.relationship = row[cnt_n + '_REL']
                    guardian.students.clear()  # Clear students, these will be added back later
                    guardian.save()
                    return guardian
                except Guardian.DoesNotExist:
                    guardian = Guardian(
                        person_id=row[cnt_n + '_ID'],
                        first_name=row[cnt_n + '_FNAME'],
                        last_name=row[cnt_n + '_LNAME'],
                        email=row[cnt_n + '_EMAIL'],
                        cell_number=row[cnt_n + '_CPHONE'],
                        notify_cell=bool(row[cnt_n + '_CPHONE']),
                        hidden=False,
                        relationship=row[cnt_n + '_REL']
                    )
                    guardian.save()
                    return guardian
                finally:
                    written_guardians.append(row[cnt_n + '_ID'])
            elif row[cnt_n + '_ID']:
                return Guardian.objects.get(person_id=row[cnt_n + '_ID'])
            else:
                return None

        for row in guardian_reader:
            for i in range(1, 4):  # [1, 2, 3]
                guardian = handle_guardian(row, i)
                if not guardian:
                    continue
                guardian.students.add(Student.objects.get(
                    person_id=row['STUDENT_NUMBER']))
                guardian.save()

    def import_enrollment(self):
        """Parses all student enrollment data.

        Chances are you should be running import_all instead.
        """

        enrollment_reader = bytes_io_to_tsv_dict_reader(self.fs_enrollment)

        # Start by clearing all existing enrollment
        for student in Student.objects.all():
            student.section_set.clear()

        students_not_found = []
        for row in enrollment_reader:
            try:
                student = Student.objects.get(person_id=row['STUDENT_NUMBER'])
                student.section_set.add(Section.objects.get(
                    section_id=row['SECTIONID']))
            except Student.DoesNotExist:
                if row['STUDENT_NUMBER'] not in students_not_found:
                    students_not_found.append(row['STUDENT_NUMBER'])
                    print('Student: {0} does not exist!'.format(
                        row['STUDENT_NUMBER']))
        print(students_not_found)

    def import_all(self):
        """Runs all of the import functions in the correct order."""
        self.import_faculty()
        self.import_classes()
        self.import_students()
        self.import_guardians()
        self.import_enrollment()

    def close(self):
        """Closes the ByteIO buffers."""
        self.fs_classes.close()
        self.fs_enrollment.close()
        self.fs_faculty.close()
        self.fs_parent.close()
        self.fs_student.close()

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()
