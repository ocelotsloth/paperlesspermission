"""Test module for models.py"""

from django.test import TestCase
from paperlesspermission.models import Person, Faculty


class PersonTests(TestCase):
    def test_eq(self):
        """Verify that the equality function works. """
        test = Person(person_id='1',
                      first_name='a',
                      last_name='b',
                      email='a@a.test',
                      cell_number='757-555-5555',
                      notify_cell=False,
                      hidden=False)

        # Test on an identical version.
        value_equal = Person(person_id='1',
                             first_name='a',
                             last_name='b',
                             email='a@a.test',
                             cell_number='757-555-5555',
                             notify_cell=False,
                             hidden=False)
        self.assertEqual(test, value_equal)

        # Test by only changing person_id and checking for inequality.
        value_not_equal_person_id = Person(person_id='2',
                                           first_name='a',
                                           last_name='b',
                                           email='a@a.test',
                                           cell_number='757-555-5555',
                                           notify_cell=False,
                                           hidden=False)
        self.assertNotEqual(test, value_not_equal_person_id)

        # Test by only changing first_name and checking for inequality.
        value_not_equal_first_name = Person(person_id='1',
                                            first_name='z',
                                            last_name='b',
                                            email='a@a.test',
                                            cell_number='757-555-5555',
                                            notify_cell=False,
                                            hidden=False)
        self.assertNotEqual(test, value_not_equal_first_name)

        # Test by only changing last_name and checking for inequality.
        value_not_equal_last_name = Person(person_id='1',
                                           first_name='a',
                                           last_name='z',
                                           email='a@a.test',
                                           cell_number='757-555-5555',
                                           notify_cell=False,
                                           hidden=False)
        self.assertNotEqual(test, value_not_equal_last_name)

        # Test by only changing email and checking for inequality.
        value_not_equal_email = Person(person_id='1',
                                       first_name='a',
                                       last_name='b',
                                       email='z@z.test',
                                       cell_number='757-555-5555',
                                       notify_cell=False,
                                       hidden=False)
        self.assertNotEqual(test, value_not_equal_email)

        # Test by only changing cell_number and checking for inequality.
        value_not_equal_cell_number = Person(person_id='1',
                                             first_name='a',
                                             last_name='b',
                                             email='a@a.test',
                                             cell_number='555-555-5555',
                                             notify_cell=False,
                                             hidden=False)
        self.assertNotEqual(test, value_not_equal_cell_number)

        # Test by only changing notify_cell and checking for inequality.
        value_not_equal_notify_cell = Person(person_id='1',
                                             first_name='a',
                                             last_name='b',
                                             email='a@a.test',
                                             cell_number='757-555-5555',
                                             notify_cell=True,
                                             hidden=False)
        self.assertNotEqual(test, value_not_equal_notify_cell)

        # Test by only changing hidden and checking for inequality.
        value_not_equal_hidden = Person(person_id='1',
                                        first_name='a',
                                        last_name='b',
                                        email='a@a.test',
                                        cell_number='757-555-5555',
                                        notify_cell=False,
                                        hidden=True)
        self.assertNotEqual(test, value_not_equal_hidden)


class FacultyTests(TestCase):
    def test_eq(self):
        """Verify that the equality function works."""
        test = Faculty(person_id='1',
                       first_name='a',
                       last_name='b',
                       email='a@a.test',
                       cell_number='757-555-5555',
                       notify_cell=False,
                       hidden=False,
                       preferred_name='a b')

        # Test against an identical Faculty object.
        value_equal = Faculty(person_id='1',
                              first_name='a',
                              last_name='b',
                              email='a@a.test',
                              cell_number='757-555-5555',
                              notify_cell=False,
                              hidden=False,
                              preferred_name='a b')
        self.assertEqual(test, value_equal)

        # We only need to test differences unique to this class. The Person
        # class super __eq__ handles the rest.
        value_not_equal_preferred_name = Faculty(person_id='1',
                                                 first_name='a',
                                                 last_name='b',
                                                 email='a@a.test',
                                                 cell_number='757-555-5555',
                                                 notify_cell=False,
                                                 hidden=False,
                                                 preferred_name='f z')
        self.assertNotEqual(test, value_not_equal_preferred_name)
