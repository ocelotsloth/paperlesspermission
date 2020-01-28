from django.db import models
from phonenumber_field.modelfields import PhoneNumberField

class Person(models.Model):
    personID = models.IntegerField(unique=True)
    firstName = models.CharField(max_length=200)
    lastName = models.CharField(max_length=200)
    email = models.CharField(max_length=200)
    cell_number = PhoneNumberField()
    notify_cell = models.BooleanField()

    class Meta:
        abstract = True

    def __str__(self):
        return ("%s %s" % self.firstName, self.lastName)

class Guardian(Person):
    relationship = models.CharField(max_length=30)
    students = models.ManyToManyField('Student')

class Student(Person):
    gradeLevel = models.CharField(max_length=30)
    guardians = models.ManyToManyField(Guardian)

class Faculty(Person):
    preferredName = models.CharField(max_length=200)

    def __str__(self):
        return self.preferredName

class Course(models.Model):
    courseNumber = models.CharField(unique=True, max_length=30)
    courseName = models.CharField(max_length=200)

    def __str__(self):
        return self.courseName

class Section(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    sectionNumber = models.CharField(unique=False, max_length=30)
    teacher = models.ForeignKey(Faculty, on_delete=models.CASCADE)
    courseName = models.CharField(max_length=200)
    schoolYear = models.CharField(max_length=30)
    room = models.CharField(max_length=30)
    period = models.CharField(max_length=30)

    def __str__(self):
        return ("%s - Section %s" % self.course, self.sectionNumber)

class FieldTrip(models.Model):
    name = models.CharField(max_length=200)
    fromDate = models.DateTimeField()
    toDate = models.DateTimeField()
    students = models.ManyToManyField(Student)
    faculty = models.ManyToManyField(Faculty)
    courses = models.ManyToManyField(Course)
    sections = models.ManyToManyField(Section)

    def __str__(self):
        return self.name


