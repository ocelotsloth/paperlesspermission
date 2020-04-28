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
from time import sleep

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User

import paperlesspermission.views as views
import paperlesspermission.models as models

class ViewTest(TestCase):
    """Defines functions and data available to all view test cases."""
    def setUp(self):
        """Set up data available to all view test cases."""
        # pylint: disable=invalid-name
        super(ViewTest, self).setUp()

        logging.disable(logging.CRITICAL)

        self.teacher_user = User.objects.create_user(
            'teacher',
            email='tuser@school.test',
            password='test'
        )

        self.admin_user = User.objects.create_user(
            'admin',
            email='auser@school.test',
            password='test'
        )
        self.admin_user.is_staff = True
        self.admin_user.save()

        self.super_user = User.objects.create_superuser(
            'super',
            email='suser@school.test',
            password='test'
        )

        student1 = models.Student(
            person_id='202300001',
            first_name='Test',
            last_name='Student',
            email='tstudent@school.test',
            cell_number='+17035555555',
            notify_cell=True,
            grade_level=models.Student.FRESHMAN
        )
        student1.save()

        student2 = models.Student(
            person_id='202200002',
            first_name='Alice',
            last_name='Hanson',
            email='ahanson@school.test',
            cell_number='+7035555555',
            notify_cell=True,
            grade_level=models.Student.FRESHMAN
        )
        student2.save()

        guardian1 = models.Guardian(
            person_id='2001',
            first_name='Guardian',
            last_name='Student',
            email='gstudent@email.test',
            cell_number='+17035555555',
            notify_cell=True,
        )
        guardian1.save()
        guardian1.students.add(student1)
        guardian1.save()

        guardian2 = models.Guardian(
            person_id='2002',
            first_name='Alice',
            last_name='Hanson',
            email='ahanson@email.test',
            cell_number='+17035555555',
            notify_cell=True
        )
        guardian2.save()
        guardian2.students.add(student2)
        guardian2.save()

        guardian3 = models.Guardian(
            person_id='2003',
            first_name='OtherGuardian',
            last_name='Student',
            email='ogstudent@email.test',
            cell_number='+17035555555',
            notify_cell=True,
        )
        guardian3.save()
        guardian3.students.add(student1)
        guardian3.save()

        teacher1 = models.Faculty(
            person_id='1000001',
            first_name='Teacher',
            last_name='User',
            email='tuser@school.test',
            cell_number='+17035555555',
            notify_cell=True,
            preferred_name='Mrs. Teacher'
        )
        teacher1.save()

        teacher2 = models.Faculty(
            person_id='1000002',
            first_name='Joey',
            last_name='West',
            email='jwest@school.test',
            cell_number='+17035555555',
            notify_cell=True,
            preferred_name='Mrs. West'
        )
        teacher2.save()

        course100 = models.Course(
            course_number='100',
            course_name='English 1'
        )
        course100.save()

        course105 = models.Course(
            course_number='105',
            course_name='Biology 2'
        )
        course105.save()

        section101 = models.Section(
            section_id='100101',
            course=course100,
            section_number='101',
            teacher=teacher1,
            school_year='2020',
            room='202',
            period='2nd'
        )
        section101.save()
        section101.students.add(student1)
        section101.save()

        section102 = models.Section(
            section_id='105102',
            course=course105,
            section_number='102',
            teacher=teacher2,
            school_year='2020',
            room='312',
            period='3rd'
        )
        section102.save()
        section102.students.add(student1)
        section102.students.add(student2)
        section102.save()

        trip = models.FieldTrip(
            id=1,
            name='Test Trip',
            group_name='Fishing Club',
            location='Bermuda Triangle',
            start_date='2020-03-01',
            dropoff_time='13:30',
            dropoff_location='Front Entrance',
            end_date='2020-04-01',
            pickup_time='13:30',
            pickup_location='Front Entrance',
            due_date='2020-02-15'
        )
        trip.save()
        trip.students.add(student1)
        trip.faculty.add(teacher1)
        trip.save()
        trip.generate_permission_slips()

    def tearDown(self):
        """Reset logging."""
        # pylint: disable=invalid-name
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
    """Test cases for djo import all view."""
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
    """Test cases for the slip view."""
    def test_slip_view_exists(self):
        """Ensure that the slip view exists."""
        self.assertTrue(hasattr(views, 'slip'))

    def test_slip_view_mapped_correctly(self):
        """Ensure that the URL mapping is correct."""
        self.assertEqual(
            reverse('permission slip', kwargs={'slip_id': '1'}),
            '/slip/1/'
        )

    def test_slip_view_get_student_slip(self):
        """Ensure that a student link returns the student submission."""

        # We're going to get student1's trip1 permission slip.
        student1 = models.Student.objects.get(person_id='202300001')
        trip = models.FieldTrip.objects.get(id=1)
        permission_slip = models.PermissionSlip.objects.get(
            field_trip=trip,
            student=student1
        )
        slip_link = models.PermissionSlipLink.objects.get(
            permission_slip=permission_slip,
            student=student1
        )
        slip_url_id = slip_link.link_id

        response = self.client.get(
            reverse('permission slip', kwargs={'slip_id': slip_url_id})
        )

        self.assertContains(
            response,
            'Student Submission',
            status_code=200,
            html=True,
        )

    def test_slip_view_submit_student_slip(self):
        """Ensure that submitting a student slip returns a filled
        out student portion."""

        # We're going to get student1's trip1 permission slip.
        student1 = models.Student.objects.get(person_id='202300001')
        trip = models.FieldTrip.objects.get(id=1)
        permission_slip = models.PermissionSlip.objects.get(
            field_trip=trip,
            student=student1
        )
        slip_link = models.PermissionSlipLink.objects.get(
            permission_slip=permission_slip,
            student=student1
        )
        slip_url_id = slip_link.link_id
        slip_url = reverse('permission slip', kwargs={'slip_id': slip_url_id})

        csrf_token = self.client.get(slip_url).context.get('csrf_token')
        response = self.client.post(
            slip_url,
            {
                'name': 'Test Student Submission',
                'electronic_consent': True,
                'csrf_token': csrf_token
            },
        )

        # Assert that the returned page shows the page submitted.
        self.assertContains(
            response,
            'Submitted',
            status_code=200,
            html=False,
        )

        # Assert that the student slip has actually been submitted.
        permission_slip.refresh_from_db()
        self.assertEqual(permission_slip.student_signature, 'Test Student Submission')
        self.assertTrue(permission_slip.student_signature_date)

    def test_slip_view_reject_invalid_student_submission_ec(self):
        """Student submissions with no electronic_consent must be rejected."""

        # We're going to get student1's trip1 permission slip.
        student1 = models.Student.objects.get(person_id='202300001')
        trip = models.FieldTrip.objects.get(id=1)
        permission_slip = models.PermissionSlip.objects.get(
            field_trip=trip,
            student=student1
        )
        slip_link = models.PermissionSlipLink.objects.get(
            permission_slip=permission_slip,
            student=student1
        )
        slip_url_id = slip_link.link_id
        slip_url = reverse('permission slip', kwargs={'slip_id': slip_url_id})

        initial_student_sig = permission_slip.student_signature
        initial_student_sig_date = permission_slip.student_signature_date

        csrf_token = self.client.get(slip_url).context.get('csrf_token')
        response = self.client.post(
            slip_url,
            {
                'name': 'Test Student Submission', # NOTE: This is not blank
                'electronic_consent': False,       # NOTE: This is blank
                'csrf_token': csrf_token
            },
        )

        # Assert that the returned page is an error.
        self.assertEqual(response.status_code, 400)

        # Assert that the permission_slip has not been updated.
        permission_slip.refresh_from_db()
        final_student_sig = permission_slip.student_signature
        final_student_sig_date = permission_slip.student_signature_date

        self.assertEqual(initial_student_sig, final_student_sig)
        self.assertEqual(initial_student_sig_date, final_student_sig_date)

    def test_slip_view_reject_invalid_student_submission_sig(self):
        """Student submissions with no name/signature must be rejected."""

        # We're going to get student1's trip1 permission slip.
        student1 = models.Student.objects.get(person_id='202300001')
        trip = models.FieldTrip.objects.get(id=1)
        permission_slip = models.PermissionSlip.objects.get(
            field_trip=trip,
            student=student1
        )
        slip_link = models.PermissionSlipLink.objects.get(
            permission_slip=permission_slip,
            student=student1
        )
        slip_url_id = slip_link.link_id
        slip_url = reverse('permission slip', kwargs={'slip_id': slip_url_id})

        initial_student_sig = permission_slip.student_signature
        initial_student_sig_date = permission_slip.student_signature_date

        csrf_token = self.client.get(slip_url).context.get('csrf_token')
        response = self.client.post(
            slip_url,
            {
                'name': '',                 # NOTE: This is blank
                'electronic_consent': True, # NOTE: This is not blank
                'csrf_token': csrf_token
            },
        )

        # Assert that the returned page is an error.
        self.assertEqual(response.status_code, 400)

        # Assert that the permission_slip has not been updated.
        permission_slip.refresh_from_db()
        final_student_sig = permission_slip.student_signature
        final_student_sig_date = permission_slip.student_signature_date

        self.assertEqual(initial_student_sig, final_student_sig)
        self.assertEqual(initial_student_sig_date, final_student_sig_date)

    def test_slip_view_already_submitted_student_slip(self):
        """Ensure that an already submitted student slip is rendered with
        submitted shown in the green badge."""

        # We're going to get student1's trip1 permission slip.
        student1 = models.Student.objects.get(person_id='202300001')
        trip = models.FieldTrip.objects.get(id=1)
        permission_slip = models.PermissionSlip.objects.get(
            field_trip=trip,
            student=student1
        )
        slip_link = models.PermissionSlipLink.objects.get(
            permission_slip=permission_slip,
            student=student1
        )
        slip_url_id = slip_link.link_id
        slip_url = reverse('permission slip', kwargs={'slip_id': slip_url_id})

        csrf_token = self.client.get(slip_url).context.get('csrf_token')
        self.client.post(
            slip_url,
            {
                'name': 'Test Student Submission',
                'electronic_consent': True,
                'csrf_token': csrf_token
            },
        )
        response = self.client.get(slip_url)

        # Assert that the returned page shows the page submitted.
        self.assertContains(
            response,
            'Submitted',
            status_code=200,
            html=False,
        )

    def test_slip_view_get_parent_slip(self):
        """Ensure that a parent link returns the parent submission."""

        # We're going to get guardian1's trip1 permission slip.
        student1 = models.Student.objects.get(person_id='202300001')
        guardian1 = models.Guardian.objects.get(person_id='2001')
        trip = models.FieldTrip.objects.get(id=1)
        permission_slip = models.PermissionSlip.objects.get(
            field_trip=trip,
            student=student1
        )
        slip_link = models.PermissionSlipLink.objects.get(
            permission_slip=permission_slip,
            guardian=guardian1
        )
        slip_url_id = slip_link.link_id

        response = self.client.get(
            reverse('permission slip', kwargs={'slip_id': slip_url_id})
        )

        self.assertContains(
            response,
            'Parent Submission',
            status_code=200,
            html=True,
        )

    def test_slip_view_POST_parent_slip(self):
        """Ensure that submitting a student slip returns a filled out guardian portion."""

        # We're going to get guardian1's trip1 permission slip.
        student1 = models.Student.objects.get(person_id='202300001')
        guardian1 = models.Guardian.objects.get(person_id='2001')
        trip = models.FieldTrip.objects.get(id=1)
        permission_slip = models.PermissionSlip.objects.get(
            field_trip=trip,
            student=student1
        )
        slip_link = models.PermissionSlipLink.objects.get(
            permission_slip=permission_slip,
            guardian=guardian1
        )
        slip_url_id = slip_link.link_id
        slip_url = reverse('permission slip', kwargs={'slip_id': slip_url_id})

        csrf_token = self.client.get(slip_url).context.get('csrf_token')
        response = self.client.post(
            slip_url,
            {
                'name': 'Test Parent Submission',
                'electronic_consent': True,
                'csrf_token': csrf_token
            },
        )

        # Assert that the returned page shows the page submitted.
        self.assertContains(
            response,
            'Submitted',
            status_code=200,
            html=False,
        )

        # Assert that the returned page shows the guardian name.
        self.assertContains(
            response,
            'Guardian Student',
            status_code=200,
            html=False
        )

        # Assert that the student slip has actually been submitted.
        permission_slip.refresh_from_db()
        self.assertEqual(permission_slip.guardian_signature, 'Test Parent Submission')
        self.assertTrue(permission_slip.guardian_signature_date)

    def test_slip_view_POST_second_parent_slip(self):
        """A parent submission from a different parent should update the slip."""

        # First get guardian1's slip and fill it out.
        student1 = models.Student.objects.get(person_id='202300001')
        guardian1 = models.Guardian.objects.get(person_id='2001')
        trip = models.FieldTrip.objects.get(id=1)
        permission_slip = models.PermissionSlip.objects.get(
            field_trip=trip,
            student=student1
        )
        slip_link = models.PermissionSlipLink.objects.get(
            permission_slip=permission_slip,
            guardian=guardian1
        )
        slip_url = reverse('permission slip', kwargs={'slip_id': slip_link.link_id})

        csrf_token = self.client.get(slip_url).context.get('csrf_token')
        response = self.client.post(
            slip_url,
            {
                'name': 'Test Guardian 1 Submission',
                'electronic_consent': True,
                'csrf_token': csrf_token
            },
        )

        permission_slip.refresh_from_db()
        initial_sig_date = permission_slip.guardian_signature_date

        # At this point the slip should be filled out by guardian1. Lets change
        # that to guardian3 and assert that the database gets that update.

        # First, let's wait a couple of seconds to ensure the time/date is
        # different, as we'll be testing to make sure the database changes that
        # stored/logged value.
        sleep(2)

        guardian3 = models.Guardian.objects.get(person_id='2003')
        slip_link = models.PermissionSlipLink.objects.get(
            permission_slip=permission_slip,
            guardian=guardian3
        )
        slip_url = reverse('permission slip', kwargs={'slip_id': slip_link.link_id})

        csrf_token = self.client.get(slip_url).context.get('csrf_token')
        signature = 'Test Guardian 3 Submission'
        response = self.client.post(
            slip_url,
            {
                'name': signature,
                'electronic_consent': True,
                'csrf_token': csrf_token
            },
        )

        # Assert response is correct

        self.assertContains(
            response,
            'OtherGuardian Student',
            status_code=200,
            html=False,
        )

        # Assert database was updated
        permission_slip.refresh_from_db()
        final_sig_date = permission_slip.guardian_signature_date
        self.assertEqual(permission_slip.guardian_signature, signature)
        self.assertNotEqual(initial_sig_date, final_sig_date)

    def test_slip_view_reject_invalid_parent_submission_ec(self):
        """Parent submissions with no electronic_consent must be rejected."""

        # We're going to get guardian1's trip1 permission slip.
        student1 = models.Student.objects.get(person_id='202300001')
        guardian1 = models.Guardian.objects.get(person_id='2001')
        trip = models.FieldTrip.objects.get(id=1)
        permission_slip = models.PermissionSlip.objects.get(
            field_trip=trip,
            student=student1
        )
        slip_link = models.PermissionSlipLink.objects.get(
            permission_slip=permission_slip,
            guardian=guardian1
        )
        slip_url_id = slip_link.link_id
        slip_url = reverse('permission slip', kwargs={'slip_id': slip_url_id})

        initial_student_sig = permission_slip.student_signature
        initial_student_sig_date = permission_slip.student_signature_date

        csrf_token = self.client.get(slip_url).context.get('csrf_token')
        response = self.client.post(
            slip_url,
            {
                'name': 'Test Parent Submission', # NOTE: This is not blank
                'electronic_consent': False,      # NOTE: This is blank
                'csrf_token': csrf_token
            },
        )

        # Assert that the returned page is an error.
        self.assertEqual(response.status_code, 400)

        # Assert that the permission_slip has not been updated.
        permission_slip.refresh_from_db()
        final_student_sig = permission_slip.student_signature
        final_student_sig_date = permission_slip.student_signature_date

        self.assertEqual(initial_student_sig, final_student_sig)
        self.assertEqual(initial_student_sig_date, final_student_sig_date)

    def test_slip_view_reject_invalid_parent_submission_sig(self):
        """Parent submissions with no name/signature must be rejected."""

        # We're going to get guardian1's trip1 permission slip.
        student1 = models.Student.objects.get(person_id='202300001')
        guardian1 = models.Guardian.objects.get(person_id='2001')
        trip = models.FieldTrip.objects.get(id=1)
        permission_slip = models.PermissionSlip.objects.get(
            field_trip=trip,
            student=student1
        )
        slip_link = models.PermissionSlipLink.objects.get(
            permission_slip=permission_slip,
            guardian=guardian1
        )
        slip_url_id = slip_link.link_id
        slip_url = reverse('permission slip', kwargs={'slip_id': slip_url_id})

        initial_student_sig = permission_slip.student_signature
        initial_student_sig_date = permission_slip.student_signature_date

        csrf_token = self.client.get(slip_url).context.get('csrf_token')
        response = self.client.post(
            slip_url,
            {
                'name': '',                 # NOTE: This is blank
                'electronic_consent': True, # NOTE: This is not blank
                'csrf_token': csrf_token
            },
        )

        # Assert that the returned page is an error.
        self.assertEqual(response.status_code, 400)

        # Assert that the permission_slip has not been updated.
        permission_slip.refresh_from_db()
        final_student_sig = permission_slip.student_signature
        final_student_sig_date = permission_slip.student_signature_date

        self.assertEqual(initial_student_sig, final_student_sig)
        self.assertEqual(initial_student_sig_date, final_student_sig_date)

    def test_completed_slip_shows_completed(self):
        """Completed slips should show a green badge in the upper right."""

        # We're going to get guardian1 and student1s' trip1 permission slip.
        student1 = models.Student.objects.get(person_id='202300001')
        guardian1 = models.Guardian.objects.get(person_id='2001')
        trip = models.FieldTrip.objects.get(id=1)
        permission_slip = models.PermissionSlip.objects.get(
            field_trip=trip,
            student=student1
        )
        slip_link = models.PermissionSlipLink.objects.get(
            permission_slip=permission_slip,
            guardian=guardian1
        )
        slip_url = reverse('permission slip', kwargs={'slip_id': slip_link.link_id})

        csrf_token = self.client.get(slip_url).context.get('csrf_token')
        self.client.post(
            slip_url,
            {
                'name': 'Guardian 1 Name',
                'electronic_consent': True,
                'csrf_token': csrf_token
            },
        )

        slip_link = models.PermissionSlipLink.objects.get(
            permission_slip=permission_slip,
            student=student1
        )
        slip_url = reverse('permission slip', kwargs={'slip_id': slip_link.link_id})

        csrf_token = self.client.get(slip_url).context.get('csrf_token')
        response = self.client.post(
            slip_url,
            {
                'name': 'Student 1 Name',
                'electronic_consent': True,
                'csrf_token': csrf_token
            },
        )

        self.assertContains(
            response,
            '<h3 class="float-right"><span class="badge badge-success">Complete</span></h3>',
            status_code=200,
            html=False,
        )

