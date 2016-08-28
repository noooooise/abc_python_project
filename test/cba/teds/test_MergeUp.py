
import datetime
import time
import unittest

from cba.teds.utils.StashRepository import StashRepository

from cba.teds.MergeUp import mergeUp, appendMergeUpResult 
from cba.teds.utils.StashRepository import MergeResult
from junit_xml import TestSuite

class testMergeUp(unittest.TestCase):
    """
    Unit Tests for MergeUp Script.
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
        

    def test_doesMergeWork(self):
        """
        Tests that a merge "works" (i.e. doesn't throw an exception). Known failures e.g. "Branch is already up-to-date" are OK.
        """        
          
        try:    
                      
            argsString =  "-p %s -r %s -s unitTestA,unitTestB,unitTestC,unitTestD -t master -U %s -P %s" % (self._project, self._repository, self._user, self._password)
            args = argsString.split()                                    
            mergeUp(args)
  
        except Exception as e:
            self.fail("MergeUp.py threw an exception (%s)." % (e))
    
    def test_MergeUpArguments(self):
        try:
            mergeUp(['-h'])
        except SystemExit as e:
            self.assertIsInstance(e, SystemExit, 'Checking for System Exit')
            
        try:
            mergeUp([])
        except SystemExit as e:
            self.assertIsInstance(e, SystemExit, 'Checking for System Exit')
            
        try:
            mergeUp(['d'])
        except SystemExit as e:
            self.assertIsInstance(e, SystemExit, 'Checking for System Exit')

    def test_appendMergeUpResult(self):
        
        testSuite = TestSuite("Merge Down")
        appendMergeUpResult(MergeResult.Merged, testSuite, 'source_branch', 'target_branch', 1 )
        expectedResult = 'Merge Up from source_branch to target_branch was successful.'
        self.assertEqual(testSuite.test_cases[0].name, expectedResult, 'Test appendMergeUpResult 1')
        
        appendMergeUpResult(MergeResult.Unnecessary, testSuite, 'source_branch', 'target_branch', 1 )
        expectedResult = 'Merge Up from source_branch to target_branch is unnecessary.'
        self.assertEqual(testSuite.test_cases[1].name, expectedResult, 'Test appendMergeUpResult 2')
        
        
        appendMergeUpResult(MergeResult.Conflicts, testSuite, 'source_branch', 'target_branch', 1 )
        expectedResult = 'Merge Up from source_branch to target_branch failed (Conflicts).'
        self.assertEqual(testSuite.test_cases[2].name, expectedResult, 'Test appendMergeUpResult 3')
                 

if __name__ == "__main__":
    unittest.main()