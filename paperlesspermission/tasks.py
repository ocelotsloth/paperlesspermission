"""Defines celery tasks which can be asynchronously run.

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

from __future__ import absolute_import, unicode_literals

from celery import shared_task
from celery.utils.log import get_task_logger

from django.conf import settings
from django.core.mail import send_mass_mail

from .djo import DJOImport
from .models import FieldTrip, PermissionSlip, PermissionSlipLink

LOGGER = get_task_logger(__name__)

@shared_task
def async_print(value):
    print(value)


@shared_task
def async_djo_import_enrollment_data():
    """ Import all DJO enrollment data. """
    print("Importing DJO enrollment data")
    sftp_host = getattr(settings, 'DJO_SFTP_HOST')
    sftp_user = getattr(settings, 'DJO_SFTP_USER')
    sftp_pass = getattr(settings, 'DJO_SFTP_PASS')
    sftp_fingerprint = getattr(settings, 'DJO_SFTP_FINGERPRINT')
    djoimport = DJOImport.GetFromSFTP(sftp_host, sftp_user, sftp_pass, sftp_fingerprint)
    djoimport.import_all()


@shared_task
def async_generate_permission_slips(field_trip_id, notify=False):
    """ Generate permission slips for a field trip. """
    trip = FieldTrip.objects.get(id=field_trip_id)
    print("Generating permission slips for trip: {0}".format(field_trip_id))
    trip.generate_permission_slips()

    # Send notification emails if asked
    if notify:
        async_initial_trip_notifications.delay(field_trip_id)

@shared_task
def async_initial_trip_notifications(field_trip_id):
    """ Send trip notification emails. """
    # Fetch the field trip
    trip = FieldTrip.objects.get(id=field_trip_id)
    # Fetch all the permission slips
    slips = PermissionSlip.objects.filter(field_trip=trip)
    emails = []

    for slip in slips:
        emails.extend(slip.generate_emails())

    send_mass_mail(tuple(emails))

def async_resend_permission_slip(slip_id):
    """Resend notification for specific field trip."""
    slip = PermissionSlip.objects.get(id=slip_id)
    emails = slip.generate_emails()
    send_mass_mail(tuple(emails))
