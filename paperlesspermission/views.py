import logging
import datetime

from django.http import HttpResponse
from django.template import loader
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.forms.models import model_to_dict

from .forms import PermissionSlipFormStudent, PermissionSlipFormParent, TripDetailForm
from .models import PermissionSlipLink, PermissionSlip, FieldTrip

LOGGER = logging.getLogger(__name__)


def index(request):
    context = {}
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

    if request.method == 'POST' and not permission_slip.complete:
        if submission_type == 'Parent':
            form = PermissionSlipFormParent(request.POST)
        elif submission_type == 'Student':
            form = PermissionSlipFormStudent(request.POST)

        if form.is_valid():
            complete = True
            if submission_type == 'Parent':
                permission_slip.guardian = slip_link.guardian
                permission_slip.guardian_signature = form.cleaned_data["name"]
                permission_slip.guardian_signature_date = datetime.datetime.now()
            elif submission_type == 'Student':
                permission_slip.student_signature = form.cleaned_data["name"]
                permission_slip.student_signature_date = datetime.datetime.now()
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
        'student_name': permission_slip.student,
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
        'complete': complete,
    }
    return render(request, 'paperlesspermission/slip.html', context)

@login_required
def trip_list(request):
    trips = FieldTrip.objects.filter(hidden=False)
    context = {
        'trips': trips
    }
    return render(request, 'paperlesspermission/trip_list.html', context)

@login_required
@csrf_protect
def trip_detail(request, trip_id, existing=True):
    """ View or modify trip details. POST while passing False to existing creates
    a new FieldTrip object. """
    trip = get_object_or_404(FieldTrip, id=trip_id) if existing else FieldTrip()
    form = TripDetailForm(initial=model_to_dict(trip))
    title = 'Field Trip Detail' if existing else 'Create Field Trip'

    if request.method == 'POST':
        form = TripDetailForm(request.POST)
        if form.is_valid():
            if not existing:
                trip = FieldTrip()
            form.update_trip(trip)
            return redirect('/trip')

    context = {
        'title': title,
        'trip': trip,
        'form': form
    }
    return render(request, 'paperlesspermission/trip_detail.html', context)

@login_required
@csrf_protect
def new_trip(request):
    return trip_detail(request, None, existing=False)
