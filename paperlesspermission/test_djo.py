"""Test module for djo.py"""

from io import BytesIO
from django.test import TestCase
from paperlesspermission.models import Faculty, Course, Section, Student, Guardian
from paperlesspermission.djo import DJOImport


class DJOImportTestCase(TestCase):
    """Abstract class to test the DJOImport class.

    To actually test a method of this class, subclass DJOImportTestCase. It
    will inherit the setUp and tearDown methods.
    """

    def setUp(self):
        self.fs_faculty = BytesIO(
            b'RECORDID\tFIRST_NAME\tLAST_NAME\tEMAIL_ADDR\tPREFERREDNAME\n'
            + b'1001\tJohn\tDoe\tjdoe@school.test\tDr. Doe\n'
            + b'1002\tAlice\tHartman\tahartman@school.test\tMs. Hartman\n'
            + b'1003\tDoug\tAteman\tdateman@school.test\tMr. Ateman\n'
            + b'1004\tAndy\tBattern\tabattern@school.test\tMr. Battern\n'
        )

        self.fs_classes = BytesIO(
            b'RECORDID\tCOURSE_NUMBER\tSECTION_NUMBER\tTERMID\tSCHOOLYEAR\tTEACHER\tROOM\tCOURSE_NAME\tEXPRESSION\tCOTEACHER\n'
            + b'15110\t0001\t1\t1901\t2019-2020\t1001\t124\tSpelling\t7(A1-B1,A3)\t\n'
            + b'15121\t0002\t1\t1901\tSemester 1\t1002\t231\tEnglish 1\t3(A1-B1,A3)\t\n'
            + b'15122\t0002\t2\t1901\tSemester 1\t1003\t233\tEnglish 1\t3(A1-B1,A3)\t\n'
            + b'15131\t0003\t1\t1901\t2019-2020\t1004\tGym\tPE\t3(A1-B1,A3)\t1001\n'
        )

        self.fs_student = BytesIO(
            b'RECORDID\tGRADE_LEVEL\tFIRST_NAME\tLAST_NAME\tEMAIL\n'
            + b'1\t10\tAbe\tTesco\t20atesco1@school.test\n'
            + b'2\t10\tTessa\tAdelede\t20tadelede2@school.test\n'
            + b'3\t11\tMatt\tTesco\t19mtesco3@school.test\n'
            + b'4\t11\tAdam\tHun\t19ahun4@school.test\n'
            + b'5\t12\tMary\tWalters\t18mwalters5@school.test\n'
            + b'6\t12\tTaylor\tJohnston\t18tjohnston6@school.test\n'
        )

        self.fs_parent = BytesIO(
            b'STUDENT_NUMBER\tCNT1_ID\tCNT1_FNAME\tCNT1_LNAME\tCNT1_REL\tCNT1_CPHONE\tCNT1_EMAIL\tCNT2_ID\tCNT2_FNAME\tCNT2_LNAME\tCNT2_REL\tCNT2_CPHONE\tCNT2_EMAIL\tCNT3_ID\tCNT3_FNAME\tCNT3_LNAME\tCNT3_REL\tCNT3_CPHONE\tCNT3_EMAIL\n'
            + b'1\t91\tJupiter\tTesco\tMother\t703-555-1111\tjtesco@gmail.test\t92\tAdam\tTesco\tFather\t703-555-2222\tate@gmail.test\t\t\t\t\t\t\n'
            + b'2\t93\tGarv\tCallis\tFather\t701-555-3333\tgcallis0@email.test\t94\tKarla\tCallis\tMother\t\tkcallis@gmail.test\t95\tDukey\tMacConal\tGrandparent\t201-555-6666\tdmacconnal5@sun.test\n'
            + b'3\t91\tJupiter\tTesco\tMother\t703-555-1111\tjtesco@gmail.test\t92\tAdam\tTesco\tFather\t703-555-2222\tate@gmail.test\t\t\t\t\t\t\n'
            + b'4\t96\tAlford\tLordon\tFather\t843-444-3222\talorton@gmail.test\t\t\t\t\t\t\t\t\t\t\t\t\n'
            + b'5\t97\tBax\tKimm\tFather\t433-555-5555\tbkimm@gmail.test\t\t\t\t\t\t\t\t\t\t\t\t\n'
            + b'6\t98\tLulu\tMcMennum\tMother\t323-555-2222\tlmcmennum@gmail.test\t\t\t\t\t\t\t\t\t\t\t\t\n'
        )

        self.fs_enrollment = BytesIO(
            b'STUDENT_NUMBER\tSECTIONID\n'
            + b'1\t15110\n'
            + b'1\t15121\n'
            + b'1\t15131\n'
            + b'2\t15110\n'
            + b'2\t15122\n'
            + b'3\t15110\n'
            + b'4\t15110\n'
            + b'4\t15122\n'
            + b'4\t15131\n'
            + b'5\t15131\n'
            + b'5\t15110\n'
            + b'6\t15131\n'
        )

        self.importer = DJOImport(self.fs_classes,
                                  self.fs_faculty,
                                  self.fs_student,
                                  self.fs_parent,
                                  self.fs_enrollment)

    def tearDown(self):
        self.fs_faculty.close()
        self.fs_classes.close()
        self.fs_student.close()
        self.fs_parent.close()
        self.fs_enrollment.close()


