
import unittest
import os

from cba.teds.utils.WorkingDirectory import forceWorkingDirectory

class testRule(unittest.TestCase):
    """
    Unit Tests for forceWorkingDirectory
    """
    @classmethod
    def setUpClass(self):
        forceWorkingDirectory()

    def test_forceWorkingDirectory(self):
        newWorkingDirectory = 'test'
        os.chdir(newWorkingDirectory)
        forceWorkingDirectory()
        self.assertTrue(os.path.exists("test"), 'test directory exist')

        newWorkingDirectory = 'test/cba'
        os.chdir(newWorkingDirectory)
        forceWorkingDirectory()
        self.assertTrue(os.path.exists("test"), 'test directory exist')

        newWorkingDirectory = 'test/cba/teds'
        os.chdir(newWorkingDirectory)
        forceWorkingDirectory()
        self.assertTrue(os.path.exists("test"), 'test directory exist')

        newWorkingDirectory = 'test/cba/teds/teradata'
        os.chdir(newWorkingDirectory)
        forceWorkingDirectory()
        self.assertTrue(os.path.exists("test"), 'test directory exist')

        newWorkingDirectory = 'test/cba/teds/teradata/qa'
        os.chdir(newWorkingDirectory)
        forceWorkingDirectory()
        self.assertTrue(os.path.exists("test"), 'test directory exist')

        newWorkingDirectory = 'test/cba/teds/teradata/qa/rules'
        os.chdir(newWorkingDirectory)
        forceWorkingDirectory()
        self.assertTrue(os.path.exists("test"), 'test directory exist')

        newWorkingDirectory = '../'
        os.chdir(newWorkingDirectory)
        forceWorkingDirectory()
        self.assertFalse(os.path.exists("test"), 'test directory should NOT exist')
