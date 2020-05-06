"""Defines all of the data models used in the application.

This file is used to define all of the data models used by Paperless
Permission.

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

from hashlib import sha256

from django.db import models
from django.db.models import Q
from django.db import transaction
from django.conf import settings

from phonenumber_field.modelfields import PhoneNumberField

class Person(models.Model):
    """This is an abstract class that defines the common attributes of people.

    Attributes:
        person_id (CharField): The unique identifier for the person
        first_name (CharField): First Name
        last_name (CharField): Last Name
        email (EmailField): Email address
        cell_number (PhoneNumberField): Cell phone number
        notify_cell (BooleanField): Whether or not to send SMS messages
        hidden (BooleanField): Hide persons no longer in upstream data source
    """
    person_id = models.CharField(unique=True, max_length=200)
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    email = models.EmailField(max_length=254)
    cell_number = PhoneNumberField()
    notify_cell = models.BooleanField()
    hidden = models.BooleanField(default=False)

    class Meta:
        abstract = True

    def get_full_name(self):
        """Returns the full name of a person"""
        return '{0} {1}'.format(self.first_name, self.last_name)

    def __str__(self):
        return '{0} {1}'.format(self.first_name, self.last_name)


class Guardian(Person):
    """Defines a student's parent/guardian.

    Extends the `Person` class. In practice these end up being Mothers,
    Fathers, Grandparents, or other legal custodians.

    Attributes:
        relationship (CharField): The relationship of the Guardian to the
            Student
        students (ManyToManyField): All of the students the guardian is
            related to
    """
    relationship = models.CharField(max_length=30)
    students = models.ManyToManyField('Student')


class Student(Person):
    """Defines a Student.

    Extends the `Person` class.

    Attributes:
        grade_level (String): Student's grade level
        guardians (ManyToManyField): All of the `Guardians` related to the
            Student
    """
    FRESHMAN = 'FR'
    SOPHOMORE = 'SO'
    JUNIOR = 'JR'
    SENIOR = 'SR'
    GRADE_LEVEL_CHOICES = [
        (FRESHMAN, 'Freshman'),
        (SOPHOMORE, 'Sophomore'),
        (JUNIOR, 'Junior'),
        (SENIOR, 'Senior'),
    ]
    grade_level = models.CharField(
        max_length=2,
        choices=GRADE_LEVEL_CHOICES,
    )

    def __str__(self):
        return self.email.split('@')[0]


class Faculty(Person):
    """Defines Faculty/Staff that will run field trips.

    Attributes:
        preferred_name (CharField): Teachers might prefer to go by Mrs/Mr
            <last_name>
    """
    preferred_name = models.CharField(max_length=200)

    def __str__(self):
        return self.preferred_name


class Course(models.Model):
    """Defines a `Course`.

    This is the container for individual `Section` objects.

    Attributes:
        course_number (CharField): The course identifier
        course_name (CharField): The name of the course
        hidden (BooleanField): Hides courses no longer present in upstream data
    """
    course_number = models.CharField(unique=True, max_length=30)
    course_name = models.CharField(max_length=200)
    hidden = models.BooleanField(default=False)

    def __str__(self):
        return self.course_name


class Section(models.Model):
    """Defines a `Section` of a `Course`.

    Attributes:
        section_id (CharField): Section Unique Identifier
        course (ForeignKey): FK to `Course`
        section_number (CharField): The section identifier
        teacher (ForeignKey): FK to `Faculty`
        coteacher (ForeignKey): FK to `Faculty`, can be set Null
        school_year (CharField): School year the section is held in
        room (CharField): Room the section is held in
        period (CharField): Period the section is held during
        hidden (BooleanField): Hides sections no longer present in upstream
            data
    """
    section_id = models.CharField(unique=True, max_length=30)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    section_number = models.CharField(unique=False, max_length=30)
    teacher = models.ForeignKey(Faculty, null=True, on_delete=models.SET_NULL)
    coteacher = models.ForeignKey(
        Faculty,
        null=True,
        on_delete=models.SET_NULL,
        related_name='coteacher_set'
    )
    school_year = models.CharField(max_length=30)
    room = models.CharField(max_length=30)
    period = models.CharField(max_length=30)
    hidden = models.BooleanField(default=False)
    students = models.ManyToManyField(Student)

    def __str__(self):
        return "{0} - Section {1}".format(self.course, self.section_number)


class FieldTrip(models.Model):
    """Defines a `FieldTrip`.

    Attributes:
        name (CharField): Name of the Field Trip
        start_date (DateTimeField): Start date/time.
        end_date (DateTimeField): End date/time.
        students (ManyToManyField): All students invited to attend the Field
            Trip
        faculty (ManyToManyField): All faculty/staff invited to administer the
            Field Trip
        courses (ManyToManyField): Students enrolled in these courses during
            the relevent school year/semester will automatically be invited to
            attend this field trip
        sections (ManyToManyField): Students enrolled in these sections will
            automatically be invited to attend this field trip
        grade_levels (ManyToManyField): Students enrolled in these grade levels
            will automatically be invited to attend this field trip
        status (IntegerField Choice): Current status of the trip. DO NOT update
            this field directly. Instead use the appropriate approve(),
            initial_notify(), or archive() method.
    """
    name = models.CharField(max_length=100)
    group_name = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    start_date = models.DateField()
    dropoff_time = models.TimeField()
    dropoff_location = models.CharField(max_length=100)
    end_date = models.DateField()
    pickup_time = models.TimeField()
    pickup_location = models.CharField(max_length=100)
    students = models.ManyToManyField(Student, blank=True)
    faculty = models.ManyToManyField(Faculty)
    courses = models.ManyToManyField(Course, blank=True)
    sections = models.ManyToManyField(Section, blank=True)
    grade_levels = models.CharField(max_length=30, null=True, blank=True)
    due_date = models.DateField()
    hidden = models.BooleanField(default=False)

    # Default value. This is set when a teacher submits a new trip. While the
    # status is still 0, teachers are still able to make changes.
    #
    # Emails to students and guardians MUST NOT be sent for trips in this
    # status.
    #
    # TODO: write test to verify this behavior
    NEW = 0
    # Approved is set after Administrator approves the trip. This MUST prevent
    # teachers from making changes to the trip.
    #
    # Emails to students and guardians MAY be sent for trips in this status.
    # Once sent, the status MUST be updated to IN_PROGRESS.
    #
    # TODO: write test to verify this behavior
    APPROVED = 1
    # After the Admin sends the initial notifications out, the status is changed
    # to RELEASED. Admins can still make changes, but will be shown a
    # warning.
    #
    # Emails to students and guardians MAY be sent for trips in this status.
    # These emails SHOULD NOT be sent to for permission slips that have been
    # completed by the student and one Guardian.
    #
    # RELEASED trips SHOULD NOT be set back to APPROVED.
    #                MUST NOT be set back to NEW.
    #
    # TODO: write test to verify this behavior
    RELEASED = 2
    # Once the due-date passes, the trip is locked, archived and cannot be
    # changed.
    #
    # Emails MUST NOT be sent for trips in this status.
    #
    # ARCHIVED trips MUST NOT be set back to NEW.
    #                MUST NOT be set back to APPROVED.
    #                SHOULD NOT be set back to IN_PROGRESS.
    #                SHOULD NOT be modified. Their slips or slip-links either.
    #
    # TODO: write test to verify this behavior
    ARCHIVED = 3
    STATUS_CHOICES = (
        (NEW, 'New'),
        (APPROVED, 'Approved'),
        (RELEASED, 'Released'),
        (ARCHIVED, 'Archived'),
    )
    status = models.IntegerField(choices=STATUS_CHOICES, default=NEW)

    def faculty_is_moderator(self, email):
        """Returns whether a faculty member is a moderator for a trip.

        The search is performed using the email address.
        """
        return self.faculty.all().filter(email=email).exists()

    @transaction.atomic
    def approve(self):
        """Approves a field trip. Do not run this before authenticating user.

        Ideally you would run this method from within a transaction."""

        if self.status != self.NEW:
            # No need to do anything if the trip is already approved.
            return

        self.status = self.APPROVED
        self.save()

    def release(self):
        """Sets the status to IN_PROGRESS. You are repsonsible for sending
        notifications by yourself."""

        if self.status != self.APPROVED:
            raise RuntimeError('FieldTrip cannot be released if it is not currently Approved')

        self.status = self.RELEASED

    @transaction.atomic
    def archive(self):
        """Sets the status to ARCHIVED. Any further modifications will be
        frozen.

        This method should be run from within a transaction."""

        self.status = self.ARCHIVED
        self.hidden = True
        self.save()

    def generate_permission_slips(self, force=False):
        """Generates permission slips for all included students.

        Note: This method uses boolean algebra of sets to generate a
              distinct list of all included students.
        """

        if (not force) and (self.status == self.ARCHIVED):
            raise RuntimeError("Should not modify archived trip. Unarchive or use force=True.")

        # Add students
        student_list = self.students.all()
        # Add all students in included courses
        for course in self.courses.all():
            for section in Section.objects.filter(course=course):
                student_list = student_list | section.students.all()
        # Add all students in included section
        for section in self.sections.all():
            student_list = student_list | section.students.all()
        # Add all students in included grade levels
        student_list = student_list | Student.objects.filter(grade_level__in=[self.grade_levels])

        # Actually generate the permission slips
        for student in student_list:
            permission_slip, created = PermissionSlip.objects.get_or_create(
                field_trip=self,
                student=student,
                defaults={'flagged_for_review': False}
            )
            if created:
                permission_slip.generate_slip_links()

    def __str__(self):
        return self.name


class PermissionSlip(models.Model):
    field_trip = models.ForeignKey(FieldTrip, on_delete=models.PROTECT)
    guardian = models.ForeignKey(Guardian, null=True, blank=True, on_delete=models.PROTECT)
    student = models.ForeignKey(Student, on_delete=models.PROTECT)
    due_date = models.DateField(null=True, blank=True)  # overrides FieldTrip
    student_signature = models.CharField(max_length=100, null=True, blank=True)
    student_signature_date = models.DateTimeField(null=True, blank=True)
    guardian_signature = models.CharField(max_length=100, null=True, blank=True)
    guardian_signature_date = models.DateTimeField(null=True, blank=True)
    flagged_for_review = models.BooleanField(default=False, blank=True)

    def reset(self):
        self.guardian = None
        self.student_signature = None
        self.student_signature_date = None
        self.guardian_signature = None
        self.guardian_signature_date = None
        self.flagged_for_review = False

    def generate_slip_links(self):
        # Get list of all guardians of this student
        student_guardians = Guardian.objects.filter(students__id=self.student.id)

        # Generate link for student (if not created already)
        PermissionSlipLink.objects.get_or_create(
            permission_slip=self,
            student=self.student
        )

        # Generate links for each guardian (if not created already)
        for guardian in student_guardians:
            PermissionSlipLink.objects.get_or_create(
                permission_slip=self,
                guardian=guardian
            )

    def generate_emails(self):
        slip_links = PermissionSlipLink.objects.filter(permission_slip=self)
        emails = []
        student = self.student
        efrom = getattr(settings, 'EMAIL_FROM_ADDRESS')
        base_url = getattr(settings, 'BASE_URL')
        for slip_link in slip_links:

            if slip_link.guardian:
                to = [slip_link.guardian.email]
                subject = 'New Permission Slip for {0}'.format(student.get_full_name())
                message = """{0},