class ImportFacultyTests(DJOImportTestCase):
    """Tests the import_faculty() method"""

    def test_import_faculty(self):
        """Tests to ensure that import_faculty does not throw an exception."""
        try:
            self.importer.import_faculty()
        except Exception:
            self.fail("DJOImport.import_faculty() did not successfully run.")

    def test_faculty_import_size(self):
        """Tests to see if the faculty_import function returns the correct
        number of Faculty objects."""
        self.importer.import_faculty()

        self.assertEqual(Faculty.objects.count(), 4)

    def test_faculty_contents_initial_hidden_value(self):
        """Tests to ensure that hidden value is always false on first
        import."""
        self.importer.import_faculty()

        for faculty_obj in Faculty.objects.all():
            self.assertFalse(faculty_obj.hidden)

    def test_faculty_object_contents(self):
        """Tests to ensure that the actual faculty objects are correct."""
        self.importer.import_faculty()

        value_faculty = Faculty.objects.get(person_id='1001')
        self.assertEqual(value_faculty.first_name, 'John')
        self.assertEqual(value_faculty.last_name, 'Doe')
        self.assertEqual(value_faculty.email, 'jdoe@school.test')
        self.assertEqual(value_faculty.preferred_name, 'Dr. Doe')
        self.assertEqual(value_faculty.notify_cell, False)
        self.assertEqual(value_faculty.hidden, False)

        value_faculty = Faculty.objects.get(person_id='1002')
        self.assertEqual(value_faculty.first_name, 'Alice')
        self.assertEqual(value_faculty.last_name, 'Hartman')
        self.assertEqual(value_faculty.email, 'ahartman@school.test')
        self.assertEqual(value_faculty.preferred_name, 'Ms. Hartman')
        self.assertEqual(value_faculty.notify_cell, False)
        self.assertEqual(value_faculty.hidden, False)

        value_faculty = Faculty.objects.get(person_id='1003')
        self.assertEqual(value_faculty.first_name, 'Doug')
        self.assertEqual(value_faculty.last_name, 'Ateman')
        self.assertEqual(value_faculty.email, 'dateman@school.test')
        self.assertEqual(value_faculty.preferred_name, 'Mr. Ateman')
        self.assertEqual(value_faculty.notify_cell, False)
        self.assertEqual(value_faculty.hidden, False)

        value_faculty = Faculty.objects.get(person_id='1004')
        self.assertEqual(value_faculty.first_name, 'Andy')
        self.assertEqual(value_faculty.last_name, 'Battern')
        self.assertEqual(value_faculty.email, 'abattern@school.test')
        self.assertEqual(value_faculty.preferred_name, 'Mr. Battern')
        self.assertEqual(value_faculty.notify_cell, False)
        self.assertEqual(value_faculty.hidden, False)

    def test_faculty_import_hidden(self):
        """Test that hidden is set on deleted faculty members."""

        # Initial import - test that faculty1004 exists
        self.importer.import_faculty()
        self.assertFalse(Faculty.objects.get(person_id='1004').hidden)

        # Remove faculty 1004
        self.fs_faculty = BytesIO(
            b'RECORDID\tFIRST_NAME\tLAST_NAME\tEMAIL_ADDR\tPREFERREDNAME\n'
            + b'1001\tJohn\tDoe\tjdoe@school.test\tDr. Doe\n'
            + b'1002\tAlice\tHartman\tahartman@school.test\tMs. Hartman\n'
            + b'1003\tDoug\tAteman\tdateman@school.test\tMr. Ateman\n'
            # + b'1004\tAndy\tBattern\tabattern@school.test\tMr. Battern\n'
        )

        # Second import - test that faculty1004 still exists and has hidden
        # flag set
        self.importer = DJOImport(self.fs_classes,
                                  self.fs_faculty,
                                  self.fs_student,
                                  self.fs_parent,
                                  self.fs_enrollment)
        self.importer.import_faculty()
        self.assertTrue(Faculty.objects.get(person_id='1004').hidden)

        # Add faculty 1004 back
        self.fs_faculty = BytesIO(
            b'RECORDID\tFIRST_NAME\tLAST_NAME\tEMAIL_ADDR\tPREFERREDNAME\n'
            + b'1001\tJohn\tDoe\tjdoe@school.test\tDr. Doe\n'
            + b'1002\tAlice\tHartman\tahartman@school.test\tMs. Hartman\n'
            + b'1003\tDoug\tAteman\tdateman@school.test\tMr. Ateman\n'
            + b'1004\tAndy\tBattern\tabattern@school.test\tMr. Battern\n'
        )
        # Third import - test that faculty1004 has its hidden flag removed when
        # added back into the data set.
        self.importer = DJOImport(self.fs_classes,
                                  self.fs_faculty,
                                  self.fs_student,
                                  self.fs_parent,
                                  self.fs_enrollment)
        self.importer.import_faculty()
        self.assertFalse(Faculty.objects.get(person_id='1004').hidden)


