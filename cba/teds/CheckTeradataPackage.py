from cba.teds.utils.Logger import getLogger
import getopt
import logging
import sys
import time

from cba.teds.teradata.qa.artifacts.AssembledBTEQ import *
from cba.teds.teradata.qa.artifacts.AssembledPackage import *

from datetime import datetime
from junit_xml import TestSuite


def checkTeradataPackage(argv):
    """
    Check the specified Teradata Package.

    Example : python -m cba.teds.CheckTeradataPackage -q "D:\Documents and Settings\JoyGa\PycharmProjects\python_core\resources\teradataQualityCheckRules.xml" -r "resources/test/" -t test_assembled_package.tgz -o unitTestResources_assembled_bteqs -p junit-QACheck.xml -e Y
    python -m cba.teds.CheckTeradataPackage -q "D:\Apps\python_core\resources\teradataQualityCheckRules.xml" -r "D:\Apps\python_core\output" -t assembled_bteqs.tgz -o unitTestResources_assembled_bteqs -p junit-QACheck.xml
    """

    # Initialize Logging
    logger = getLogger()

    logger.debug("Start TeradataQualityCheck(%s) - %s", argv, datetime.now().strftime("%Y%m%d%H%M"))

    rootDirectoryPath = ''
    outputDir = ''
    printToJunitReport = ''
    tarName = ''
    extractFlag = ''
    teradataQualityCheckRuleFile = ''

    try:
        opts, args = getopt.getopt(argv, "q:r:t:o:p:e:dh",
                                   ["teradataQualityCheckRuleFile=", "rootDirectoryPath=", "tarName=", "outputDir=",
                                    "extractFlag=", "printToJunitReport=", "debug"])
    except getopt.GetoptError as e:
        print(e)
        print(
            "  cba.teds.TeradataQualityCheck -q <qaRuleFilePath> -r <rootDirectoryPath> -t <tarName> -o <outputDir> -p <junit-output.xml> -e <Y|N>")
        sys.exit(2)

    if ( len(opts) == 0):
        print(
            "  (Please specify arguments) cba.teds.TeradataQualityCheck -q <qaRuleFilePath> -r <rootDirectoryPath> -t <tarName> -o <outputDir>  -p <junit-output.xml> -e <Y|N>")
        sys.exit()

    for arg in args:
        if arg in ("d", "debug"):
            print(" DEBUGGING ENABLE")
            logger.setLevel(logging.DEBUG)

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print(
                "  HELP cba.teds.TeradataQualityCheck -q <qaRuleFilePath> -d <rootDirectoryPath> -t <tarName> -o <outputDir>  -p <junit-output.xml> -e <Y|N>")
            sys.exit()
        elif opt in ("-q", "--teradataQualityCheckRuleFile"):
            teradataQualityCheckRuleFile = arg
            logger.info(" teradataQualityCheckRuleFile = %s" % (teradataQualityCheckRuleFile))
        elif opt in ("-r", "--rootDirectoryPath"):
            rootDirectoryPath = arg
            logger.info(" Directory PATH = %s" % (rootDirectoryPath))
        elif opt in ("-o", "--outputDir"):
            outputDir = arg
            logger.info(" OutputDir name = %s" % (outputDir))
        elif opt in ("-t", "--tarName"):
            tarName = arg
            logger.info(" Tar Name       = %s" % (tarName))
        elif opt in ("-p", "--printToJunitReport"):
            printToJunitReport = arg
            logger.info(" JUNIT File     = %s" % (printToJunitReport))
        elif opt in ("-e", "--extractFlag"):
            extractFlag = arg
            logger.info(" extractFlag    = %s" % (extractFlag))

    start = time.clock()

    fileList = None
    name = None
    if ( tarName.find('assembled_bteqs') > -1 ):
        extractReleasePackage = AssembledBTEQ(rootDirectoryPath, tarName, outputDir)
        if ( extractFlag == 'Y' or extractFlag == 'True' or extractFlag == 'T'):
            logger.info(" Extracting file to dir : %s/%s" % (rootDirectoryPath, outputDir))
            extractReleasePackage._extractFile()

        extractReleasePackage._findAllExtractedDir()
        fileList = extractReleasePackage.retrieveCreateTableFiles()
        name='Table Check Bteq'
        # with open(printToJunitReport, 'w') as f:
        #    TestSuite.to_file(f, [tableChecks.retrieveCreateTableTestSuite()], prettyprint=False)

    elif ( tarName.find('assembled_package') > -1 ):

        assembledPackage = AssembledPackage(rootDirectoryPath, tarName)
        assembledPackage.runChecks(teradataQualityCheckRuleFile, printToJunitReport)


    end = time.clock()
    executionTime = (end - start)
    print(' Execution Time ', executionTime)


if __name__ == '__main__':
    checkTeradataPackage(sys.argv[1:])