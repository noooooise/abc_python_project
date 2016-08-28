
import datetime
import time
import unittest

from cba.teds.utils.StashRepository import StashRepository

from cba.teds.MergeDown import mergeDown, appendMergeDownResult
from junit_xml import TestSuite, TestCase
from cba.teds.utils.StashRepository import MergeResult

class testMergeDown(unittest.TestCase):
    """
    Unit Tests for MergeDown Script.
    """

    @classmethod
    def setUpClass(self):

        rightNow = time.time()
        timestampString = datetime.datetime.fromtimestamp(rightNow).strftime("%Y%m%d%H%M%S")
        forkName = "UNIT_TEST_FORK_" + timestampString

        self._user = "teradata-ci"
        self._password = "Passw0rd!"

        testHarnessRepository = StashRepository(self._user, self._password, "GDW", "TEST_HARNESS_DATA")
        testHarnessRepository.forkRepository(forkName)

        self._project = "~teradata-ci"
        self._repository = forkName
        self._stashRepository = StashRepository(self._user, self._password, self._project, self._repository)
                
    @classmethod
    def tearDownClass(self):

        self._stashRepository.deleteRepository()  
        
    def test_doesMergeDownWork(self):
        """
        Tests that a merge "works" (i.e. doesn't throw an exception). Known failures e.g. "Branch is already up-to-date" are OK.
        """
           
        try:                     
            argsString =  "-p %s -r %s -s master -t * -U %s -P %s" % (self._project, self._repository, self._user, self._password)
            args = argsString.split()                             
            mergeDown(args)
   
        except Exception as e:
            self.fail("MergeDown.py threw an exception (%s)." % (e))
                 

    def test_MergeDownArguments(self):
        try:
            mergeDown(['d'])
        except SystemExit as e:
            self.assertIsInstance(e, SystemExit, 'Checking for System Exit')
            
        try:
            mergeDown("h".split())
        except SystemExit as e:
            self.assertIsInstance(e, SystemExit, 'Checking for System Exit')
        
        try:
            mergeDown([])
        except SystemExit as e:
            self.assertIsInstance(e, SystemExit, 'Checking for System Exit')

        
    def test_appendMergeResult(self):
        
        testSuite = TestSuite("Merge Down")
        appendMergeDownResult(MergeResult.Merged, testSuite, 'source_branch', 'target_branch', 1 )
        expectedResult = 'Merge Down from source_branch to target_branch was successful.'
        self.assertEqual(testSuite.test_cases[0].name, expectedResult, 'Test appendMergeDownResult 1')
        
        appendMergeDownResult(MergeResult.Unnecessary, testSuite, 'source_branch', 'target_branch', 1 )
        expectedResult = 'Merge Down from source_branch to target_branch is unnecessary.'
        self.assertEqual(testSuite.test_cases[1].name, expectedResult, 'Test appendMergeDownResult 2')
        
        
        appendMergeDownResult(MergeResult.Conflicts, testSuite, 'source_branch', 'target_branch', 1 )
        expectedResult = 'Merge Down from source_branch to target_branch failed (Conflicts).'
        self.assertEqual(testSuite.test_cases[2].name, expectedResult, 'Test appendMergeDownResult 3')
        
        
if __name__ == "__main__":
    unittest.main()
