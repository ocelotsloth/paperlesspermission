"""Defines helper functions for use throughout the application.

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

from io import BytesIO, StringIO
from csv import DictReader
import logging


def bytes_io_to_string_io(bytes_io):
    return StringIO(bytes_io.getvalue().decode())


def bytes_io_to_tsv_dict_reader(bytes_io):
    return DictReader(bytes_io_to_string_io(bytes_io), delimiter='\t')


def disable_logging(f):
    def wrapper(*args):
        logging.disable(logging.WARNING)
        result = f(*args)
        logging.disable(logging.NOTSET)
        return result

    return wrapper
