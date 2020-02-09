"""Defines the import command for manage.py."""

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
