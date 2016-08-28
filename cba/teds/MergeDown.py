
import cba.teds.utils.Logger
import getopt
import logging
import sys
import time
import os
from datetime import datetime

from junit_xml import TestSuite, TestCase

from cba.teds.utils.StashRepository import StashRepository
from cba.teds.utils.StashRepository import MergeResult


def mergeDown(argv):
    """
    Merge Down (i.e. Merge Source -> Target) from a specified Source Branch to a specified list of Target Branches).
    
    The script will not terminate for a failed merge result (e.g. Conflicts, Existing or Unknown).
    
    Example: python -m cba.teds.MergeDown -p GDW -r test_gdw2 -t GLAS_PRVN_2.7,BICD_PRVN_6.0 -s master -U teradata-ci -P ????
    """

    # Initialize Logging
    logger = cba.teds.utils.Logger.getLogger()

    logger.debug("Start MergeDown(%s) - %s", argv, datetime.now().strftime("%Y%m%d%H%M"))

    project = ""
    repo = ""
    targets = []
    source = ""
    user = ""
    password = ""

    try:
        opts, args = getopt.getopt(argv, "p:r:t:s:U:P:dh", ["project=", "repo=", "targets=", "source=", "user=", "password=", "debug", "help"])
    except getopt.GetoptError as e:
        print(e)
        print("cba.teds.mergedown -p <project> -r <repo> -t <targets> -s <source> -U <user> -P <password> [-debug]")
        sys.exit(2)

    for arg in args:
        if arg in ("d", "debug"):
            logger.setLevel(logging.DEBUG)
            
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print("usage: cba.teds.mergedown -p <project> -r <repo> -t <targets> -s <source> -U <user> -P <password> [-debug]")
            sys.exit()
        elif opt in ("-p", "--project"):
            project = arg
        elif opt in ("-r", "--repo"):
            repo = arg
        elif opt in ("-s", "--source"):
            source = arg
        elif opt in ("-t", "--targets"):
            targets = arg.split(",")
        elif opt in ("-U", "--user"):
            user = arg
        elif opt in ("-P", "--password"):
            password = arg

    if project != "" and repo != "" and source != "" and targets != [] and user != "" and password != "":

        stashRepository = StashRepository(user, password, project, repo)

        if len(targets) == 1 and targets[0] == "*":
            targets = stashRepository.getBranchNames()

        testSuite = TestSuite("Merge Down")

        for target in targets:
            if target != source:
                start = time.clock()
                mergeResult = stashRepository.mergeBranches(source, target)
                end = time.clock()
                executionTime = (end - start)
                appendMergeDownResult(mergeResult, testSuite, source, target, executionTime)

                # NOTE (06.05.2015): Gogul indicated that he would want it to continue (and report failures at the end)
                # if (mergeResult != MergeResult.Merged and mergeResult != MergeResult.Unnecessary):
                    # break

        if not os.path.exists("output"):
            os.makedirs("output")

        with open("output/MergeDownReport.xml", 'w') as reportFile:
            TestSuite.to_file(reportFile, [testSuite])

    else:
        print("cba.teds.mergedown -p <project> -r <repo> -t <targets> -s <source> [-debug]")
        sys.exit(2)

    logger.debug("End MergeDown - %s", datetime.now().strftime("%Y%m%d%H%M"))


def appendMergeDownResult(mergeResult, testSuite, source, target, executionTime ):
    if (mergeResult == MergeResult.Merged): 
        testSuite.test_cases.append(TestCase("Merge Down from %s to %s was successful." % (source, target), None, executionTime))
    elif (mergeResult == MergeResult.Unnecessary):
        testSuite.test_cases.append(TestCase("Merge Down from %s to %s is unnecessary." % (source, target), None, executionTime))
    else:
        testCase = TestCase("Merge Down from %s to %s failed (%s)." % (source, target, mergeResult.name), None, executionTime)
        testCase.add_failure_info(mergeResult.name, mergeResult.value)
        testSuite.test_cases.append(testCase)


if __name__ == "__main__":
    mergeDown(sys.argv[1:])  