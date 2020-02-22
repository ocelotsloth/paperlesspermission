"""Test module for modules.py"""

from django.test import TestCase
from paperlesspermission.models import Person, Faculty


class PersonTests(TestCase):
    def test_eq(self):
        """Verify that the equality function works."""
        test = Person(person_id='1', first_name='a', last_name='b', email='a@a.test',
                      cell_number='757-555-5555', notify_cell=False, hidden=False)
        value_equal = Person(person_id='1', first_name='a', last_name='b', email='a@a.test',
                             cell_number='757-555-5555', notify_cell=False, hidden=False)
        value_not_equal_person_id = Person(person_id='2', first_name='a', last_name='b',
                                           email='a@a.test', cell_number='757-555-5555', notify_cell=False, hidden=False)
        value_not_equal_first_name = Person(person_id='1', first_name='z', last_name='b',
                                            email='a@a.test', cell_number='757-555-5555', notify_cell=False, hidden=False)
        value_not_equal_last_name = Person(person_id='1', first_name='a', last_name='z',
                                           email='a@a.test', cell_number='757-555-5555', notify_cell=False, hidden=False)
        value_not_equal_email = Person(person_id='1', first_name='a', last_name='b',
                                       email='z@z.test', cell_number='757-555-5555', notify_cell=False, hidden=False)
        value_not_equal_cell_number = Person(person_id='1', first_name='a', last_name='b',
                                             email='a@a.test', cell_number='555-555-5555', notify_cell=False, hidden=False)
        value_not_equal_notify_cell = Person(person_id='1', first_name='a', last_name='b',
                                             email='a@a.test', cell_number='757-555-5555', notify_cell=True, hidden=False)
        value_not_equal_hidden = Person(person_id='1', first_name='a', last_name='b',
                                        email='a@a.test', cell_number='757-555-5555', notify_cell=False, hidden=True)
        self.assertEqual(test, value_equal)
        self.assertNotEqual(test, value_not_equal_person_id)
        self.assertNotEqual(test, value_not_equal_first_name)
        self.assertNotEqual(test, value_not_equal_last_name)
        self.assertNotEqual(test, value_not_equal_email)
        self.assertNotEqual(test, value_not_equal_cell_number)
        self.assertNotEqual(test, value_not_equal_notify_cell)
        self.assertNotEqual(test, value_not_equal_hidden)


class FacultyTests(TestCase):
    def test_eq(self):
        """Verify that the equality function works."""
        test = Faculty(person_id='1', first_name='a', last_name='b', email='a@a.test',
                       cell_number='757-555-5555', notify_cell=False, hidden=False, preferred_name='a b')
        value_equal = Faculty(person_id='1', first_name='a', last_name='b', email='a@a.test',
                              cell_number='757-555-5555', notify_cell=False, hidden=False, preferred_name='a b')
        value_not_equal_preferred_name = Faculty(person_id='1', first_name='a', last_name='b', email='a@a.test',
                                                 cell_number='757-555-5555', notify_cell=False, hidden=False, preferred_name='f z')

        self.assertEqual(test, value_equal)
        self.assertNotEqual(test, value_not_equal_preferred_name)