class ImportClassesTest(DJOImportTestCase):
    """Test the import_classes() method."""

    def test_import_classes(self):
        """Tests to see if import_classes runs without exception."""
        try:
            # Faculty must be imported first
            self.importer.import_faculty()
            self.importer.import_classes()
        except Exception:
            self.fail("DJOImport.import_classes() did not successfully run.")

    def test_import_classes_courses_size(self):
        """Tests to see if the import_classes function returns the correct
        number of course objects."""
        self.importer.import_faculty()
        self.importer.import_classes()

        self.assertEqual(Course.objects.count(), 3)

    def test_import_classes_courses_initial_hidden_value(self):
        """Tests to see if the import_classes functions initially sets the hiddden
        attribute on the courses objects to False."""
        self.importer.import_faculty()
        self.importer.import_classes()

        for course_obj in Course.objects.all():
            self.assertFalse(course_obj.hidden)

    def test_import_classes_courses_deleted_hidden_value(self):
        """Tests to see if the import_classes functions initially sets the hiddden
        attribute on the courses objects to False."""
        self.importer.import_faculty()
        self.importer.import_classes()

        # Delete the spelling course
        self.importer.fs_classes = BytesIO(
            b'RECORDID\tCOURSE_NUMBER\tSECTION_NUMBER\tTERMID\tSCHOOLYEAR\tTEACHER\tROOM\tCOURSE_NAME\tEXPRESSION\tCOTEACHER\n'
            # + b'15110\t0001\t1\t1901\t2019-2020\t1001\t124\tSpelling\t7(A1-B1,A3)\t\n'
            + b'15121\t0002\t1\t1901\tSemester 1\t1002\t231\tEnglish 1\t3(A1-B1,A3)\t\n'
            + b'15122\t0002\t2\t1901\tSemester 1\t1003\t233\tEnglish 1\t3(A1-B1,A3)\t\n'
            + b'15131\t0003\t1\t1901\t2019-2020\t1004\tGym\tPE\t3(A1-B1,A3)\t1001\n'
        )
        self.importer.import_faculty()
        self.importer.import_classes()

        self.assertTrue(Course.objects.get(course_number='0001').hidden)

    def test_import_classes_sections_size(self):
        """Tests to see if the import_classes function returns the correct
        number of section objects."""
        self.importer.import_faculty()
        self.importer.import_classes()

        self.assertEqual(Section.objects.count(), 4)

    def test_import_classes_sections_initial_hidden_value(self):
        """Tests to see if the import_classes functions initially sets the hiddden
        attribute on the sections objects to False."""
        self.importer.import_faculty()
        self.importer.import_classes()

        for section_obj in Section.objects.all():
            self.assertFalse(section_obj.hidden)

    def test_import_classes_sections_deleted_hidden_value(self):
        """Tests to see if the import_classes functions initially sets the hiddden
        attribute on the sections objects to False."""
        self.importer.import_faculty()
        self.importer.import_classes()

        # Delete section 2 of English 1
        self.importer.fs_classes = BytesIO(
            b'RECORDID\tCOURSE_NUMBER\tSECTION_NUMBER\tTERMID\tSCHOOLYEAR\tTEACHER\tROOM\tCOURSE_NAME\tEXPRESSION\tCOTEACHER\n'
            + b'15110\t0001\t1\t1901\t2019-2020\t1001\t124\tSpelling\t7(A1-B1,A3)\t\n'
            + b'15121\t0002\t1\t1901\tSemester 1\t1002\t231\tEnglish 1\t3(A1-B1,A3)\t\n'
            # + b'15122\t0002\t2\t1901\tSemester 1\t1003\t233\tEnglish 1\t3(A1-B1,A3)\t\n'
            + b'15131\t0003\t1\t1901\t2019-2020\t1004\tGym\tPE\t3(A1-B1,A3)\t1001\n'
        )
        self.importer.import_faculty()
        self.importer.import_classes()

        self.assertTrue(Section.objects.get(section_id='15122').hidden)


