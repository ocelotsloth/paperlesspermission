"""Test module for djo.py"""

from io import BytesIO
from django.test import TestCase
from paperlesspermission.models import Faculty
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
            importer = DJOImport(self.fs_classes,
                                 self.fs_faculty,
                                 self.fs_student,
                                 self.fs_parent,
                                 self.fs_enrollment)
            importer.import_faculty()
        except Exception:
            self.fail("DJOImport.import_faculty() did not successfully run.")

    def test_faculty_import_size(self):
        """Tests to see if the faculty_import function returns the correct
        number of Faculty objects."""
        importer = DJOImport(self.fs_classes,
                             self.fs_faculty,
                             self.fs_student,
                             self.fs_parent,
                             self.fs_enrollment)
        importer.import_faculty()

        all_faculty = Faculty.objects.all()
        size = len(all_faculty)

        self.assertEqual(size, 4, "")

    def test_faculty_contents_initial_hidden_value(self):
        """Tests to ensure that hidden value is always false on first
        import."""
        importer = DJOImport(self.fs_classes,
                             self.fs_faculty,
                             self.fs_student,
                             self.fs_parent,
                             self.fs_enrollment)
        importer.import_faculty()

        for faculty_obj in Faculty.objects.all():
            self.assertFalse(faculty_obj.hidden)

    def test_faculty_object_contents(self):
        """Tests to ensure that the actual faculty objects are correct."""
        importer = DJOImport(self.fs_classes,
                             self.fs_faculty,
                             self.fs_student,
                             self.fs_parent,
                             self.fs_enrollment)
        importer.import_faculty()

        faculty1001 = Faculty(person_id='1001',
                              first_name='John',
                              last_name='Doe',
                              email='jdoe@school.test',
                              preferred_name='Dr. Doe',
                              notify_cell=False,
                              hidden=False)
        self.assertEqual(Faculty.objects.get(person_id='1001'), faculty1001)

        faculty1002 = Faculty(person_id='1002',
                              first_name='Alice',
                              last_name='Hartman',
                              email='ahartman@school.test',
                              preferred_name='Ms. Hartman',
                              notify_cell=False,
                              hidden=False)
        self.assertEqual(Faculty.objects.get(person_id='1002'), faculty1002)

        faculty1003 = Faculty(person_id='1003',
                              first_name='Doug',
                              last_name='Ateman',
                              email='dateman@school.test',
                              preferred_name='Mr. Ateman',
                              notify_cell=False,
                              hidden=False)
        self.assertEqual(Faculty.objects.get(person_id='1003'), faculty1003)

        faculty1004 = Faculty(person_id='1004',
                              first_name='Andy',
                              last_name='Battern',
                              email='abattern@school.test',
                              preferred_name='Mr. Battern',
                              notify_cell=False,
                              hidden=False)
        self.assertEqual(Faculty.objects.get(person_id='1004'), faculty1004)

    def test_faculty_import_hidden(self):
        """Test that hidden is set on deleted faculty members."""

        # Initial import - test that faculty1004 exists
        importer = DJOImport(self.fs_classes,
                             self.fs_faculty,
                             self.fs_student,
                             self.fs_parent,
                             self.fs_enrollment)
        importer.import_faculty()

        faculty1004 = Faculty(person_id='1004',
                              first_name='Andy',
                              last_name='Battern',
                              email='abattern@school.test',
                              preferred_name='Mr. Battern',
                              notify_cell=False,
                              hidden=False)
        self.assertEqual(Faculty.objects.get(person_id='1004'), faculty1004)

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
        importer = DJOImport(self.fs_classes,
                             self.fs_faculty,
                             self.fs_student,
                             self.fs_parent,
                             self.fs_enrollment)
        importer.import_faculty()

        faculty1004 = Faculty(person_id='1004',
                              first_name='Andy',
                              last_name='Battern',
                              email='abattern@school.test',
                              preferred_name='Mr. Battern',
                              notify_cell=False,
                              hidden=True)
        self.assertEqual(Faculty.objects.get(person_id='1004'), faculty1004)
