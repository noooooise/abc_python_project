
import unittest
from junit_xml import TestSuite, TestCase

from cba.teds.teradata.qa.artifacts.AssembledPackage import *
from cba.teds.utils.WorkingDirectory import forceWorkingDirectory


class testHelperFunction(unittest.TestCase):
    """
    Unit Tests for the extractObjectNameFromFilePath() Helper Function.
    """

    @classmethod
    def setUpClass(self):
        forceWorkingDirectory()

    def test_extractedFilesDirectory(self):
        self.assertEqual(extractObjectNameFromFilePath("/TERADATA/abc/def/ghi/myTable.tbl"), "myTable", "Check Object Name 01")
        self.assertEqual(extractObjectNameFromFilePath("/DBAI/xyz/mySQL.sql"), "mySQL", "Check Object Name 02")


class testAssembledPackage(unittest.TestCase):
    """
    Unit Tests for the AssembledPackage Class.

    Many of the unit tests leverage a package called "test_assembled_package.tgz" in "resources/test/" that is used to
    create an Assembled Package in setUpClass().

    NOTE:  The destructor for AssembledPackage will perform any necessary cleanup.
    """

    @classmethod
    def setUpClass(self):

        forceWorkingDirectory()

        self._testPackageFileName = "test_assembled_package.tgz"
        self._testPackageLocation = "resources/test/"

        self._assembledPackage = AssembledPackage(self._testPackageLocation, self._testPackageFileName)


    def test_extractedFilesDirectory(self):
        self.assertIsNotNone(self._assembledPackage, "Check Package")
        self.assertTrue(os.path.exists(self._assembledPackage.extractedFilesDirectory()), "Check Extracted Files")

    def test_retrieveAssembledPackageFilesList(self):
        self.assertIsNotNone(self._assembledPackage, "Check Package")
        self.assertTrue(len(self._assembledPackage.retrieveAssembledPackageFilesList()) > 0, "Check File List")

    def test_name(self):
        self.assertIsNotNone(self._assembledPackage, "Check Package")
        self.assertIsNotNone(self._assembledPackage.name(), "Check Name")

    def test_retrieveChangeRequestNumber(self):
        self.assertIsNotNone(self._assembledPackage, "Check Package")
        self.assertEqual(self._assembledPackage.retrieveChangeRequestNumber(), "C1403206", "Check Change Number")

    def test_retrieveTeradataKeywords(self):
        self.assertIsNotNone(self._assembledPackage, "Check Package")
        self.assertTrue(len(self._assembledPackage.retrieveTeradataKeywords()) > 0, "Check Keywords")

    def test_retrieveCreatedObjects(self):
        self.assertIsNotNone(self._assembledPackage, "Check Package")
        self.assertTrue(len(self._assembledPackage.retrieveCreatedObjects()) > 0, "Check Created Objects")

    def test_retrieveDeletedObjects(self):
        self.assertIsNotNone(self._assembledPackage, "Check Package")
        self.assertTrue(len(self._assembledPackage.retrieveDeletedObjects()) > 0, "Check Deleted Objects")

    def test_retrieveRolledBackObjects(self):
        self.assertIsNotNone(self._assembledPackage, "Check Package")
        self.assertTrue(len(self._assembledPackage.retrieveRolledBackObjects()) > 0, "Check Rolled Back Objects")


class testImaginaryAssembledPackage(unittest.TestCase):
    """
    Unit Tests for the AssembledPackage Class using an imaginary (i.e. doesn't exist) package.
    """

    @classmethod
    def setUpClass(self):

        forceWorkingDirectory()

    def test_ImaginaryPackage(self):
        self._testPackageLocation = "resources/test/"
        self._testPackageFileName = "imaginary_file.tgz"
        self.assertRaises(ValueError, AssembledPackage, self._testPackageLocation, self._testPackageFileName)


class testGoodAssembledPackage(unittest.TestCase):
    """
    Unit Tests for the AssembledPackage Class using the goodPackage under /resources/test/.
    """

    @classmethod
    def setUpClass(self):

        forceWorkingDirectory()

        self._testPackageFileName = "ALREADY_EXTRACTED"
        self._testPackageLocation = "resources/test/"
        self._extractionDirectory = "goodPackage"

        self._assembledPackage = AssembledPackage(self._testPackageLocation, self._testPackageFileName, self._extractionDirectory)
        self._assembledPackage.runChecks("resources/teradataQualityCheckRules.xml", "output/testGoodAssembledPackage.xml")

    def test_GoodPackage(self):
        self.assertIsNotNone(self._assembledPackage, "Check Package")
        self.assertTrue(os.path.exists(self._assembledPackage.extractedFilesDirectory()), "Check Extracted Files")

        for testCaseKey in self._assembledPackage._ruleRunner._testCases:
            testCase = self._assembledPackage._ruleRunner._testCases.get(testCaseKey)
            self.assertIsNone(testCase.failure_message)
            self.assertIsNone(testCase.error_message)