class ImportStudentsTest(DJOImportTestCase):
    def test_import_students(self):
        """Test that the import function actually runs."""
        try:
            self.importer.import_faculty()
            self.importer.import_classes()
            self.importer.import_students()
        except Exception:
            self.fail("DJOImport.import_classes() did not successfully run.")

    def test_import_students_size(self):
        """Tests to see if the import_students function returns the correct
        number of student objects."""
        self.importer.import_faculty()
        self.importer.import_classes()
        self.importer.import_students()

        self.assertEqual(Student.objects.count(), 6)

    def test_import_students_initial_hidden_value(self):
        """Tests to see if the import_classes functions initially sets the hiddden
        attribute on the sections objects to False."""
        self.importer.import_faculty()
        self.importer.import_classes()
        self.importer.import_students()

        for student_obj in Student.objects.all():
            self.assertFalse(student_obj.hidden)

    def test_import_students_deleted_hidden_value(self):
        """Tests to see if the import_classes functions initially sets the hiddden
        attribute on the sections objects to False."""
        self.importer.import_faculty()
        self.importer.import_classes()
        self.importer.import_students()

        # First test: ensure that hidden flag is set to false
        self.assertFalse(Student.objects.get(person_id='4').hidden)

        # Delete student 4
        self.importer.fs_student = BytesIO(
            b'RECORDID\tGRADE_LEVEL\tFIRST_NAME\tLAST_NAME\tEMAIL\n'
            + b'1\t10\tAbe\tTesco\t20atesco1@school.test\n'
            + b'2\t10\tTessa\tAdelede\t20tadelede2@school.test\n'
            + b'3\t11\tMatt\tTesco\t19mtesco3@school.test\n'
            # + b'4\t11\tAdam\tHun\t19ahun4@school.test\n'
            + b'5\t12\tMary\tWalters\t18mwalters5@school.test\n'
            + b'6\t12\tTaylor\tJohnston\t18tjohnston6@school.test\n'
        )
        self.importer.import_faculty()
        self.importer.import_classes()
        self.importer.import_students()

        # Second test: ensure that hidden flag is set to true
        self.assertTrue(Student.objects.get(person_id='4').hidden)

        # Add student 4 back
        self.importer.fs_student = BytesIO(
            b'RECORDID\tGRADE_LEVEL\tFIRST_NAME\tLAST_NAME\tEMAIL\n'
            + b'1\t10\tAbe\tTesco\t20atesco1@school.test\n'
            + b'2\t10\tTessa\tAdelede\t20tadelede2@school.test\n'
            + b'3\t11\tMatt\tTesco\t19mtesco3@school.test\n'
            + b'4\t11\tAdam\tHun\t19ahun4@school.test\n'
            + b'5\t12\tMary\tWalters\t18mwalters5@school.test\n'
            + b'6\t12\tTaylor\tJohnston\t18tjohnston6@school.test\n'
        )
        self.importer.import_faculty()
        self.importer.import_classes()
        self.importer.import_students()

        # Third test: ensure that hidden flag is set to false again
        self.assertFalse(Student.objects.get(person_id='4').hidden)


