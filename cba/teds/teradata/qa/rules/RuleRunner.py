import re
from junit_xml import TestSuite, TestCase
from cba.teds.teradata.qa.rules.RuleReader import RuleReader
from cba.teds.teradata.qa.rules.Rule import *

class RuleRunner(object):
    """
    The RuleRunner class was designed to be used by a Artifacts implementation class (e.g. AssembledPackage) to run
    a series of checks (Rules) against a set of Artifacts.

    Usage:

    1.  Constructor - Reads, Parses and Processes the Rules File. Collects (in one pass) all required data from the
                      Artifacts.

    2.  runRules() - Evaluates the Rules against the Artifact Data. Collects the Results.

    3.  generateReport() - Generates an XML (JUnit) Report for the Results.

    NOTE:  The XML output is transformed (by TeamCity) using resources/teradataQualityCheckTransform.xsl.
    NOTE:  Maps/Sets are used to help optimise the implementation.
    NOTE:  There are a couple of hard-coded rules (i.e. _runObjectCountRules() and _recordChangeNumber()).
    """

    def __init__(self, rulesFile, assembledPackage = None):

        # Initialize Logging
        self.logger = cba.teds.utils.Logger.getLogger()

        # Always Log (Debug) Constructors, Destructors and Public Methods
        self.logger.debug("Create: RuleRunner(%s, %s)", rulesFile, assembledPackage)

        # e.g. rulesFile = "resources/newTeradataQualityCheckRules.xml"
        ruleReader = RuleReader(rulesFile)

        self._assembledPackage = assembledPackage

        self._whens = ruleReader.retrieveListOfWhenConditions()
        self._actions = ruleReader.retrieveListOfActions()
        self._rules = ruleReader.retrieveListOfRules()

        self._testCases = {} # map keyed on artifact name

        self._filterMaps = {}
        self._scopeMaps = {}

        # Build When Maps (scopeMaps and filterMaps)
        self._buildWhenMaps()

        # Collect when data from the assembledPackage if when condition is matched
        self._buildWhenDataFromAssembledPackage(assembledPackage)

    # PUBLIC METHODS

    def runRules(self):
        """
            This is public interface. This function run the checks by looping over the rules
            Get the when object from each rule and loop over the when data
            Evaluate Action based on the action attached to each rule and generate the test case
            All the test cases are grouped by the artifact name
        """

        self.logger.debug("Create: RuleRunner.runRules")

        # Explicit (Hard-Coded) Rules
        self._runObjectCountRules()
        self._recordChangeNumber()

        # Rules from XML File
        for rule in self._rules:
            message = rule.message
            level = rule.level

            for whenData in rule.when.data:
                artifactName = whenData.artifactName

                """
                    Make the artifact name shorter e.g
                        From : resources/test//EXTRACTED_FILES_20150526161812/TERADATA\P_D_BAL_001\P_D_BAL_001_STD_0\P_D_BAL_001_STD_0.FACT_LEND_PAL_MNLY.tbl
                        TO   : \P_D_TXM_001\P_D_INP_001_STD_0\P_D_INP_001_STD_0.SB_69_1_1_F_CARD_BALN_MNLY.tbl
                """
                teradataDirectoryIndex = artifactName.find("TERADATA")
                if teradataDirectoryIndex > -1:
                    artifactName = artifactName[teradataDirectoryIndex-1:]

                dbaiDirectoryIndex = artifactName.find("DBAI")
                if dbaiDirectoryIndex > -1:
                    artifactName = artifactName[dbaiDirectoryIndex-1:]

                testCase = self._retrieveTestCase(artifactName)

                # Execute action
                actionRequired = rule.action.executeAction(whenData.data, self._assembledPackage)
                if actionRequired:
                    self._recordTestResult(testCase, message, level)

    def generateReport(self, junitFileName):
        """
        This is the public interface to generate the Junit Report for the Teradata Quality Checks
        :param junitFileName: the file path of the junit file
        :return:
        """

        self.logger.debug("Create: RuleRunner.generateReport (%s)" % junitFileName)

        testSuite = TestSuite("Teradata Package Check")
        for testCaseName in self._testCases:
            testCase = self._testCases.get(testCaseName)
            testSuite.test_cases.append(testCase)

        with open(junitFileName, "w") as reportFile:
            TestSuite.to_file(reportFile, [testSuite])
        reportFile.close()

    # PRIVATE METHODS

    def _recordChangeNumber(self):
        crNumber = self._assembledPackage.retrieveChangeRequestNumber()
        testCase = self._retrieveTestCase(".Change Record Number")
        informationMessage = "The Change Record Number is: %s" % crNumber
        patternMatchForChangeNumber = 'C\d{7}'
        if re.search(patternMatchForChangeNumber, crNumber) is None:
            self._recordTestResult(testCase, informationMessage, RuleLevel.Warning.value)
        else:
            self._recordTestResult(testCase, informationMessage, RuleLevel.Information.value)

    def _runObjectCountRules(self):

        createdObjects = self._assembledPackage.retrieveCreatedObjects()
        deletedObjects = self._assembledPackage.retrieveDeletedObjects()
        rolledBackObjects = self._assembledPackage.retrieveRolledBackObjects()

        # This code is LEGEND... ... ... ... ...
        createdButNotRolledBack = createdObjects - rolledBackObjects
        createdAndRolledBack = createdObjects & rolledBackObjects
        deletedButNotRolledBack = deletedObjects - rolledBackObjects
        deletedAndRolledBack = deletedObjects & rolledBackObjects
        createdAndDeleted = createdObjects | deletedObjects
        notCreatedOrDeletedButRolledBack = rolledBackObjects - createdAndDeleted
        # ... ... ... ... ...  ARY!

        # The . is to ensure that this test case is at the top of the list
        testCase = self._retrieveTestCase(".Object Counts")
        if len(createdButNotRolledBack) > 0:
            errorMessage = "These objects are created but not rolled back: \n%s" % createdButNotRolledBack
            self._recordTestResult(testCase, errorMessage, RuleLevel.Error.value)
        if len(createdAndRolledBack) > 0:
            errorMessage = "These objects are created and rolled back: \n%s" % createdAndRolledBack
            self._recordTestResult(testCase, errorMessage, RuleLevel.Information.value)
        if len(deletedButNotRolledBack) > 0:
            errorMessage = "These objects are deleted but not rolled back: \n%s" % deletedButNotRolledBack
            self._recordTestResult(testCase, errorMessage, RuleLevel.Error.value)
        if len(deletedAndRolledBack) > 0:
            errorMessage = "These objects are deleted and rolled back: \n%s" % deletedAndRolledBack
            self._recordTestResult(testCase, errorMessage, RuleLevel.Information.value)
        if len(notCreatedOrDeletedButRolledBack) > 0:
            errorMessage = "These objects are not created or deleted but are rolled back: \n%s" % notCreatedOrDeletedButRolledBack
            self._recordTestResult(testCase, errorMessage, RuleLevel.Error.value)

    def _buildWhenMaps(self):
        """
            This function builds two when Maps
            - filterMap is a map of when maps (Outer Map is grouped by the same filter type)
            - scopeMap is a map of when maps (Outer Map is grouped by the same scope type)
        """
        self.logger.debug("Create: RuleRunner._buildWhenMaps")
        for whenKey in self._whens:
            # Build a map of when maps (FILTER type is used as a key on outer map)
            self._buildFilterMap(whenKey)

            # Build a map of when maps (SCOPE type is used as a key on outer map)
            self._buildScopeMap(whenKey)

    def _buildScopeMap(self, whenKey):
        """
            This function builds scopeMaps (on when objects) Inner map is a map of WHEN objects
            - scopeMap is a map of when maps (Outer Map is grouped by the same scope type)
        """
        self.logger.debug("Create: RuleRunner._buildScopeMap")
        scope = self._whens[whenKey].scope
        scopeMap = self._scopeMaps.get(scope)
        # Create a scope map if there is none in "self._scopeMaps"
        if scopeMap is None:
            scopeMap = {}
            self._scopeMaps[scope] = scopeMap

        # Add when to scopeMap (inner) map
        scopeMap[whenKey] = self._whens[whenKey]

    def _buildFilterMap(self, whenKey):
        """
            This function builds filterMaps (on when objects) Inner map is a map of WHEN objects
            - filterMap is a map of when maps (Outer Map is grouped by the same filter type)
        """
        self.logger.debug("Create: RuleRunner._buildFilterMap")

        filter = self._whens[whenKey].filter
        filterMap = self._filterMaps.get(filter)
        # Create a filter map if there is none in "self._filterMaps"
        if filterMap is None:
            filterMap = {}
            self._filterMaps[filter] = filterMap

        # Add when to filterMap (inner) map
        filterMap[whenKey] = self._whens[whenKey]

    def _buildWhenDataFromAssembledPackage(self, assembledPackage):
        """
            This function will scan all the files from the assembledPackage
            and populate when data (if when condition is matched)
        :param assembledPackage:
        :return:
        """
        self.logger.debug("Create: RuleRunner._buildWhenDataFromAssembledPackage")

        fileList = assembledPackage.retrieveAssembledPackageFilesList()
        for filePath in fileList:

            ## setup for ALL files
            allFillterWhenMap = self._filterMaps.get("ALL")
            for allWhenName in allFillterWhenMap:
                self._buildWhenData(filePath, allFillterWhenMap.get(allWhenName))


            # we need to know if we care about file
            # looping through every files and retrieve a list of filterType(s) of each file
            filterTypes = self._retrieveFilterTypesForArtifact(filePath)

            for filterType in filterTypes:
                filterWhenMap = self._filterMaps.get(filterType.value) # Get a list of WhenMap for a particular filter type (e.g CREATE_TABLE filter)
                if filterWhenMap:
                    for whenName in filterWhenMap:
                        self._buildWhenData(filePath, filterWhenMap.get(whenName))
                else:
                    self.logger.warn("Invalid Filter Type : ", filterType.value)

    def _buildWhenData(self, filePath, when):
        """
            This function build the "when data" if the content of the file match When condition
        :param filePath:
        :param when:
        :return:
        """
        self.logger.debug("Create: RuleRunner._buildWhenData")
        # If the file extension is zip or tar file, we do not need to collect the when data
        if filePath.endswith(".gz") or filePath.endswith(".tar"):
            return

        if when.scope == WhenScope.Line.value :
            # Logic to collect when data for "LINE" scope
            file = None
            try:
                file = open(filePath)
                for line in file:
                    if when.isConditionMatched(line) == True :
                        when.data.append(WhenData(filePath,line))
            except Exception as exception:
                self.logger.error("ERROR IN READING FILE for WhenScope.Line : (%s)" % filePath)
                self.logger.error(exception)
            if file :
                file.close()
        elif when.scope == WhenScope.Script.value:
            # Logic to collect when data for "SCRIPT" scope
            file = None

            whenData = ""
            isWhenConditionMatch = False
            try:
                file = open(filePath)
                for line in file:
                    if when.isConditionMatched(line) == True :
                        isWhenConditionMatch = True
                    whenData += line
            except Exception as exception:
                self.logger.error("ERROR IN READING FILE for WhenScope.Script : (%s)" % filePath)
                self.logger.error(exception)
            if file :
                file.close()

            # if when condition is matched, the entire content of the script will be stored in the whenData
            if isWhenConditionMatch == True:
                when.data.append(WhenData(filePath,whenData))
        elif when.scope == WhenScope.FilePath.value:
            if when.isConditionMatched(filePath) == True :
                when.data.append(WhenData(filePath,filePath))

    def _retrieveFilterTypesForArtifact(self, artifactName):
        """
        This function will retrieve a list of Filter Types (WhenFilter) for a specified Artifact

        :param artifactName:  The Artifact Name (i.e. a File Path for Assembled Package Checks).
        :return:  A List of Filer Types (WhenFilter).
        """

        filterTypes = []

        if artifactName.endswith(".tbl"):
            filterTypes.append(WhenFilter.CreateTable)
        elif artifactName.endswith(".viw"):
            filterTypes.append(WhenFilter.CreateView)
        elif artifactName.endswith(".cmt"):
            filterTypes.append(WhenFilter.CreateComment)

        if artifactName.find("Auto_Backup_Tables") > -1:
            filterTypes.append(WhenFilter.CreateBackupTable)
        elif artifactName.find("Auto_Backup_Views") > -1:
            filterTypes.append(WhenFilter.CreateBackupView)

        return filterTypes

    def _retrieveTestCase(self, artifactName):
        """
        Retrieve a Test Case for a specified Artifact.

        We group our checks by artifact and we use a map (self._testCases) to store them all. This method is lazy i.e.
        it will first try and get a Test Case from the map and then (if it can't find one) it will create one.

        :param artifactName: An Artifact Name (e.g filePath in the assembledPackage) as a String.
        :return:  A Test Case.
        """

        testCase = self._testCases.get(artifactName)

        if testCase == None:
            testCase = TestCase(artifactName, artifactName)
            self._testCases[artifactName] = testCase

        return testCase

    def _recordTestResult(self, testCase, result, level):

        if level == RuleLevel.Error.value :
           self._recordTestFail(testCase, result)
        elif level == RuleLevel.Warning.value:
            self._recordTestWarning(testCase, result)
        elif level == RuleLevel.Information.value:
            self._recordTestInformation(testCase, result)

    def _recordTestFail(self, testCase, failureMessage):
        """
        Record (in the Test Case) a Test Failure.

        (Our World -> Test Case World)
        Failure -> Failure
        Warning -> Error
        Information ->  StdOut

        :param testCase: Test Case Object.
        :param failureMessage: A String that describes the Failure.  
        """

        # Append failure messages if necessary
        if testCase.failure_message:
            failureMessage = ("%s _BR_ %s" % (testCase.failure_message, failureMessage) )

        # This will replace any existing failure messages
        testCase.add_failure_info(failureMessage)

    def _recordTestWarning(self, testCase, warningMessage):
        """
        Record (in the Test Case) a Test Warning.

        (Our World -> Test Case World)
        Failure -> Failure
        Warning -> Error
        Information ->  StdOut

        :param testCase: Test Case Object.
        :param warningMessage: A String that describes the Warning.
        """

        # Append warning messages if necessary
        if testCase.error_message:
            warningMessage = ("%s _BR_ %s" % (testCase.error_message, warningMessage) )

        # This will replace any existing warning messages
        testCase.add_error_info(warningMessage)

    def _recordTestInformation(self, testCase, informationMessage):
        """
        Record (in the Test Case) some Test Information.

        (Our World -> Test Case World)
        Failure -> Failure
        Warning -> Error
        Information ->  StdOut

        :param testCase: Test Case Object.
        :param informationMessage: A String that describes the Information.
        """

        # Append information messages if necessary
        if testCase.stdout:
            informationMessage = ("%s _BR_ %s" % (testCase.stdout, informationMessage) )

        # This will replace any existing information messages
        testCase.stdout = informationMessage

