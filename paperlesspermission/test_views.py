"""Test module for views.py

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

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied

import paperlesspermission.views as views
import paperlesspermission.models as models

class ViewTest(TestCase):
    def setUp(self):
        super(ViewTest, self).setUp()

        logging.disable(logging.CRITICAL)

        self.teacher_user = User.objects.create_user('teacher',
                email='tuser@school.test', password='test')

        self.admin_user = User.objects.create_user('admin',
                email='auser@school.test', password='test')
        self.admin_user.is_staff = True
        self.admin_user.save()

        self.super_user = User.objects.create_superuser('super',
                email='suser@school.test', password='test')

        self.student1 = models.Student(
            person_id='202300001',
            first_name='Test',
            last_name='Student',
            email='tstudent@school.test',
            cell_number='+17035555555',
            notify_cell=True,
            grade_level=models.Student.FRESHMAN
        )
        self.student1.save()

        self.guardian1 = models.Guardian(
            person_id='2001',
            first_name='Guardian',
            last_name='Student',
            email='gstudent@email.test',
            cell_number='+17035555555',
            notify_cell=True,
        )
        self.guardian1.save()
        self.guardian1.students.add(self.student1)
        self.guardian1.save()

        self.teacher1 = models.Faculty(
            person_id='1000001',
            first_name='Teacher',
            last_name='User',
            email='tuser@school.test',
            cell_number='+17035555555',
            notify_cell=True,
            preferred_name='Mrs. Teacher'
        )
        self.teacher1.save()

        self.course100 = models.Course(
            course_number='100',
            course_name='English 1'
        )
        self.course100.save()

        self.section101 = models.Section(
            section_id='100101',
            course=self.course100,
            section_number='101',
            teacher=self.teacher1,
            school_year='2020',
            room='202',
            period='2nd'
        )
        self.section101.save()
        self.section101.students.add(self.student1)
        self.section101.save()

    def tearDown(self):
        super(ViewTest, self).tearDown()

        logging.disable(logging.NOTSET)

    def check_view_redirect(self, url, expected_redirect, user=None):
        """Ensure an authenticated user is redirected to /trip

        Run this function in other test cases. This allows for testing
        multiple types of users."""
        if user is not None:
            self.client.force_login(user)
        response = self.client.get(url)

        # Check that status code is a redirect
        self.assertEqual(response.status_code, 302)

        # Check that response class is HttpResponseRedirect
        self.assertEqual(response.__class__.__name__, 'HttpResponseRedirect')

        # Check that the redirect URL is to '/trip'
        self.assertEqual(response.url, expected_redirect)


class IndexViewTests(ViewTest):
    """Test cases for the index view"""
    def test_index_view_exists(self):
        """Tests to ensure the index view exists"""
        self.assertTrue(hasattr(views, 'index'))

    def test_index_view_mapped_correctly(self):
        """Ensure that the index view is mapped to '/'"""
        self.assertEqual(reverse('index'), '/')

    def test_index_view_not_authenticated_redirect(self):
        """Ensure an unauthenticated user is redirected to /login"""
        self.check_view_redirect(reverse('index'), '/login')

    def test_index_view_authenticated_redirect_teacher(self):
        """Test index redirect for teacher user"""
        self.check_view_redirect(reverse('index'), '/trip', self.teacher_user)

    def test_index_view_authenticated_redirect_admin(self):
        """Test index redirect for admin user"""
        self.check_view_redirect(reverse('index'), '/trip', self.admin_user)

    def test_index_view_authenticated_redirect_superuser(self):
        """Test index redirect for super user"""
        self.check_view_redirect(reverse('index'), '/trip', self.super_user)

class DJOImportAllViewTests(ViewTest):
    def test_djo_import_all_view_exists(self):
        """Ensure that the djo_import_all view exists."""
        self.assertTrue(hasattr(views, 'djo_import_all'))

    def test_djo_import_all_view_mapped_correctly(self):
        """Ensure that the URL mapping is correct."""
        self.assertEqual(reverse('import all'), '/import/')

    def test_djo_import_all_view_unauthenticated(self):
        """Ensure import view cannot be run while unauthenticated."""
        self.check_view_redirect(reverse('import all'), '/login?next=/import/')

    def test_djo_import_all_not_staff(self):
        """Ensure import view cannot be run while not logged in as admin."""
        self.client.force_login(self.teacher_user)
        response = self.client.get(reverse('import all'))

        # Check that status code is set to 403
        self.assertEqual(response.status_code, 403)

        # Check that response type is ResponseForbidden
        self.assertEqual(response.__class__.__name__, 'HttpResponseForbidden')

    def test_djo_import_all_staff_allowed(self):
        """Ensure djo_import_all runs when logged in as admin."""
        self.client.force_login(self.admin_user)
        response = self.client.get(reverse('import all'))

        # Check that the call returns success (HTTP 204 No Content)
        self.assertEqual(response.status_code, 204)

    def test_djo_import_all_staff_allowed_super(self):
        """Ensure super users are able to run djo_import_all."""
        self.client.force_login(self.super_user)
        response = self.client.get(reverse('import all'))

        # Check that the call returns success (HTTP 204 No Content)
        self.assertEqual(response.status_code, 204)

class SlipViewTests(ViewTest):
    pass