class ImportGuardiansTest(DJOImportTestCase):
    def test_import_guardians(self):
        """Test that the import function actually runs."""
        try:
            self.importer.import_faculty()
            self.importer.import_classes()
            self.importer.import_students()
            self.importer.import_guardians()
        except Exception:
            self.fail("DJOImport.import_guardians() did not successfully run.")

    def test_import_students_size(self):
        """Tests to see if the import_students function returns the correct
        number of student objects."""
        self.importer.import_faculty()
        self.importer.import_classes()
        self.importer.import_students()
        self.importer.import_guardians()

        self.assertEqual(Guardian.objects.count(), 8)

    def test_import_students_initial_hidden_value(self):
        """Tests to see if the import_classes functions initially sets the hiddden
        attribute on the sections objects to False."""
        self.importer.import_faculty()
        self.importer.import_classes()
        self.importer.import_students()
        self.importer.import_guardians()

        for guardian_obj in Guardian.objects.all():
            self.assertFalse(guardian_obj.hidden)

    def test_import_students_deleted_hidden_value(self):
        """Tests to see if the import_classes functions initially sets the hiddden
        attribute on the sections objects to False."""
        self.importer.import_faculty()
        self.importer.import_classes()
        self.importer.import_students()
        self.importer.import_guardians()

        # First test: ensure that parent's hidden value set to false
        self.assertFalse(Guardian.objects.get(person_id='98').hidden)

        # Delete parent 98 (student 6's sole parent)
        self.importer.fs_parent = BytesIO(
            b'STUDENT_NUMBER\tCNT1_ID\tCNT1_FNAME\tCNT1_LNAME\tCNT1_REL\tCNT1_CPHONE\tCNT1_EMAIL\tCNT2_ID\tCNT2_FNAME\tCNT2_LNAME\tCNT2_REL\tCNT2_CPHONE\tCNT2_EMAIL\tCNT3_ID\tCNT3_FNAME\tCNT3_LNAME\tCNT3_REL\tCNT3_CPHONE\tCNT3_EMAIL\n'
            + b'1\t91\tJupiter\tTesco\tMother\t703-555-1111\tjtesco@gmail.test\t92\tAdam\tTesco\tFather\t703-555-2222\tate@gmail.test\t\t\t\t\t\t\n'
            + b'2\t93\tGarv\tCallis\tFather\t701-555-3333\tgcallis0@email.test\t94\tKarla\tCallis\tMother\t\tkcallis@gmail.test\t95\tDukey\tMacConal\tGrandparent\t201-555-6666\tdmacconnal5@sun.test\n'
            + b'3\t91\tJupiter\tTesco\tMother\t703-555-1111\tjtesco@gmail.test\t92\tAdam\tTesco\tFather\t703-555-2222\tate@gmail.test\t\t\t\t\t\t\n'
            + b'4\t96\tAlford\tLordon\tFather\t843-444-3222\talorton@gmail.test\t\t\t\t\t\t\t\t\t\t\t\t\n'
            + b'5\t97\tBax\tKimm\tFather\t433-555-5555\tbkimm@gmail.test\t\t\t\t\t\t\t\t\t\t\t\t\n'
            # + b'6\t98\tLulu\tMcMennum\tMother\t323-555-2222\tlmcmennum@gmail.test\t\t\t\t\t\t\t\t\t\t\t\t\n'
        )
        self.importer.import_faculty()
        self.importer.import_classes()
        self.importer.import_students()
        self.importer.import_guardians()

        # Second test: ensure hidden flag set on deleted parent
        self.assertTrue(Guardian.objects.get(person_id='98').hidden)

        # Add parent 98 (student 6's sole parent) back into the database
        self.importer.fs_parent = BytesIO(
            b'STUDENT_NUMBER\tCNT1_ID\tCNT1_FNAME\tCNT1_LNAME\tCNT1_REL\tCNT1_CPHONE\tCNT1_EMAIL\tCNT2_ID\tCNT2_FNAME\tCNT2_LNAME\tCNT2_REL\tCNT2_CPHONE\tCNT2_EMAIL\tCNT3_ID\tCNT3_FNAME\tCNT3_LNAME\tCNT3_REL\tCNT3_CPHONE\tCNT3_EMAIL\n'
            + b'1\t91\tJupiter\tTesco\tMother\t703-555-1111\tjtesco@gmail.test\t92\tAdam\tTesco\tFather\t703-555-2222\tate@gmail.test\t\t\t\t\t\t\n'
            + b'2\t93\tGarv\tCallis\tFather\t701-555-3333\tgcallis0@email.test\t94\tKarla\tCallis\tMother\t\tkcallis@gmail.test\t95\tDukey\tMacConal\tGrandparent\t201-555-6666\tdmacconnal5@sun.test\n'
            + b'3\t91\tJupiter\tTesco\tMother\t703-555-1111\tjtesco@gmail.test\t92\tAdam\tTesco\tFather\t703-555-2222\tate@gmail.test\t\t\t\t\t\t\n'
            + b'4\t96\tAlford\tLordon\tFather\t843-444-3222\talorton@gmail.test\t\t\t\t\t\t\t\t\t\t\t\t\n'
            + b'5\t97\tBax\tKimm\tFather\t433-555-5555\tbkimm@gmail.test\t\t\t\t\t\t\t\t\t\t\t\t\n'
            + b'6\t98\tLulu\tMcMennum\tMother\t323-555-2222\tlmcmennum@gmail.test\t\t\t\t\t\t\t\t\t\t\t\t\n'
        )
        self.importer.import_faculty()
        self.importer.import_classes()
        self.importer.import_students()
        self.importer.import_guardians()

        # Third test: ensure hidden flag removed on parent
        self.assertFalse(Guardian.objects.get(person_id='98').hidden)


