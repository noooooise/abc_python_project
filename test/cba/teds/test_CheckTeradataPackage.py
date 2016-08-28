
import unittest
import os

from cba.teds.utils.WorkingDirectory import forceWorkingDirectory
from cba.teds.CheckTeradataPackage import checkTeradataPackage


class Test(unittest.TestCase):
    """
    Unit Tests for CheckTeradataPackage Class.

    These are currently configured to run using "test_assembled_package.tgz" and "assembled_bteqs.tgz" in "resources/test/".
    """

    @classmethod
    def setUpClass(self):
        forceWorkingDirectory()
        self._rootDirectoryPath = "resources/test/"
        if ( os.path.isdir("output") == False ):
            print('output dir empty')
            os.makedirs('output')
        else:
            print("output dir exist")



    def test_CheckTeradataPackageAssembledPackage(self):
        try:

            tarName = "test_assembled_package.tgz"
            filePathOfPackage = self._rootDirectoryPath + '/' + tarName
            print(' filePathOfPackage ', filePathOfPackage)
            self.assertTrue(os.path.isfile(filePathOfPackage), 'test_assembled_package.tgz should exist')

            outputDir = 'extractDirName'
            printToJunitReport = 'output/junit-testCheckTeradataPackage.xml'
            teradataQualityCheckRuleFile = 'resources/teradataQualityCheckRules.xml'



            argsString = ('-q %s -r %s -t %s -o %s -p %s' % (teradataQualityCheckRuleFile,self._rootDirectoryPath, tarName, outputDir, printToJunitReport))
            args = argsString.split()
            checkTeradataPackage(args)

            self.assertTrue(os.path.isfile(printToJunitReport), 'generated junit report for Teradata QA should exist')

        except Exception as e:
            self.fail("CheckTeradataPackage.py threw an exception (%s)." % (e))

    def test_CheckTeradataPackageArguments(self):
        # Test -h or help argument
        try:
            checkTeradataPackage(['-h'])
        except SystemExit as e:
            self.assertIsInstance(e, SystemExit, 'Checking for System Exit')

        #Test empty argument
        try:
            checkTeradataPackage([])
        except SystemExit as e:
            self.assertIsInstance(e, SystemExit, 'Checking for System Exit')

        # Test invalid argument
        try:
            checkTeradataPackage(['-x'])
        except SystemExit as e:
            self.assertIsInstance(e, SystemExit, 'Checking for System Exit')


if __name__ == "__main__":
    unittest.main()