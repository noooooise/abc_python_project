
import cba.teds.utils.Logger
import getopt
import os
import sys

from datetime import datetime
from junit_xml import TestSuite, TestCase
from random import randint


def helloWorld(argv):
    """
    Hello World is intended as a simple example of a script that can be called from the command line (or via
    TeamCity).
    
    Example: python -m cba.teds.HelloWorld -n TEDS

    It includes sample code to parse command line parameters, capture activity, generate XML and log activity. A
    corresponding Build Configuration in TeamCity demonstrates how to transform the XML into a Report Build Artifact.
    """

    # Initialize Logging
    logger = cba.teds.utils.Logger.getLogger()

    logger.debug("Start HelloWorld(%s) - %s", argv, datetime.now().strftime("%Y%m%d%H%M"))

    name = ""

    try:
        opts, args = getopt.getopt(argv, "n:", ["name="])
        args  # this comment prevents a warning
    except getopt.GetoptError as e:
        print(e)
        print("cba.teds.helloWorld -n <name>")
        sys.exit(2)

    for opt, arg in opts:
        if opt in ("-n", "--name"):
            name = arg

    testSuite = TestSuite("Hello World")

    testSuite.test_cases.append(TestCase("I'm a check in BETA", None, randint(1,10)))
    testSuite.test_cases.append(TestCase("I'm another check", None, randint(1,10)))
    testSuite.test_cases.append(TestCase("I'm yet another check", None, randint(1,10)))
    testSuite.test_cases.append(TestCase("Guess what..?", None, randint(1,10)))

    # testCase = TestCase("I'm a failed check", None, randint(1,10))
    # testCase.add_failure_info("Here is some more information and a ([[A-10]]) for even more information.", "")
    # testSuite.test_cases.append(testCase)

    testCase = TestCase("I'm a warning", None, randint(1,10))
    testCase.add_error_info("Here is some more information about the warning and a ([[A-10]]) for even more information.", "")
    testSuite.test_cases.append(testCase)

    testCase = TestCase("I'm a warning and a failure", None, randint(1,10))
    testCase.add_failure_info("Here is some more information about the failure and a ([[A-10]]) for even more information.", "")
    testCase.add_error_info("Here is some more information about the warning and a ([[A-10]]) for even more information.", "")
    testCase.stdout = "Here is some information."
    testSuite.test_cases.append(testCase)

    testCase = TestCase("I'm a failure", None, randint(1,10))
    testCase.add_failure_info("Here is some more information about the failure and a ([[A-10]]) for even more information.", "")
    testSuite.test_cases.append(testCase)

    testSuite.test_cases.append(TestCase("Hello %s!" % (name), None, randint(1,10)))

    # testCase = TestCase("I'm another failed check", None, randint(1,10))
    # testCase.add_failure_info("I can be anything but should include a [[27]] to Confluence.", "")
    # testSuite.test_cases.append(testCase)

    if not os.path.exists("output"):
        os.makedirs("output")

    with open("output/HelloWorldReport.xml", 'w') as reportFile:
        TestSuite.to_file(reportFile, [testSuite])

    logger.debug("End MergeDown - %s", datetime.now().strftime("%Y%m%d%H%M"))


if __name__ == "__main__":
    helloWorld(sys.argv[1:])  