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

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User

import paperlesspermission.views as views

class ViewTest(TestCase):
    def setUp(self):
        self.teacher_user = User.objects.create_user('teacher',
                email='tuser@school.test', password='test')

        self.admin_user = User.objects.create_user('admin',
                email='auser@school.test', password='test')
        self.admin_user.is_staff = True
        self.admin_user.save()

        self.super_user = User.objects.create_superuser('super',
                email='suser@school.test', password='test')

class IndexViewTests(ViewTest):
    """Test cases for the index view"""
    def test_index_view_exists(self):
        """Tests to ensure the index view exists"""
        self.assertTrue(hasattr(views, 'index'))

    def test_index_view_mapped_correctly(self):
        """Ensure that the index view is mapped to '/'"""
        self.assertEqual(reverse('index'), '/')

    def index_view_redirect(self, redirect_location, user=None):
        """Ensure an authenticated user is redirected to /trip

        Run this function in other test cases. This allows for testing
        multiple types of users."""
        if user is not None:
            self.client.force_login(user)
        response = self.client.get('/')

        # Check that status code is a redirect
        self.assertEqual(response.status_code, 302)

        # Check that response class is HttpResponseRedirect
        self.assertEqual(response.__class__.__name__, 'HttpResponseRedirect')

        # Check that the redirect URL is to '/trip'
        self.assertEqual(response.url, redirect_location)

    def test_index_view_not_authenticated_redirect(self):
        """Ensure an unauthenticated user is redirected to /login"""
        self.index_view_redirect('/login')

    def test_index_view_authenticated_redirect_teacher(self):
        """Test index redirect for teacher user"""
        self.index_view_redirect('/trip', self.teacher_user)

    def test_index_view_authenticated_redirect_admin(self):
        """Test index redirect for admin user"""
        self.index_view_redirect('/trip', self.admin_user)

    def test_index_view_authenticated_redirect_superuser(self):
        """Test index redirect for super user"""
        self.index_view_redirect('/trip', self.super_user)
