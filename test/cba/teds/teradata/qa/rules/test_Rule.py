
import unittest

from cba.teds.teradata.qa.rules.Rule import *
from cba.teds.teradata.qa.artifacts.AssembledPackage import AssembledPackage
from cba.teds.utils.WorkingDirectory import forceWorkingDirectory

class testRule(unittest.TestCase):
    """
    Unit Tests for Classes and Enums in Rule.py (i.e. the object model that supports our quality checks).
    """

    @classmethod
    def setUpClass(self):
        self._testPackageLocation = "resources/test/"
        forceWorkingDirectory()
        testPackageFileName = "test_assembled_package.tgz"
        self._assembledPackage = AssembledPackage(self._testPackageLocation, testPackageFileName)

    def test_readRules(self):

        when = When("Someone says BeetleJuice!", "BeetleJuice", WhenType.Contains.value, WhenScope.Script.value,
                    WhenFilter.All.value)

        # when.data.append(WhenData("IMDB", "Adam and Barbara are a normal couple...who happen to be dead. They have "
        #                                   "given their precious time to decorate the house and make it their own, but "
        #                                   "unfortunately a family is moving in, and not quietly. Adam and Barbara try "
        #                                   "to scare them out, but ends up becoming the main attraction to the money "
        #                                   "making family. They call upon BeetleJuice to help, but BeetleJuice has more"
        #                                   " in mind than just helping."))
        when.data.append(WhenData("IMDB", "Adam and Barbara are a normal couple...who happen to be dead. They have "
                                          "given their precious time to decorate the house"))

        action = Action("Check for Duplicates", ActionType.TextMatch.value, "BeetleJuice BeetleJuice BeetleJuice")

        rule = Rule(when, action, RuleLevel.Error.value, "Run For The Hills!")

        self.assertEqual(when.__str__(), "When: {name: (Someone says BeetleJuice!), value: (BeetleJuice), type: "
                                         "(CONTAINS), scope: (SCRIPT), filter: (ALL)}")

        self.assertEqual(action.__str__(), "Action: {name: (Check for Duplicates), actionType: (textMatch), actionData:"
                                           " (BeetleJuice BeetleJuice BeetleJuice)}")

        self.assertEqual(rule.__str__(), "Rule: {when: (Someone says BeetleJuice!), action: (Check for Duplicates), "
                                         "level: (error), message: (Run For The Hills!)}")

        self.assertEqual(when.data[0].__str__(), "WhenData: {artifactName: (IMDB), data: (Adam and Barbara are a normal couple...who happen to be dead. They have given their precious time to decorate the house)}")

    def test_isConditionMatchedForWhen(self):

        # Test CONTAINS (WhenType)
        when = When("Create Table Statement", "TABLE P_D", WhenType.Contains.value, WhenScope.Line.value,
                    WhenFilter.CreateTable.value)

        self.assertTrue(when.isConditionMatched('CREATE MULTISET TABLE P_D'), 'Test for Production Database Table')
        self.assertFalse(when.isConditionMatched('CREATE MULTISET TABLE DEVELOPMENT'), 'Test no Match for when condition')

    def test_isConditionMatchedForBeginsWithWhenType(self):
        # Test BEGINS_WITH (WhenType)
        when = When("TCF Column (RECORD_DELETED_FLAG)", "RECORD_DELETED_FLAG BYTEINT", WhenType.BeginsWith.value, WhenScope.Line.value,
                    WhenFilter.CreateTable.value)

        self.assertTrue(when.isConditionMatched('RECORD_DELETED_FLAG BYTEINT'), 'Test for Production Database Table')
        self.assertFalse(when.isConditionMatched('SOMETHING RECORD_DELETED_FLAG BYTEINT'), 'Test no Match for when condition')
        self.assertFalse(when.isConditionMatched('SOMEOTHERCOLUMN BYTEINT'), 'Test no Match for when condition')

    def test_isConditionMatchedForMatchesPatternWhenType(self):
        # TEST MATCHES_PATTERN (WhenType)
        when = When("Check for ByteInt Compression", "COMPRESS\s?\(\s?0\s?,\s?1\s?\)", WhenType.MatchesPattern.value, WhenScope.Line.value,
                    WhenFilter.CreateTable.value)

        self.assertTrue(when.isConditionMatched('COMPRESS (0,1)'), 'Test for patternMatch Valid 1')
        self.assertTrue(when.isConditionMatched('COMPRESS (0, 1)'), 'Test for patternMatch Valid 2')
        self.assertTrue(when.isConditionMatched('COMPRESS ( 0, 1 )'), 'Test for patternMatch Valid 3')
        self.assertFalse(when.isConditionMatched('COMPRESS ( 0 )'), 'Test for patternMatch Missing 1')
        self.assertFalse(when.isConditionMatched('COMPRESS ( 1 )'), 'Test for patternMatch Missing 0')

         # TEST MATCHES_PATTERN (WhenType)
        when = When("Database Column", "\sTITLE\s\'", WhenType.MatchesPattern.value, WhenScope.Line.value,
                    WhenFilter.CreateTable.value)

        self.assertTrue(when.isConditionMatched("ACCT_IDNN_HK CHAR(32) CHARACTER SET LATIN NOT CASESPECIFIC TITLE 'Account Identifier HK' NOT NULL,"), 'Test for patternMatch Valid 1')
        self.assertFalse(when.isConditionMatched("CREATE MULTISET TABLE P_D_BUS_001_STD_0.S_ACCT_ARRS_NEW ,NO FALLBACK ,"), 'Pattern should not match')

    def test_isConditionMatchForDevelopmentDB(self):

        #   '\s[A]\_' use: '\s[A-Z]\_[DS][0-9]{2}\_[DVJF]'
        # "COMPRESS\s?\(\s?0\s?,\s?1\s?\)"
        # OLD : \s[A-OQ-Z]\_
        # NEW : \s[A-Z]\_[DS][0-9]{2}\_[DVJF]

        # regex1 = "\s[A-Z]\_?[DS]?[0-9]{0,2}\_[DVJF]"
        regex1 = "\s[A-OQ-Z]\_[DS][0-9]{2}\_[DVJF]"
        when = When("Check for Development Database", regex1, WhenType.MatchesPattern.value, WhenScope.Line.value,
                    WhenFilter.CreateTable.value)
        # This is valid
        self.assertFalse(when.isConditionMatched('AS P_V_INP_001_STD_0.TX_92_1_S_HLS_ACCT_ATTR'), 'Test for patternMatch View Valid 1')
        self.assertFalse(when.isConditionMatched('AS P_D_INP_001_STD_0.TX_92_1_S_HLS_ACCT_ATTR'), 'Test for patternMatch Table Valid 1')

        self.assertTrue(when.isConditionMatched('AS A_D06_V_INP_001_STD_0.TX_92_1_S_HLS_ACCT_ATTR'), 'Test for patternMatch Valid 2')
        self.assertTrue(when.isConditionMatched('AS D_D06_V_INP_001_STD_0.TX_92_1_S_HLS_ACCT_ATTR'), 'Test for patternMatch Valid 3')
        self.assertTrue(when.isConditionMatched('AS Q_D06_V_INP_001_STD_0.TX_92_1_S_HLS_ACCT_ATTR'), 'Test for patternMatch Valid 4')
        self.assertTrue(when.isConditionMatched('AS Z_D06_V_INP_001_STD_0.TX_92_1_S_HLS_ACCT_ATTR'), 'Test for patternMatch Valid 5')

    def test_validChangeNumberFormat(self):
        regExp = 'C\d{7}'
        data = 'hhhhh C123467'
        self.assertIsNone(re.search(regExp, data), 'Testing None 1')

        data = 'hhhhh D1234567'
        self.assertIsNone(re.search(regExp, data), 'Testing None 2')

        data = 'hhhhh 1234567'
        self.assertIsNone(re.search(regExp, data), 'Testing None 3')

        # Test for VALID CR Number
        data = 'hhhhh C1234567'
        self.assertIsNotNone(re.search(regExp, data), 'Testing Not None')

    def test_executeAction(self):
        action = Action("Check for Multiset Statement", ActionType.TextMatch.value, "MULTISET")

        # Check for Action Not Required
        self.assertFalse(action.executeAction('CREATE MULTISET TABLE', self._assembledPackage), 'Multiset exist')

        # Check for Action Required and produce Error
        self.assertTrue(action.executeAction('CREATE SET TABLE', self._assembledPackage), 'Multiset exist')
        self.assertTrue(action.executeAction('CREATE TABLE', self._assembledPackage), 'Multiset exist')

        action = Action("Check for ByteInt Compression", ActionType.PatternMatch.value, "COMPRESS\s?\(\s?0\s?,\s?1\s?\)")
        # Check for Action Not Required
        self.assertFalse(action.executeAction('COMPRESS (0,1)', self._assembledPackage), 'Valid COMPRESS 1')
        self.assertFalse(action.executeAction('COMPRESS ( 0,1)', self._assembledPackage), 'Valid COMPRESS 2')
        self.assertFalse(action.executeAction('COMPRESS ( 0 , 1 )', self._assembledPackage), 'Valid COMPRESS 3')
        # Check for Action Required and produce Error
        self.assertTrue(action.executeAction('COMPRESS ( 0 )', self._assembledPackage), 'Test for patternMatch Missing 1')
        self.assertTrue(action.executeAction('COMPRESS ( 1 )', self._assembledPackage), 'Test for patternMatch Missing 0')

    def test_executeActionCompressNum(self):
        action = Action("Check for Number Compression", ActionType.PatternMatch.value, "COMPRESS\s?\(?\d+\)?,?")
        # Check for Action Not Required
        self.assertFalse(action.executeAction('COMPRESS 1, ', self._assembledPackage), 'Valid COMPRESS 1')
        self.assertFalse(action.executeAction('COMPRESS 1 ,', self._assembledPackage), 'Valid COMPRESS 2')


    def test_executeActionLockingRow(self):
        # action = Action("Check for Locking Rows", ActionType.PatternMatch.value, "LOCKING\s+ROW\s+FOR\s+ACCESS")
        action = Action("Check for Locking Rows", ActionType.PatternMatch.value, "LOCKING\s+ROW\s+.*\s*ACCESS")


        # Check for Action Not Required
        self.assertFalse(action.executeAction('LOCKING ROW FOR ACCESS', self._assembledPackage), 'Valid COMPRESS 1')
        self.assertFalse(action.executeAction('LOCKING  ROW FOR ACCESS', self._assembledPackage), 'Valid COMPRESS 2')
        self.assertFalse(action.executeAction('LOCKING ROW   FOR   ACCESS', self._assembledPackage), 'Valid COMPRESS 3')
        self.assertFalse(action.executeAction('LOCKING ROW asdf as   ACCESS', self._assembledPackage), 'Valid COMPRESS 3')

        # Check for Action Required and produce Error
        self.assertTrue(action.executeAction('LOCKINGROW   FOR   ACCESS', self._assembledPackage), 'Valid COMPRESS 3')

    def test_executeActionForCRNumber(self):
        action = Action("Check for CR Number", ActionType.ContainsCrNumber.value, "")
        self._assembledPackage._changeRequestNumber = 'C1112223'

        ###### Check for CR Number in Backup Table ######
        # Check for Action NOT Required Valid CR Number
        backupTableLine = 'CREATE MULTISET TABLE PDDBABKP.SB_92_1_1_F_LEND_B_1_C1112223 AS P_D_INP_001_STD_0.SB_92_1_1_F_LEND_BALN_MNLY WITH DATA AND STATS;'
        self.assertFalse(action.executeAction(backupTableLine, self._assembledPackage), 'Check for A valid CR NO')

        # Check for Action Required and produce Error if the CR Number (C7777777) is invalid
        backupTableLine = 'CREATE MULTISET TABLE PDDBABKP.SB_92_1_1_F_LEND_B_1_C7777777 AS P_D_INP_001_STD_0.SB_92_1_1_F_LEND_BALN_MNLY WITH DATA AND STATS;'
        self.assertTrue(action.executeAction(backupTableLine, self._assembledPackage), 'Check for A invalid CR NO')

        ###### Check for CR Number in Backup Table Comment ######
        # Check for Action NOT Required Valid CR Number
        backupCommentLine = "COMMENT ON TABLE PDDBABKP.SB_92_1_1_F_LEND_B_1_C1112223 IS 'C1112223:To be dropped on 30-June-2015 - Naga Nandyala. Table origin P_D_INP_001_STD_0.SB_92_1_1_F_LEND_BALN_MNLY';"
        self.assertFalse(action.executeAction(backupCommentLine, self._assembledPackage), 'Check for A valid CR NO')

        # Check for Action Required and produce Error if the CR Number (C7777777) is invalid
        backupCommentLine = "COMMENT ON TABLE PDDBABKP.SB_92_1_1_F_LEND_B_1_C7777777 IS '7777777:To be dropped on 30-June-2015 - Naga Nandyala. Table origin P_D_INP_001_STD_0.SB_92_1_1_F_LEND_BALN_MNLY';"
        self.assertTrue(action.executeAction(backupCommentLine, self._assembledPackage), 'Check for A invalid CR NO')

    def test_executeActionForTeradataKeywords(self):
        action = Action("Check for Teradata keywords", ActionType.ContainsTeradataKeywords.value, "")
        self._assembledPackage._teradataKeywords = ['CREATE','AS']
        dbLine = 'CREATE MULTISET TABLE PDDBABKP.SB_92_1_1_F_LEND_B_1_C1112223 AS P_D_INP_001_STD_0.SB_92_1_1_F_LEND_BALN_MNLY WITH DATA AND STATS;'
        self.assertTrue(action.executeAction(dbLine, self._assembledPackage), 'Check for teradat keywords 1 (QA checks Fail Test)')

        dbLine = "ACCT_IDNN_HK CHAR(32) CHARACTER SET LATIN NOT CASESPECIFIC TITLE 'Account Identifier HK' NOT NULL,"
        self.assertFalse(action.executeAction(dbLine, self._assembledPackage), 'Check for teradat keywords 2 (QA checks Pass Test)')

    def test_executeActionForNoTextMatch(self):
        action = Action("Check for Teradata keywords", ActionType.NoTextMatch.value, "MULTISET")
        dbLine = 'CREATE MULTISET TABLE PDDBABKP.SB_92_1_1_F_LEND_B_1_C1112223 AS P_D_INP_001_STD_0.SB_92_1_1_F_LEND_BALN_MNLY WITH DATA AND STATS;'
        self.assertTrue(action.executeAction(dbLine, self._assembledPackage), 'MULTISET should not existed (QA checks Fail Test)')

        dbLine = "ACCT_IDNN_HK CHAR(32) CHARACTER SET LATIN NOT CASESPECIFIC TITLE 'Account Identifier HK' NOT NULL,"
        self.assertFalse(action.executeAction(dbLine, self._assembledPackage), 'MULTISET should not existed (QA checks Pass Test)')

    def test_executeActionInvalidActionType(self):
        action = Action("Check for Teradata keywords", 'INVALID_ACTION_TYPE', "MULTISET")
        dbLine = 'Testing Invalid ActionType'
        self.assertFalse(action.executeAction(dbLine, self._assembledPackage), 'Testing Invalid ActionType')


if __name__ == "__main__":
    unittest.main()