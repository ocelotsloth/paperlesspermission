import logging
import datetime

from django.http import HttpResponse
from django.template import loader
from django.shortcuts import render, get_object_or_404
from django.views.decorators.csrf import csrf_protect

from .forms import PermissionSlipFormStudent, PermissionSlipFormParent
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

    context = {
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