class testBadAssembledPackage(unittest.TestCase):
    """
    Unit Tests for the AssembledPackage Class using the badPackage under /resources/test/.
    """

    @classmethod
    def setUpClass(self):

        forceWorkingDirectory()

        self._testPackageFileName = "ALREADY_EXTRACTED"
        self._testPackageLocation = "resources/test/"
        self._extractionDirectory = "badPackage"

        self._assembledPackage = AssembledPackage(self._testPackageLocation, self._testPackageFileName, self._extractionDirectory)
        self._assembledPackage.runChecks("resources/teradataQualityCheckRules.xml", "output/testBadAssembledPackage.xml")

    def test_TCFColumns(self):
        testCases = self._assembledPackage._ruleRunner._testCases
        tableDirectoryPath = '/TERADATA/P_D_BAL_001/P_D_BAL_001_STD_0/'

        # Test QA Checks Fail on Recorded Deleted Column
        createTableTestCase = testCases.get(('%s%s' % (tableDirectoryPath,'FAIL_TEST_RecordDeletedColumn.tbl')))
        self.assertEquals(createTableTestCase.failure_message, 'Record Deleted Columns must contain COMPRESS (0,1) ([[A-1]])')

        # Test QA Checks Fail on Process Name Column
        createTableTestCase = testCases.get(('%s%s' % (tableDirectoryPath,'FAIL_TEST_ProcessNameColumn.tbl')))
        self.assertEquals(createTableTestCase.failure_message, 'Compress value is missing in Process Name ([[A-1]])')

        # Test QA Checks Fail on Update Process Name Column
        createTableTestCase = testCases.get(('%s%s' % (tableDirectoryPath,'FAIL_TEST_UpdateProcessNameColumn.tbl')))
        self.assertEquals(createTableTestCase.failure_message, 'Compress is missing in Update Process Name ([[A-1]])')

        # Test QA Checks Fail on CTL ID Column
        createTableTestCase = testCases.get(('%s%s' % (tableDirectoryPath,'FAIL_TEST_CTL_IDColumn.tbl')))
        self.assertEquals(createTableTestCase.failure_message, 'COMPRESS with some number is missing in CTL ID ([[A-1]])')

        # Test QA Checks WARNING on EXPY D Column
        createTableTestCase = testCases.get(('%s%s' % (tableDirectoryPath,'FAIL_TEST_EXPY_DColumn.tbl')))
        self.assertEquals(createTableTestCase.error_message, 'EXPY_D column must have compress date ([[A-1]])')

        # Test QA Checks WARNING on EXPY TS Column
        createTableTestCase = testCases.get(('%s%s' % (tableDirectoryPath,'FAIL_TEST_EXPY_TSColumn.tbl')))
        self.assertEquals(createTableTestCase.error_message, 'EXPY_TS column must have compress timestamp ([[A-1]])')

        # Test QA Checks WARNING on MULTISET Create table statement
        createTableTestCase = testCases.get(('%s%s' % (tableDirectoryPath,'FAIL_TEST_MultisetCreateTable.tbl')))
        self.assertEquals(createTableTestCase.error_message, 'Create Table Statements must contain MULTISET ([[A-2]])')

    def test_StatisticsEngine(self):
        testCases = self._assembledPackage._ruleRunner._testCases
        tableDirectoryPath = '/TERADATA/P_D_BAL_001/P_D_BAL_001_STD_0/'
        # Test QA Checks Fail on STS file found
        testCase = testCases.get(('%s%s' % (tableDirectoryPath,'P_D_BAL_001_STD_0.FACT_ACCT_BALN_STG.sts')))
        self.assertEquals(testCase.failure_message, 'STS file is found in STG Table([[A-11]])')

        # Test QA Checks Fail on STS file found
        testCase = testCases.get(('%s%s' % (tableDirectoryPath,'FAIL_TEST_FACT_ACCT_BALN_TEMP.sts')))
        self.assertEquals(testCase.failure_message, 'STS file is found in TEMP Table([[A-11]])')

        # Test QA Checks Fail on STS file found
        testCase = testCases.get(('%s%s' % (tableDirectoryPath,'FAIL_TEST_FACT_ACCT_BALN_WRK.sts')))
        self.assertEquals(testCase.failure_message, 'STS file is found in WRK Table([[A-11]])')

    def test_ReservedKeywords(self):
        testCases = self._assembledPackage._ruleRunner._testCases
        tableDirectoryPath = '/TERADATA/P_D_BAL_001/P_D_BAL_001_STD_0/'

        # Test QA Checks Fail on Teradata Reserved Keywords (Table columns)
        testCase = testCases.get(('%s%s' % (tableDirectoryPath,'FAIL_TEST_KeywordsCheck.tbl')))
        self.assertEquals(testCase.failure_message, 'Database Column contains Teradata keywords([[A-10]])')

    def test_HardCodedDatabaseName(self):
        testCases = self._assembledPackage._ruleRunner._testCases
        tableDirectoryPath = '/TERADATA/P_D_BAL_001/P_D_BAL_001_STD_0/'

        # Test QA Checks Fail on Hardcoded development database name
        testCase = testCases.get(('%s%s' % (tableDirectoryPath,'FAIL_TEST_DevDatabaseTable.tbl')))
        self.assertEquals(testCase.failure_message, 'Non-production database name is found([[A-3]])')

    def test_MissingLockingRow(self):
        testCases = self._assembledPackage._ruleRunner._testCases
        # Test QA Checks Fail on missing Locking Row in the View
        testCase = testCases.get('/TERADATA/P_V_BAL_001/P_V_BAL_001_STD_0/Fail_Test_LockingRow.viw')
        self.assertEquals(testCase.failure_message, 'LOCKING ROW should exist in the View([[A-6]])')

    def test_LongComments(self):
        testCases = self._assembledPackage._ruleRunner._testCases
        # Test QA Checks Fail on Comments longer than 256 characters
        testCase = testCases.get('/TERADATA/P_V_BAL_001/P_V_BAL_001_STD_0/Fail_Test_LongComments.cmt')
        self.assertEquals(testCase.failure_message, 'Comments must be less than 256 characters ([[A-9]])')

    def test_InvalidChangeNumberFormat(self):
        testCases = self._assembledPackage._ruleRunner._testCases
        # Test QA Checks WARNING on invalid CR number
        testCase = testCases.get('.Change Record Number')
        self.assertEquals(testCase.error_message, 'The Change Record Number is: CXXXXXXX')

    def test_InvalidChangeNumberInComment(self):
        testCases = self._assembledPackage._ruleRunner._testCases
        # Test QA Checks Fail on Comments (Valid Change Number is missing in the Comment)
        testCase = testCases.get('/TERADATA/P_D_BAL_001/P_D_BAL_001_STD_0/P_D_BAL_001_STD_0.FACT_ACCT_BALN_STG.cmt')
        self.assertEquals(testCase.failure_message, 'Comments must contain the Change Record (CR) Number ([[A-7]])')

    def test_BadPackage(self):
        self.assertIsNotNone(self._assembledPackage, "Check Package")
        self.assertTrue(os.path.exists(self._assembledPackage.extractedFilesDirectory()), "Check Extracted Files")
        testCases = self._assembledPackage._ruleRunner._testCases
        tableDirectoryPath = '/TERADATA/P_D_BAL_001/P_D_BAL_001_STD_0/'

        for testCaseKey in testCases:
            testCase = self._assembledPackage._ruleRunner._testCases.get(testCaseKey)
            print('testCase.failure_message', testCase.name)
            # self.assertIsNotNone(testCase.failure_message)
            # self.assertIsNotNone(testCase.error_message)

        # Test QA Checks Fail on Table and Table Comments
        createTableTestCase = testCases.get('/DBAI/AUTO_BACKUP/Auto_Backup_Tables/10_R2.123_Backup_Tables.sql')
        self.assertEquals(createTableTestCase.failure_message, 'Backup Tables must contain the Change Record (CR) Number ([[A-4]]) _BR_ Backup Table Comments must contain the Change Record (CR) Number ([[A-4]])')

        print('1', createTableTestCase.error_message)
        print('2', createTableTestCase.failure_message)
        print('3', createTableTestCase.stdout)








if __name__ == "__main__":
    unittest.main()