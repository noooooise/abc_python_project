
import cba.teds.utils.Logger
import os
import shutil
import tarfile

from cba.teds.teradata.qa.artifacts.TeradataArtifacts import TeradataArtifacts
from tarfile import TarFile


class AssembledBTEQ(TeradataArtifacts):
    """
        DEPRECATED: AssembledBTEQ is implements the TeradataArtifacts abstract class  for an Assembled BTEQ.

        This was part of our original design but was replaced with the AssembledPackage implementation. It works by
        extracting the specified assembled_bteqs.tgz to a specified directory and then identifying constituent files
        to support the interface defined in TeradataArtifacts.
    """

    def __init__(self, packageDirectory, packageFilename, extractionDirectory = None):
        """
        Constructor.

        :param packageDirectory: The relative (project root) path to the directory containing the Assembled BTEQ.
        :param packageFilename: The file name of the Assembled BTEQ.
        :param extractionDirectory: The directory where Assembled_bteq is extracted
        """

        # Initialize Logging
        self.logger = cba.teds.utils.Logger.getLogger()

        self.logger.debug("Call: AssembledBTEQ(%s, %s, %s)", packageDirectory, packageFilename, extractionDirectory)

        # Copy Parameters to Local Variables
        self._packageDirectory = packageDirectory
        self._packagedFileName = packageFilename
        self._extractionDirectory = (extractionDirectory if extractionDirectory else 'defaultExtractDir')

        self._assembledBTEQFilesList = []
        self._extractDirFolderList = []
        self._tableDirList = []
        self._createTableBteqFiles = []
        self._deleteFlag = True

        # extract tar file
        self._extractFile()
        tmpOsWalk = os.walk(self._getExtractFileAbsolutePath(), topdown=True)
        for root, dirs, fileNames in tmpOsWalk:
            self._getExtractFileAbsolutePath()
            #
            for fileName in fileNames:
                filePath = os.path.join(root, fileName)
                # Standardise Slashes Up Front for extractObjectNameFromFilePath()
                filePath = filePath.replace("\\", "/")
                self._assembledBTEQFilesList.append(filePath)


    def __del__(self):
        """
        Destructor. Ensures that AssembledBTEQ objects don't leave a footprint. Deletes the extracted files.
        """
        self.logger.debug("Destroy: AssembledBTEQ()")
        if self._isExtractFilePathExist() and self._deleteFlag == True :
            self._deleteExtractedFiles()

    def extractedFilesDirectory(self):
        self.logger.debug("Call: extractedFilesDirectory()")
        return os.path.abspath(self._extractedFilesRelativeDirectory())

    # PRIVATE METHODS #

    def _extractedFilesRelativeDirectory(self):
        return self._packageDirectory + "/" + self._extractionDirectory + "/"

    def _getExtractFileAbsolutePath(self):
        tmpFilePath = os.path.abspath(self._packageDirectory + '/' + self._extractionDirectory)
        return tmpFilePath

    def _deleteExtractedFiles(self):

        if (os.path.exists(self.extractedFilesDirectory())):
            try:
                shutil.rmtree(self.extractedFilesDirectory())
                self.logger.info("Extracted Package Deleted from '%s'", self.extractedFilesDirectory())
            except OSError as osError:
                self.logger.error("Extracted directory cannot be deleted : %s", self._extractedFilesRelativeDirectory())
                self.logger.error(osError)

    def _isExtractFilePathExist(self):
        return os.path.exists(self._getExtractFileAbsolutePath())

    def _extractFile(self, extractDir=None):
        if extractDir:
            self._extractionDirectory = extractDir
        packagedFilePath = os.path.abspath(self._packageDirectory + '/' + self._packagedFileName)
        isValidTar = False

        try:
            isValidTar = tarfile.is_tarfile(packagedFilePath)
        except FileNotFoundError as fnfe:
            self.logger.warning(
                "ReleasePackage.extractFile  Tar File not found (%s). Trying to look up the file in upper directory",
                (packagedFilePath))

        if isValidTar:
            tmpTar = TarFile.open(packagedFilePath, mode="r")
            tmpTar.extractall(self._getExtractFileAbsolutePath())
            print('extractAll')
        else:
            self.logger.warning(' WARNING : NOT A VALID TAR')
        return isValidTar


    def retrieveAssembledBTEQFilesList(self):
        """
        Find list of all BTEQs
        :returns: list of files under assembled bteq
        """


        return self._assembledBTEQFilesList