There is a new permission slip for you to fill out for your student, {1}.

Trip: {2}
Location: {3}
Date: {4}
Permission Slip Link (click): {5}

Please visit the above link to view and fill out the permission slip by the due date, {6}.

Thank you for your time,

-- 
DJO Activities Office""".format(
                    slip_link.guardian.get_full_name(),
                    student.get_full_name(),
                    self.field_trip.name,
                    self.field_trip.location,
                    self.field_trip.start_date,
                    "{0}/slip/{1}".format(base_url, slip_link.link_id),
                    self.field_trip.due_date
                )
            elif slip_link.student:
                to = [slip_link.student.email]
                subject = 'New Permission Slip for {0}'.format(self.field_trip.name)
                message = """{0},

There is a new permission slip for you to fill out:

Trip: {1}
Location: {2}
Date: {3}
Permission Slip Link (click): {4}

Please visit the above link to view and fill out the permission slip by the due date, {5}

Thank you for your time,

-- 
DJO Activities Office""".format(
                    slip_link.student.get_full_name(),
                    self.field_trip.name,
                    self.field_trip.location,
                    self.field_trip.start_date,
                    "{0}/slip/{1}".format(base_url, slip_link.link_id),
                    self.field_trip.due_date
                )

            emails.append((subject, message, efrom, to))
        return emails

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=(
                    Q(student_signature__isnull=True) &
                    Q(student_signature_date__isnull=True)
                ) | (
                    Q(student_signature__isnull=False) &
                    Q(student_signature_date__isnull=False)
                ),
                name='stu sig and sig date must both be null or non-null.'
            ),
            models.CheckConstraint(
                check=(
                    Q(guardian_signature__isnull=True) &
                    Q(guardian_signature_date__isnull=True) &
                    Q(guardian__isnull=True)
                ) | (
                    Q(guardian_signature__isnull=False) &
                    Q(guardian_signature_date__isnull=False) &
                    Q(guardian__isnull=False)
                ),
                name='guard, guard sig and sig date must both be null or non-null.'
            ),
            models.UniqueConstraint(
                fields=['field_trip', 'student'],
                name='Each stu can have at most one slip per field trip.'
            )
        ]


class PermissionSlipLink(models.Model):
    permission_slip = models.ForeignKey(
        PermissionSlip, on_delete=models.PROTECT)
    guardian = models.ForeignKey(Guardian, on_delete=models.PROTECT, null=True, blank=True)
    student = models.ForeignKey(Student, on_delete=models.PROTECT, null=True, blank=True)
    link_id = models.CharField(max_length=64, unique=True, blank=True, null=True)
    last_sent = models.DateTimeField(null=True, blank=True)

    def calculate_link_id(self):
        """Generates a hash-based link identifier for a permission slip link."""
        salt = getattr(settings, "LINK_ID_SALT", '')
        if self.guardian:
            person_id = self.guardian.person_id
        elif self.student:
            person_id = self.student.person_id
        else:
            raise ValueError("No student or guardian set")

        link_composite = '{0}-{1}-{2}'.format(
            salt, self.permission_slip.id, person_id).encode()

        self.link_id = sha256(link_composite).hexdigest()

    def save(self, *args, **kwargs):
        """Overrides default save method by calculating the link_id."""
        self.calculate_link_id()
        super(PermissionSlipLink, self).save(*args, **kwargs)

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=(
                    Q(guardian__isnull=True) &
                    Q(student__isnull=False)
                ) | (
                    Q(guardian__isnull=False) &
                    Q(student__isnull=True)
                ),
                name='Only tied to one person.'
            )
        ]
