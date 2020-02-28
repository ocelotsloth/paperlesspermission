"""Defines the import command for manage.py.

Copyright 2020 Mark Stenglein, The Paperless Permission Authors

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

from django.core.management.base import BaseCommand
from paperlesspermission.djo import DJOImport


class Command(BaseCommand):
    """Import command imports data from SFTP dropsite."""

    help = 'Imports data from SFTP dropsite.'

    def add_arguments(self, parser):
        parser.add_argument('hostname', nargs='?', type=str,
                            help='Server hostname or IP address to connect to')
        parser.add_argument('username', nargs='?', type=str,
                            help='Username to connect over SFTP with')
        parser.add_argument('password', nargs='?', type=str,
                            help='Password to connect over SFTP with')
        parser.add_argument('rsa_fingerprint', nargs='?',
                            type=str, help='RSA Fingerprint of SSH Server')

    def handle(self, *args, **options):
        with DJOImport(options['hostname'], options['username'],
                       options['password'], options['rsa_fingerprint']) as importer:
            importer.import_all()