class ImportEnrollmentTest(DJOImportTestCase):
    def test_import_enrollment(self):
        """Test that the import function actually runs."""
        try:
            self.importer.import_faculty()
            self.importer.import_classes()
            self.importer.import_students()
            self.importer.import_guardians()
            self.importer.import_enrollment()
        except Exception:
            self.fail("DJOImport.import_enrollment() did not successfully run.")

    def test_import_enrollment_size(self):
        """Tests to see if the import_enrollment function returns the correct
        number of enrollment objects."""
        self.importer.import_faculty()
        self.importer.import_classes()
        self.importer.import_students()
        self.importer.import_guardians()
        self.importer.import_enrollment()

        self.assertEqual(Section.students.through.objects.count(), 12)

    def test_import_enrollment_deleted_value(self):
        """Tests to see if the import_enrollment function deletes enrollment that
        is removed from upstream."""
        self.importer.import_faculty()
        self.importer.import_classes()
        self.importer.import_students()
        self.importer.import_guardians()
        self.importer.import_enrollment()

        # Ensure it exists before being deleted
        self.assertTrue(Section.objects.get(section_id='15122')
                                       .students.filter(person_id='2')
                                       .exists())

        # Delete student 2's enrollment with section 15122
        self.importer.fs_enrollment = BytesIO(
            b'STUDENT_NUMBER\tSECTIONID\n'
            + b'1\t15110\n'
            + b'1\t15121\n'
            + b'1\t15131\n'
            + b'2\t15110\n'
            # + b'2\t15122\n'
            + b'3\t15110\n'
            + b'4\t15110\n'
            + b'4\t15122\n'
            + b'4\t15131\n'
            + b'5\t15131\n'
            + b'5\t15110\n'
            + b'6\t15131\n'
        )
        self.importer.import_faculty()
        self.importer.import_classes()
        self.importer.import_students()
        self.importer.import_guardians()
        self.importer.import_enrollment()

        self.assertFalse(Section.objects.get(section_id='15122')
                                        .students.filter(person_id='2')
                                        .exists())


class ImportAllTests(DJOImportTestCase):
    def test_import_all(self):
        """Ensure import_all() actually runs."""
        try:
            self.importer.import_all()
        except Exception:
            self.fail("DJOImport.import_all() did not successfully run.")

    def test_with_obj_use(self):
        """Ensure the __enter__/__exit__ functions work."""
        try:
            with DJOImport(self.fs_classes,
                           self.fs_faculty,
                           self.fs_student,
                           self.fs_parent,
                           self.fs_enrollment) as importer:
                importer.import_all()
        except Exception:
            self.fail("With syntax did not successfully run.")
