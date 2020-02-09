"""Defines all of the data models used in the application.

This file is used to define all of the data models used by Paperless Permission.
"""

from django.db import models
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
    person_id = models.IntegerField(unique=True)
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    email = models.EmailField(max_length=254)
    cell_number = PhoneNumberField()
    notify_cell = models.BooleanField()
    hidden = models.BooleanField(default=False)

    class Meta:
        abstract = True

    def __str__(self):
        return ("%s %s" % self.first_name, self.last_name)

class Guardian(Person):
    """Defines a student's parent/guardian.

    Extends the `Person` class. In practice these end up being Mothers, Fathers,
    Grandparents, or other legal custodians.

    Attributes:
        relationship (CharField): The relationship of the Guardian to the Student
        students (ManyToManyField): All of the students the guardian is related to
    """
    relationship = models.CharField(max_length=30)
    students = models.ManyToManyField('Student')

class GradeLevel(models.Model):
    """Defines the different grade levels a `Student` can be a member of.

    Attributes:
        name (CharField): The grade level identifier
    """
    name = models.CharField(max_length=30)

class Student(Person):
    """Defines a Student.

    Extends the `Person` class.

    Attributes:
        grade_level (ForeignKey): Foreign Key to the student's grade level
        guardians (ManyToManyField): All of the `Guardians` related to the Student
    """
    grade_level = models.ForeignKey(GradeLevel, on_delete=models.CASCADE)
    guardians = models.ManyToManyField(Guardian)

class Faculty(Person):
    """Defines Faculty/Staff that will run field trips.

    Attributes:
        preferred_name (CharField): Teachers might prefer to go by Mrs/Mr <last_name>
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
        hidden (BooleanField): Hides sections no longer present in upstream data
    """
    section_id = models.CharField(unique=True, max_length=30)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    section_number = models.CharField(unique=False, max_length=30)
    teacher = models.ForeignKey(Faculty, null=True, on_delete=models.SET_NULL)
    coteacher = models.ForeignKey(Faculty, null=True, on_delete=models.SET_NULL)
    school_year = models.CharField(max_length=30)
    room = models.CharField(max_length=30)
    period = models.CharField(max_length=30)
    hidden = models.BooleanField(default=False)

    def __str__(self):
        return ("%s - Section %s" % self.course, self.section_number)

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
        courses (ManyToManyField): Students enrolled in these courses during the
            relevent school year/semester will automatically be invited to
            attend this field trip
        sections (ManyToManyField): Students enrolled in these sections will
            automatically be invited to attend this field trip
        grade_levels (ManyToManyField): Students enrolled in these grade levels
            will automatically be invited to attend this field trip
    """
    name = models.CharField(max_length=200)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    students = models.ManyToManyField(Student)
    faculty = models.ManyToManyField(Faculty)
    courses = models.ManyToManyField(Course)
    sections = models.ManyToManyField(Section)
    grade_levels = models.ManyToManyField(GradeLevel)

    def __str__(self):
        return self.name
