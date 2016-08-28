
import unittest

from cba.teds.teradata.qa.artifacts.AssembledBTEQ import *
from cba.teds.utils.WorkingDirectory import forceWorkingDirectory


class testAssembledBTEQ(unittest.TestCase):

    packageFileDir = "resources/test/"
    
    packageFileDirAbsoluteFilePath = ""

    @classmethod
    def setUpClass(self):

        forceWorkingDirectory()

    @classmethod
    def setUp(self):

        if os.path.exists(self.packageFileDir):
            self.packageFileDirAbsoluteFilePath = os.path.abspath(self.packageFileDir)
        else:
            if os.path.exists( "../" + self.packageFileDir):
                self.packageFileDir = "../resources/test/"
                self.packageFileDirAbsoluteFilePath = os.path.abspath(self.packageFileDir)

    @classmethod
    def tearDown(self):
        assembledBTEQ = AssembledBTEQ(self.packageFileDir, "assembled_bteqs.tgz")
        if assembledBTEQ._isExtractFilePathExist():
            assembledBTEQ._deleteExtractedFiles()

    def testExtractReleasePackageWithDefaultDir(self):
        packagedFileName = "assembled_bteqs.tgz"     
        assembledBTEQ = AssembledBTEQ(self.packageFileDir, packagedFileName)
        
        # assembledBTEQ._extractFile()
        # self.assertTrue(assembledBTEQ._extractFile(), "Testing valid tar file. extractFile() should extract the tar file and return true")
        self.assertTrue(assembledBTEQ._isExtractFilePathExist(), "extract directory should exist")
        expactedOutputExtractFilePath = os.path.abspath(self.packageFileDirAbsoluteFilePath + "/defaultExtractDir" )
        self.assertEqual(assembledBTEQ._getExtractFileAbsolutePath(), expactedOutputExtractFilePath,"check getExtractFileAbsolutePath ")


    
    def testExtractReleasePackageWithCustomDir(self):
        packagedFileName = "assembled_bteqs.tgz"
        assembledBTEQ = AssembledBTEQ(self.packageFileDir, packagedFileName, "customUnitTestExtractDir")

        self.assertTrue(assembledBTEQ._isExtractFilePathExist(), "extract directory should exist")
        expactedOutputExtractFilePath = os.path.abspath(self.packageFileDirAbsoluteFilePath + "/customUnitTestExtractDir" )
        self.assertEqual(assembledBTEQ._getExtractFileAbsolutePath(), expactedOutputExtractFilePath)

        self.assertTrue(len(assembledBTEQ.retrieveAssembledBTEQFilesList()) > 20, 'Some files exist')

        assembledBTEQ._deleteExtractedFiles()
        self.assertFalse(assembledBTEQ._isExtractFilePathExist(), "extract directory should NOT exist because it was deleted in previous step")
    
    def testInvalidTarFile(self):
        packagedFileName = "assembled_bteqs_invalid_file_name.tgz"     
        extractReleasePackage = AssembledBTEQ(self.packageFileDir, packagedFileName, "customUnitTestExtractDir")
        self.assertFalse(extractReleasePackage._extractFile(), "Testing invalid tar. extractFile() should fail and return false")

        
if __name__ == "__main__":
    #import sys;sys.argv = ["", "Test.testName"]
    unittest.main()