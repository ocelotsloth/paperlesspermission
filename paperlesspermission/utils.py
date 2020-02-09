"""Defines helper functions for use throughout the application."""

from io import BytesIO, StringIO

def BytesIO_to_StringIO(bytes_io):
    return StringIO(bytes_io.getvalue().decode())
