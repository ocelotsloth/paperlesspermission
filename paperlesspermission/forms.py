"""Defines forms used by Paperless Permission.

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
from django import forms
from django.db import transaction
from .models import Student, Faculty, Course, Section
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Fieldset, ButtonHolder, Row, Column
from django_select2.forms import Select2MultipleWidget
from bootstrap_datepicker_plus import DatePickerInput, TimePickerInput

class PermissionSlipFormParent(forms.Form):
    helper = FormHelper()

    name = forms.CharField(required=True, label='Enter your name.')
    electronic_consent = forms.BooleanField(required=True, label='By checking this box you consent to electronically signing this document.')


class PermissionSlipFormStudent(forms.Form):
    helper = FormHelper()

    name = forms.CharField(required=True, label='Enter your name.')
    electronic_consent = forms.BooleanField(required=True, label='By checking this box you signal that you have read and understand that the school handbook rules are in effect during this field trip.')

class TripDetailForm(forms.Form):
    def __init__(self, *args, read_only=False, **kwargs):
        super(TripDetailForm, self).__init__(*args, **kwargs)
        self.read_only = read_only
        self.helper = FormHelper(self)
        self.helper.html5_required = True
        if not read_only:
            self.helper.add_input(Submit('submit', 'Save'))
        if read_only:
            for _, field in self.fields.items():
                field.disabled = True
        self.helper.layout = Layout(
            Fieldset('Trip Details',
                Row(
                    Column('name'),
                    Column('due_date'),
                ),
                Row(
                    Column('group_name'),
                    Column('location'),
                ),
                Row(Column('faculty')),
            ),
            Fieldset('Scheduling Information',
                Row(
                    Column('start_date', 'dropoff_time', 'dropoff_location'),
                    Column('end_date', 'pickup_time', 'pickup_location'),
                ),
            ),
            Fieldset('Invited Participants',
                Row(Column('students')),
                Row(Column('courses')),
                Row(Column('sections')),
            )
        )

    name = forms.CharField(required=True, label='Trip Name')
    due_date = forms.DateField(
        required=True,
        widget=DatePickerInput(attrs={'autocomplete': 'off'}),
        label='Permission Slip Due Date',
    )
    group_name = forms.CharField(required=True, label='Group Name')
    location = forms.CharField(required=True, label='Trip Location')
    start_date = forms.DateField(
        required=True,
        widget=DatePickerInput(attrs={'autocomplete': 'off'}),
        label='Trip Start Date'
    )
    dropoff_time = forms.TimeField(
        required=True,
        widget=TimePickerInput(attrs={'autocomplete': 'off'}),
        label='Dropoff Time',
    )
    dropoff_location = forms.CharField(required=True, label='Dropoff Location')
    end_date = forms.DateField(
        required=True,
        widget=DatePickerInput(attrs={'autocomplete': 'off'}),
        label='Trip End Date',
    )
    pickup_time = forms.TimeField(
        required=True,
        widget=TimePickerInput(attrs={'autocomplete': 'off'}),
        label='Pickup Time',
    )
    pickup_location = forms.CharField(required=True, label='Pickup Location')
    faculty = forms.ModelMultipleChoiceField(
        required=True,
        label="Faculty/Staff Coordinators",
        widget=Select2MultipleWidget,
        queryset=Faculty.objects.filter(hidden=False)
    )
    students = forms.ModelMultipleChoiceField(
        required=False,
        label="Students Invited",
        widget=Select2MultipleWidget,
        queryset=Student.objects.filter(hidden=False)
    )
    courses = forms.ModelMultipleChoiceField(
        required=False,
        label="Courses Invited",
        widget=Select2MultipleWidget,
        queryset=Course.objects.filter(hidden=False)
    )
    sections = forms.ModelMultipleChoiceField(
        required=False,
        label="Sections Invited",
        widget=Select2MultipleWidget,
        queryset=Section.objects.filter(hidden=False)
    )

    @transaction.atomic
    def update_trip(self, trip):
        if self.has_changed():
            trip.name = self.cleaned_data['name']
            trip.due_date = self.cleaned_data['due_date']
            trip.group_name = self.cleaned_data['group_name']
            trip.location = self.cleaned_data['location']
            trip.start_date = self.cleaned_data['start_date']
            trip.dropoff_time = self.cleaned_data['dropoff_time']
            trip.dropoff_location = self.cleaned_data['dropoff_location']
            trip.end_date = self.cleaned_data['end_date']
            trip.pickup_time = self.cleaned_data['pickup_time']
            trip.pickup_location = self.cleaned_data['pickup_location']
            trip.save()
            trip.students.set(self.cleaned_data['students'])
            trip.faculty.set(self.cleaned_data['faculty'])
            trip.courses.set(self.cleaned_data['courses'])
            trip.sections.set(self.cleaned_data['sections'])
            trip.save()
