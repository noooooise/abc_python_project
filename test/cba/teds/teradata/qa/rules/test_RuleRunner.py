
import unittest

from cba.teds.teradata.qa.rules.Rule import *
from cba.teds.teradata.qa.rules.RuleRunner import RuleRunner
from cba.teds.teradata.qa.artifacts.AssembledPackage import AssembledPackage
from cba.teds.utils.WorkingDirectory import forceWorkingDirectory


class testRuleRunner(unittest.TestCase):
    """
    Unit Tests for RuleRunner Class.

    ???
    """
    @classmethod
    def setUpClass(self):
        self._testPackageLocation = "resources/test/"
        forceWorkingDirectory()
        testPackageFileName = "test_assembled_package.tgz"
        self._assembledPackage = AssembledPackage(self._testPackageLocation, testPackageFileName)


    def test_ruleRunnerConstructor(self):

        ruleRunner = RuleRunner('resources/teradataQualityCheckRules.xml', self._assembledPackage)

        whenMapGroupByFilter = ruleRunner._filterMaps
        whenMapGroupByScope = ruleRunner._scopeMaps
        whenMapFromFilter = whenMapGroupByFilter.get('CREATE_TABLE')
        # self.assertEquals(whenMapFromFilter['Create Table Statement'].name, 'Create Table Statement', 'Check for Create Table Statement in whenMapGroupByFilter')
        # self.assertEquals(whenMapFromFilter['Record Deleted Column'].name, 'Record Deleted Column', 'Check for Record Deleted Column in whenMapGroupByFilter')
        # self.assertEquals(whenMapFromFilter['Process Name Column'].name, 'Process Name Column', 'Check for Process Name Column in whenMapGroupByFilter')
        # self.assertEquals(whenMapFromFilter['Update Process Name Column'].name, 'Update Process Name Column', 'Check for Update Process Name Column in whenMapGroupByFilter')

        whenMapFromScope = whenMapGroupByScope.get('LINE')
        # self.assertEquals(whenMapFromScope['Create Table Statement'].name, 'Create Table Statement', 'Check for Create Table Statement in tableWhenMapFromScope')
        # self.assertEquals(whenMapFromScope['Record Deleted Column'].name, 'Record Deleted Column', 'Check for Record Deleted Column in tableWhenMapFromScope')
        # self.assertEquals(whenMapFromScope['Process Name Column'].name, 'Process Name Column', 'Check for Process Name Column in tableWhenMapFromScope')
        # self.assertEquals(whenMapFromScope['Update Process Name Column'].name, 'Update Process Name Column', 'Check for Update Process Name Column in tableWhenMapFromScope')

        # Hardcode the number of maps so that we know how many scopes types or filter types are configured in the RULE file
        # self.assertEquals(len(ruleRunner._scopeMaps), 2, 'Scope should have only 2 maps')
        # self.assertEquals(len(ruleRunner._filterMaps), 3, 'Filter should have only 2 maps(ALL/TABLE/VIEW/COMMENT)')

        whenMapFromFilter = whenMapGroupByFilter.get('CREATE_VIEW')
        # self.assertEquals(whenMapFromFilter['Create View'].name, 'Create View', 'Check for Create View in whenMapGroupByFilter')

        ruleRunner.runRules()
        junitFileName = "output/junit-GeneratedFromRuleRunner.xml"
        ruleRunner.generateReport(junitFileName)


    def test_buildWhenData(self):

        ruleRunner = RuleRunner('resources/teradataQualityCheckRules.xml', self._assembledPackage)
        when = When("Someone says BeetleJuice!", "BeetleJuice", WhenType.Contains.value, WhenScope.Line.value,
                    WhenFilter.All.value)
        ruleRunner._buildWhenData('imaginary_file_path.tbl', when)

        when = When("Someone says BeetleJuice!", "BeetleJuice", WhenType.Contains.value, WhenScope.Script.value,
                    WhenFilter.All.value)
        ruleRunner._buildWhenData('imaginary_file_path.tbl', when)


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()