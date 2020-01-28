from django.contrib import admin

from .models import Guardian
from .models import Student
from .models import Faculty
from .models import Course
from .models import Section
from .models import FieldTrip

admin.site.register(Guardian)
admin.site.register(Student)
admin.site.register(Faculty)
admin.site.register(Course)
admin.site.register(Section)
admin.site.register(FieldTrip)
