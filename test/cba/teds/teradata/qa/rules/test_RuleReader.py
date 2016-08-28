
import unittest

from cba.teds.teradata.qa.rules.RuleReader import RuleReader
from cba.teds.utils.WorkingDirectory import forceWorkingDirectory


class testRuleReader(unittest.TestCase):
    """
    Unit Tests for RuleReader Class.
    """

    @classmethod
    def setUp(self):
        forceWorkingDirectory()

        self._fileLocation = "resources/test/testRules.xml"
        self._ruleReader = RuleReader(self._fileLocation)

    def test_ruleReader(self):
        self.assertIsNotNone(self._ruleReader, "Check Rule Reader")

    def test_retrieveListOfWhenConditions(self):
        whens = self._ruleReader.retrieveListOfWhenConditions()
        self.assertEqual(len(whens), 1, "Check Whens")

    def test_retrieveListOfActions(self):
        actions = self._ruleReader.retrieveListOfActions()
        self.assertEqual(len(actions), 1, "Check Actions")

    def test_retrieveListOfRules(self):
        rules = self._ruleReader.retrieveListOfRules()
        self.assertEqual(len(rules), 1, "Check Rules")

    def test_noRulesFile(self):
        fileLocation = "resources/test/imaginary_file.xml"
        ruleReader = RuleReader(fileLocation)
        whens = ruleReader.retrieveListOfWhenConditions()
        self.assertEqual(len(whens), 0, "Check Empty")


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()