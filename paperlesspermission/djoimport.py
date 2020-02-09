"""Imports roster data from SQLRunner/Powerschool SIS.

This module defines the class responsible for importing data originating from
Powerschool. The data itself is exported by SQLRunner (an internal application
that negotiates a secure tunnel to Powerschool and runs queries) to CSV files
stored on an SFTP Server.
"""

import csv
from base64 import decodebytes
from io import BytesIO, StringIO

import paramiko

from paperlesspermission.models import Guardian, GradeLevel, Student, Faculty, FieldTrip, Course, Section
from paperlesspermission.utils import BytesIO_to_StringIO

class DJOImport(object):
    """Imports data from SQLRunner/Powerschool into Paperless Permission.

    Attributes:
        fs_classes (io.BytesIO): TSV file containing class data
        fs_faculty (io.BytesIO): TSV file containing faculty data
        fs_student (io.BytesIO): TSV file containing student data
        fs_parent (io.BytesIO): TSV file containing parent data
        fs_enrollment (io.BytesIO): TSV file containing enrollment data
    """

    def __init__(self, hostname, username, password, ssh_fingerprint):
        """The constructor for `DJOImport` class.

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

        self.fs_classes    = BytesIO()
        self.fs_faculty    = BytesIO()
        self.fs_student    = BytesIO()
        self.fs_parent     = BytesIO()
        self.fs_enrollment = BytesIO()

        try:
            ssh_client.connect(hostname, username=username, password=password, look_for_keys=False, allow_agent=False)
            sftp_client = ssh_client.open_sftp()
            sftp_client.chdir('ps_data_export')

            sftp_client.getfo('fs_classes.txt', self.fs_classes)
            sftp_client.getfo('fs_faculty.txt', self.fs_faculty)
            sftp_client.getfo('fs_student.txt', self.fs_student)
            sftp_client.getfo('fs_parent.txt', self.fs_parent)
            sftp_client.getfo('fs_enrollment.txt', self.fs_enrollment)
        finally:
            ssh_client.close()

    def import_faculty(self):
        """Parses the fs_faculty file and imports to the database."""

        # csv.reader requires a StringIO file-like-object, not a BytesIO
        faculty_data = BytesIO_to_StringIO(self.fs_faculty.getvalue().decode())

        faculty_reader = csv.DictReader(faculty_data, delimiter='\t')

        # Keep track of all written Faculty objects so we can later hide old
        # records that have been removed from the upstream data source.
        written_ids = []

        for row in faculty_reader:
            try:
                faculty_obj = Faculty.objects.get(person_id=row['RECORDID'])

                faculty_obj.first_name     = row['FIRST_NAME']
                faculty_obj.last_name      = row['LAST_NAME']
                faculty_obj.email          = row['EMAIL_ADDR']
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

        All enrollment data is imported with the Students.

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

        # csv.reader requires a StringIO file-like object, not a BytesIO
        classes_data = BytesIO_to_StringIO(self.fs_classes)

        classes_reader = csv.DictReader(classes_data, delimiter='\t')

        # Keep track of all written Courses and Section objects.
        written_courses  = []
        written_sections = []

        for row in classes_reader:
            # Handle the Course
            try:
                course = Course.objects.get(course_number=row['COURSE_NUMBER'])
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
                section = Section.objects.get(section_number=row['RECORDID'])
                section.course = course
                section.section_number = row['SECTION_NUMBER']
                section.teacher = Faculty.objects.get(person_id=row['TEACHER'])
                section.coteacher = Faculty.objects.get(person_id=row['COTEACHER']) if row['COTEACHER'] else None
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
                    coteacher=Faculty.objects.get(person_id=row['COTEACHER']) if row['COTEACHER'] else None,
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
