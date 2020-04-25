"""Defines the views used by Paperless Permission.

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

import logging
import datetime

from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.template import loader
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.forms.models import model_to_dict
from django.utils import timezone
from django.db import transaction, DatabaseError

from .forms import PermissionSlipFormStudent, PermissionSlipFormParent, TripDetailForm
from .models import PermissionSlipLink, PermissionSlip, FieldTrip
from paperlesspermission.tasks import async_djo_import_enrollment_data, async_generate_permission_slips, async_initial_trip_notifications, async_resend_permission_slip

LOGGER = logging.getLogger(__name__)


def index(request):
    if request.user.is_authenticated:
        return redirect('/trip')
    else:
        return redirect('/login')


@login_required
def djo_import_all(request):
    context = {}


    async_djo_import_enrollment_data.delay()
    return render(request, 'paperlesspermission/index.html', context)


@csrf_protect
def slip(request, slip_id):

    slip_link = get_object_or_404(PermissionSlipLink, link_id=slip_id)
    permission_slip = slip_link.permission_slip
    field_trip = permission_slip.field_trip

    if slip_link.guardian:
        submission_type = 'Parent'
    elif slip_link.student:
        submission_type = 'Student'
    else:
        raise ValueError('No guardian or student present')

    if request.method == 'POST' and not (permission_slip.student_signature and permission_slip.guardian_signature):
        if submission_type == 'Parent':
            form = PermissionSlipFormParent(request.POST)
        elif submission_type == 'Student':
            form = PermissionSlipFormStudent(request.POST)

        if form.is_valid():
            complete = True
            if submission_type == 'Parent':
                permission_slip.guardian = slip_link.guardian
                permission_slip.guardian_signature = form.cleaned_data["name"]
                permission_slip.guardian_signature_date = timezone.now()
            elif submission_type == 'Student':
                permission_slip.student_signature = form.cleaned_data["name"]
                permission_slip.student_signature_date = timezone.now()
            permission_slip.save()
    else:
        if submission_type == 'Parent':
            form = PermissionSlipFormParent()
        elif submission_type == 'Student':
            form = PermissionSlipFormStudent()

    if (permission_slip.guardian_signature and permission_slip.student_signature):
        complete = max(permission_slip.guardian_signature_date,
                       permission_slip.student_signature_date)
    else:
        complete = False

    context = {
        'hide_login': True,
        'form': form,
        'trip_title': field_trip.name,
        'due_date': field_trip.due_date,
        'student_name': permission_slip.student.get_full_name(),
        'group_name': field_trip.group_name,
        'location': field_trip.location,
        'start_date': field_trip.start_date,
        'dropoff_location': field_trip.dropoff_location,
        'start_time': field_trip.dropoff_time,
        'end_date': field_trip.end_date,
        'end_time': field_trip.pickup_time,
        'pickup_location': field_trip.pickup_location,
        'submission_type': submission_type,
        'student_complete_date': permission_slip.student_signature_date,
        'guardian_complete_date': permission_slip.guardian_signature_date,
        'guardian_name': permission_slip.guardian.get_full_name(),
        'complete': complete,
    }
    return render(request, 'paperlesspermission/slip.html', context)

@login_required
def trip_list(request, show_hidden=False, message=None):
    """List all trips (user is authorized to see). Optionally display a message
    to the user. Set hidden to True to show current and archived trips."""
    if request.user.is_staff:
        # Show staff all open trips
        if show_hidden:
            trips = FieldTrip.objects()
        else:
            trips = FieldTrip.objects.filter(hidden=False)
    else:
        # Only show users Field Trips they are a coordinator for
        trips = FieldTrip.objects.filter(
            hidden=False,
            faculty__email=request.user.email
        )
    context = {
        'trips': trips,
        'message': message,
    }
    return render(request, 'paperlesspermission/trip_list.html', context)

@login_required
@csrf_protect
def trip_detail(request, trip_id, existing=True):
    """ View or modify trip details. POST while passing False to existing creates
    a new FieldTrip object. """
    trip = get_object_or_404(FieldTrip, id=trip_id) if existing else FieldTrip()

    # This point forward, we only have requests with valid or new trip_ids

    # 403 if user NOT authorized to view trip
    #   - A user is NOT authorized if:
    #       - User is NOT member of the admin staff staff
    #       - User is NOT listed in the field trip faculty coordinator list
    #       - User is NOT admin AND the trip status is NOT new.
    # TODO: Write test for this abomination of an if statement
    if (not request.user.is_staff
            and (not trip.faculty_is_moderator(request.user.email)
                 or trip.status != FieldTrip.NEW)):
        raise PermissionDenied

    # This point forward, we only have requests with valid or new trip_ids that
    # users are also authorized to view OR edit.

    # Next step is to determine if the form should be read-only or not
    #  - If trip is archived
    #  - If trip is approved and you are not admin staff
    #  - If trip is already released and you are not admin staff
    if (trip.status == FieldTrip.ARCHIVED
            or trip.status == FieldTrip.APPROVED and not request.user.is_staff
            or trip.status == FieldTrip.RELEASED and not request.user.is_staff):
        read_only = True
    else:
        read_only = False

    form = TripDetailForm(initial=model_to_dict(trip), read_only=read_only)
    title = 'Field Trip Detail' if existing else 'Create Field Trip'

    if request.method == 'POST':
        form = TripDetailForm(request.POST)
        if form.is_valid():
            if not existing:
                trip = FieldTrip()
            form.update_trip(trip)
            async_generate_permission_slips.delay(trip.id, notify=False)
            return redirect('/trip')

    context = {
        'title': title,
        'trip': trip,
        'form': form
    }
    return render(request, 'paperlesspermission/trip_detail.html', context)

@login_required
def approve_trip(request, trip_id):
    """Approves (if able) the given field trip and renders the trip list."""
    if not request.user.is_staff:
        raise PermissionDenied
    trip = get_object_or_404(FieldTrip, id=trip_id)
    try:
        trip.approve()
    except RuntimeError as err:
        LOGGER.error('ERROR Approving Trip id=%s: %s', trip.id, err)
        return trip_list(request, message="Cannot approve this trip.")
    else:
        return trip_list(request, message="Trip successfully approved.")

@login_required
def release_trip(request, trip_id):
    """Releases (if able) notifications for a given field trip and renders the
    trip list."""
    if not request.user.is_staff:
        raise PermissionDenied
    trip = get_object_or_404(FieldTrip, id=trip_id)
    try:
        with transaction.atomic():
            trip.release()
            trip.generate_permission_slips()
            trip.save()
    except RuntimeError as err:
        LOGGER.error('ERROR Releasing Trip id=%s: %s', trip.id, err)
        return trip_list(request, message="Cannot release this trip.")
    else:
        async_initial_trip_notifications(trip.id)
        return trip_list(request,
                         message="Trip notifications successfully released.")

@login_required
def archive_trip(request, trip_id):
    """Archives a trip."""
    if not request.user.is_staff:
        raise PermissionDenied
    trip = get_object_or_404(FieldTrip, id=trip_id)
    try:
        trip.archive()
    except RuntimeError as err:
        LOGGER.error('ERROR archiving trip id=%s: %s', trip.id, err)
        return trip_list(request, message="Cannot archive trip.")
    else:
        return trip_list(request, message="Trip successfully archived.")

@login_required
def trip_status(request, trip_id):
    """Show list of invited students and the status of their permission slip."""
    trip = get_object_or_404(FieldTrip, id=trip_id)

    if ((not request.user.is_staff)
            and (not trip.faculty_is_moderator(request.user.email))):
        raise PermissionDenied

    slips = PermissionSlip.objects.filter(field_trip__id=trip.id)

    context = {
        'trip': trip,
        'slips': slips,
    }
    return render(request, 'paperlesspermission/trip_status.html', context)

@login_required
@csrf_protect
def new_trip(request):
    return trip_detail(request, None, existing=False)

@login_required
def slip_reset(request, slip_id):
    if not request.user.is_staff:
        raise PermissionDenied
    permission_slip = get_object_or_404(PermissionSlip, id=slip_id)
    try:
        permission_slip.reset()
        permission_slip.save()
    except DatabaseError:
        return HttpResponse(status=500)
    else:
        return HttpResponse(status=204)

@login_required
def slip_resend(request, slip_id):
    if not request.user.is_staff:
        raise PermissionDenied
    permission_slip = get_object_or_404(PermissionSlip, id=slip_id)
    async_resend_permission_slip(permission_slip.id)
    return HttpResponse(status=204)
