"""Defines helper functions for use throughout the application."""

from io import BytesIO, StringIO
from csv import DictReader


def bytes_io_to_string_io(bytes_io):
    return StringIO(bytes_io.getvalue().decode())


def bytes_io_to_tsv_dict_reader(bytes_io):
    return DictReader(bytes_io_to_string_io(bytes_io), delimiter='\t')
