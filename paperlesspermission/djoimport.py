"""Imports roster data from SQLRunner/Powerschool SIS.

This module defines the class responsible for importing data originating from
Powerschool. The data itself is exported by SQLRunner (an internal application
that negotiates a secure tunnel to Powerschool and runs queries) to CSV files
stored on an SFTP Server.
"""

import csv
from base64 import decodebytes
from io import BytesIO

import paramiko

from paperlesspermission.models import Guardian, GradeLevel, Student, Faculty, FieldTrip, Course, Section

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

        ssh_client.connect(hostname, username=username, password=password, look_for_keys=False, allow_agent=False)
        sftp_client = ssh_client.open_sftp()
        sftp_client.chdir('ps_data_export')

        self.fs_classes    = BytesIO()
        self.fs_faculty    = BytesIO()
        self.fs_student    = BytesIO()
        self.fs_parent     = BytesIO()
        self.fs_enrollment = BytesIO()

        sftp_client.getfo('fs_classes.txt', self.fs_classes)
        sftp_client.getfo('fs_faculty.txt', self.fs_faculty)
        sftp_client.getfo('fs_student.txt', self.fs_student)
        sftp_client.getfo('fs_parent.txt', self.fs_parent)
        sftp_client.getfo('fs_enrollment.txt', self.fs_enrollment)

        ssh_client.close()
