
import cba.teds.utils.Logger
import getopt
import logging
import sys
import time
import os

from cba.teds.utils.StashRepository import StashRepository
from cba.teds.utils.StashRepository import MergeResult
from cba.teds.MergeDown import appendMergeDownResult
from datetime import datetime
from junit_xml import TestSuite, TestCase


def mergeUp(argv):
    """
    Merge Up (i.e. Merge Target -> Source and then Source -> Target) a specified list of Source Branches into a specified Target Branch.
    
    The script will terminate if a merge result is Conflicts, Existing, Unnecessary or Unknown (non-terminating result is Merged).
    
    Example: python -m cba.teds.MergeUp -p GDW -r test_gdw2 -t master -s GLAS_DA_2.103,BICD_PRVN_6.0,GLAS_PRVN_2.7 -U teradata-ci -P Passw0rd!
    """

    # Initialize Logging
    logger = cba.teds.utils.Logger.getLogger()

    logger.debug("Start MergeUp(%s) - %s", argv, datetime.now().strftime("%Y%m%d%H%M"))

    project = ""
    repo = ""
    sources = []
    target = ""
    user = ""
    password = ""

    try:
        opts, args = getopt.getopt(argv, "p:r:t:s:U:P:dh", ["project=", "repo=", "target=", "sources=", "user=", "password=", "debug", "help"])
    except getopt.GetoptError as e:
        print(e)
        print("cba.teds.MergeUp -p <project> -r <repo> -t <target> -s <sources> -U <user> -P <password> [-debug]")
        sys.exit(2)

    for arg in args:
        if arg in ("d", "debug"):
            logger.setLevel(logging.DEBUG)
            
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print("usage: cba.teds.MergeUp -p <project> -r <repo> -t <target> -s <sources> -U <user> -P <password> [-debug]")
            sys.exit()
        elif opt in ("-p", "--project"):
            project = arg
        elif opt in ("-r", "--repo"):
            repo = arg
        elif opt in ("-t", "--target"):
            target = arg
        elif opt in ("-s", "--sources"):
            sources = arg.split(",")
        elif opt in ("-U", "--user"):
            user = arg
        elif opt in ("-P", "--password"):
            password = arg

    if project != "" and repo != "" and sources != [] and target != "" and user != "" and password != "":

        stashRepository = StashRepository(user, password, project, repo)

        testSuite = TestSuite("Merge Up")

        for source in sources:
            if source != target:

                start = time.clock()
                mergeResult = stashRepository.mergeBranches(target, source) # merge from master to branches
                end = time.clock()
                executionTime = (end - start) / 1000
                appendMergeDownResult(mergeResult, testSuite, source, target, executionTime )
                if (mergeResult != MergeResult.Merged and mergeResult != MergeResult.Unnecessary):
                    break

                start = time.clock()
                mergeResult = stashRepository.mergeBranches(source, target) # merge from branch to master
                end = time.clock()
                executionTime = (end - start) / 1000
                appendMergeUpResult(mergeResult, testSuite, target, source, executionTime )
                if (mergeResult != MergeResult.Merged and mergeResult != MergeResult.Unnecessary):
                    break

        if not os.path.exists("output"):
            os.makedirs("output")

        with open("output/MergeUpReport.xml", 'w') as reportFile:
            TestSuite.to_file(reportFile, [testSuite])

    else:
        print("cba.teds.MergeUp -p <project> -r <repo> -t <target> -s <sources> -U <user> -P <password> [-debug]")
        sys.exit(2)

    logger.debug("End MergeUp - %s", datetime.now().strftime("%Y%m%d%H%M"))


def appendMergeUpResult(mergeResult, testSuite, source, target, executionTime ):
    
    if (mergeResult == MergeResult.Merged): 
        testSuite.test_cases.append(TestCase("Merge Up from %s to %s was successful." % (source, target), None, executionTime))
    elif (mergeResult == MergeResult.Unnecessary):
        testSuite.test_cases.append(TestCase("Merge Up from %s to %s is unnecessary." % (source, target), None, executionTime))
    else:
        testCase = TestCase("Merge Up from %s to %s failed (%s)." % (source, target, mergeResult.name), None, executionTime)
        testCase.add_failure_info(mergeResult.name, mergeResult.value)
        testSuite.test_cases.append(testCase)


if __name__ == "__main__":
    mergeUp(sys.argv[1:])  