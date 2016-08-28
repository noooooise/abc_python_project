
import datetime
import time
import unittest

from cba.teds.utils.StashRepository import StashRepository
from cba.teds.utils.StashRepository import MergeResult


class testStashRepository(unittest.TestCase):
    """
    Unit Tests for StashRepository Class.
    
    These are currently configured to run against the "TEST_HARNESS_DATA" repository in the "GDW" project.
    """

    def __init__(self, *args, **kwargs):
        super(testStashRepository, self).__init__(*args, **kwargs)

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
          
    def test_doesMasterBranchExist(self):
        """
        Tests that there is a branch called "master" in the Repository.
        """

        branches = self._stashRepository.getBranchNames() 
        
        masterBranch = False        
        for branch in branches:
            if ( branch == 'master'):
                masterBranch = True
                break

        self.assertTrue(masterBranch, "There is no master branch called in the %s repository" % (self._repository))

    def test_tooManyBranches(self):
        """
        Tests that there are not more than BRANCH_LIMIT branches in the Repository.
        """

        self._BRANCH_LIMIT = 10

        branches = self._stashRepository.getBranchNames() 
        
        self.assertTrue(len(branches) < self._BRANCH_LIMIT, "There are too many (%s) branches in the %s repository." % (len(branches), self._repository))

    def test_doesMergeWork(self):
        """
        Tests that a merge "works" (i.e. doesn't throw an exception). Known failures e.g. "Branch is already up-to-date" are OK.
        """

        try:
            source = "master"
            target = "unitTestA"
            
            mergeResult = self._stashRepository.mergeBranches(source, target)
            if (mergeResult != MergeResult.Unnecessary):
                self.fail("Unexpected merge result when merging %s into %s" % (source, target))

        except Exception as e:
            self.fail("MergeBranches() threw an exception (%s)." % (e))


if __name__ == "__main__":
    unittest.main()