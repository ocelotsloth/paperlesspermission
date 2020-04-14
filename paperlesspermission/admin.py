"""Registers Paperless Permission models with the admin interface.

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

from django.contrib import admin

from .models import Guardian
from .models import Student
from .models import Faculty
from .models import Course
from .models import Section
from .models import FieldTrip
from .models import PermissionSlip
from .models import PermissionSlipLink

admin.site.register(Guardian)
admin.site.register(Student)
admin.site.register(Faculty)
admin.site.register(Course)
admin.site.register(Section)
admin.site.register(FieldTrip)
admin.site.register(PermissionSlip)
admin.site.register(PermissionSlipLink)
