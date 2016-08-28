
import cba.teds.utils.Logger
import datetime
import os
import re
import shutil
import tarfile
import time

from cba.teds.teradata.qa.artifacts.TeradataArtifacts import TeradataArtifacts
from cba.teds.teradata.qa.rules.RuleRunner import RuleRunner
from tarfile import TarFile


def extractObjectNameFromFilePath(filePath):
    """
        Helper function to extract the file name component from a file path.

        :param filePath: The entire path (e.g. resources/test//EXTRACTED_FILES_20150528145843/TERADATA\\P_D_BAL_001\\P_D_BAL_001_STD_0\\P_D_BAL_001_STD_0.FACT_ACCT_BALN_MNLY.tbl)
        :returns fileName: The file name (e.g. P_D_BAL_001_STD_0.FACT_ACCT_BALN_MNLY.tbl)
    """
    objectNameStartIndex = filePath.rfind("/")
    objectNameEndIndex = filePath.rfind(".")
    fileName = filePath[objectNameStartIndex+1:objectNameEndIndex]

    return fileName


class AssembledPackage(TeradataArtifacts):
    """
        AssembledPackage implements the TeradataArtifacts abstract class for an Assembled Package.

        It works by extracting the specified assembled_package.tgz to a specified directory and then identifying
        constituent files to support the interface defined in TeradataArtifacts.
    """

    def __init__(self, packageDirectory, packageFileName, extractionDirectory=None):
        """
        Constructor. Everything happens in the Constructor. The Package is extracted and the extracted files are
        walked to set up everything that is exposed via the public interface.

        :param packageDirectory: The relative (project root) path to the directory containing the Assembled Package.
        :param packageFileName: The file name of the Assembled Package.
        """

        # Initialize Logging
        self.logger = cba.teds.utils.Logger.getLogger()

        # Always Log (Debug) Constructors, Destructors and Public Methods
        self.logger.debug("Create: AssembledPackage(%s, %s)", packageDirectory, packageFileName)

        # Copy Parameters to Local Variables
        self._packageDirectory = packageDirectory
        self._packageFileName = packageFileName

        # Create a unique Directory Name to Extract To
        if extractionDirectory is None:
            rightNow = time.time()
            timestampString = datetime.datetime.fromtimestamp(rightNow).strftime("%Y%m%d%H%M%S")
            self._extractionDirectory = "EXTRACTED_FILES_" + timestampString

            # Extract the Package (Can Throw an Exception)
            self._packageExtracted = self._extractFiles()
            if self._packageExtracted == False:
                raise ValueError("Error Extracting Assembled Package: %s" % self.name())
        else:
            self._packageExtracted = False
            self._extractionDirectory = extractionDirectory

        # Walk the Extracted Files and Store all the File Names
        self._assembledPackageFilesList = []
        for root, directoryNames, fileNames in os.walk(self._extractedFilesRelativeDirectory(), topdown=True):
            for fileName in fileNames:
                filePath = os.path.join(root, fileName)
                # Standardise Slashes Up Front for extractObjectNameFromFilePath()
                filePath = filePath.replace("\\", "/")
                self._assembledPackageFilesList.append(filePath)

        # Initialise the Local Variables
        self._changeRequestNumber = None

        self._createdObjects = None
        self._deletedObjects = None
        self._rolledBackObjects = None

        self._teradataKeywords = None

    def __del__(self):
        """
        Destructor. Ensures that AssembledPackage objects don"t leave a footprint. Deletes the extracted files.
        """
        self.logger.debug("Destroy: AssembledPackage()")
        if self._packageExtracted == True:
            self._deleteExtractedFiles()

    # PUBLIC METHODS #

    def retrieveAssembledPackageFilesList(self):
        self.logger.debug("Call: retrieveAssembledPackageFilesList()")
        return self._assembledPackageFilesList

    def name(self):
        self.logger.debug("Call: name()")
        return self._packageFileName

    def extractedFilesDirectory(self):
        self.logger.debug("Call: extractedFilesDirectory()")
        return os.path.abspath(self._extractedFilesRelativeDirectory())

    def retrieveChangeRequestNumber(self):
        self.logger.debug("Call: retrieveChangeRequestNumber()")

        if self._changeRequestNumber == None:

            for filePath in self._assembledPackageFilesList:
                if filePath.find("Version.txt") > -1:
                    file = open(filePath)
                    for line in file:
                        if line.find("CR_NUMBER:") > -1:
                            line = line.rstrip().lstrip()
                            startIndex = line.find("CR_NUMBER:")
                            self._changeRequestNumber = line[startIndex + 10:].rstrip().lstrip()

        return self._changeRequestNumber

    def retrieveTeradataKeywords(self):
        """
            This public interface retrieve all the teradata keywords from 'resources/Teradata_Reserved_Words.csv'
        """
        self.logger.debug("Call: retrieveTeradataKeywords()")
        if self._teradataKeywords == None:
            self._teradataKeywords = []
            filePath = 'resources/Teradata_Reserved_Words.csv'
            file = open(filePath)
            try:
                for line in file:
                    tmpLine = line.rstrip() # remove new line character
                    tmpLine += ' '
                    self._teradataKeywords.append(tmpLine)
            except Exception as exception:
                self.logger.error("AssembledPackage.retrieveTeradataKeywords() ERROR IN READING FILE(%s)" % filePath)
                self.logger.error(exception)
            file.close()

        return self._teradataKeywords

    def runChecks(self, rulesFileName = 'resources/teradataQualityCheckRules.xml', junitFileName = 'output/junit-GeneratedFromRuleRunner.xml'):
        self.logger.debug("Call: runChecks(rulesFileName = %s, junitFileName = %s)" % (rulesFileName, junitFileName))

        self._ruleRunner = RuleRunner(rulesFileName, self)
        self._ruleRunner.runRules()
        self._ruleRunner.generateReport(junitFileName)

    def retrieveCreatedObjects(self):
        """
        Returns a list of Object Names (String) for all created objects.
        """

        self.logger.debug("Call: retrieveCreatedObjects()")

        if self._createdObjects == None:

            self._createdObjects = set()

            for filePath in self._assembledPackageFilesList:
                if filePath.endswith(".tbl"):
                    objectName = extractObjectNameFromFilePath(filePath)
                    self._createdObjects.add(objectName)

            for filePath in self._assembledPackageFilesList:
                if filePath.endswith(".viw"):
                    self._createdObjects.add(extractObjectNameFromFilePath(filePath))

        return self._createdObjects

    def retrieveDeletedObjects(self):
        """
        Returns a list of Object Names (String) for all deleted (decommissioned) objects.
        """

        self.logger.debug("Call: retrieveDeletedObjects()")

        if self._deletedObjects == None:

            self._deletedObjects = set()

            for filePath in self._assembledPackageFilesList:
                if filePath.find("_Drop_Tables.sql") != -1:
                    file = open(filePath)
                    for line in file:
                        match = re.search("DROP TABLE (.*);", line)
                        if match:
                            objectName = match.groups()[0]
                            self._deletedObjects.add(objectName)
                    file.close()

            for filePath in self._assembledPackageFilesList:
                if filePath.find("_Drop_Views.sql") != -1:
                    file = open(filePath)
                    for line in file:
                        match = re.search("DROP VIEW (.*);", line)
                        if match:
                            objectName = match.groups()[0]
                            self._deletedObjects.add(objectName)
                    file.close()

        return self._deletedObjects

    def retrieveRolledBackObjects(self):
        """
        Returns a list of Object Names (String) for all rolled-back objects.
        """

        self.logger.debug("Call: retrieveRolledBackObjects()")

        if self._rolledBackObjects == None:

            self._rolledBackObjects = set()

            for filePath in self._assembledPackageFilesList:
                if filePath.find("Rollback_Drop_Tables.sql") != -1:
                    file = open(filePath)
                    for line in file:
                        match = re.search("DROP TABLE (.*);", line)
                        if match:
                            objectName = match.groups()[0]
                            self._rolledBackObjects.add(objectName)
                    file.close()

            for filePath in self._assembledPackageFilesList:
                if filePath.find("Rollback_Drop_Views.sql") != -1:
                    file = open(filePath)
                    for line in file:
                        match = re.search("DROP VIEW (.*);", line)
                        if match:
                            objectName = match.groups()[0]
                            self._rolledBackObjects.add(objectName)
                    file.close()

            for filePath in self._assembledPackageFilesList:
                if filePath.find("_Backup_Views.sql") != -1:
                    file = open(filePath)
                    for line in file:
                        match = re.search("SHOW VIEW (.*);", line)
                        if match:
                            objectName = match.groups()[0]
                            self._rolledBackObjects.add(objectName)
                    file.close()

        return self._rolledBackObjects

    # PRIVATE METHODS #

    def _extractedFilesRelativeDirectory(self):
        return self._packageDirectory + "/" + self._extractionDirectory + "/"

    def _packagePath(self):
        return os.path.abspath(self._packageDirectory + "/" + self._packageFileName)

    def _extractFiles(self):

        extractionOK = False

        try:
            extractionOK = tarfile.is_tarfile(self._packagePath())
            tarFile = TarFile.open(self._packagePath(), mode="r")
            tarFile.extractall(self.extractedFilesDirectory())
            self.logger.info("Package Extracted to '%s'", self.extractedFilesDirectory())

        except FileNotFoundError as fileNotFoundError:
            self.logger.error("Package Not Found (Check Working Directory): %s", self._packagePath())

        return extractionOK

    def _deleteExtractedFiles(self):

        if (os.path.exists(self.extractedFilesDirectory())):
            try:
                shutil.rmtree(self.extractedFilesDirectory())
                self.logger.info("Extracted Package Deleted from '%s'", self.extractedFilesDirectory())
            except OSError as osError:
                self.logger.error("Extracted directory cannot be deleted : %s", self._extractedFilesRelativeDirectory())
                self.logger.error(osError)


