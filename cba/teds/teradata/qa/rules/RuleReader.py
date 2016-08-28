
import cba.teds.utils.Logger

from cba.teds.teradata.qa.rules.Rule import *

import xml.etree.ElementTree as ET

class RuleReader(object):
    """
    The RuleReader class provides a bridge between an XML rules file and the object model of our Quality Assurance
    component.

    Create an object by passing in an XML file and a root node and then retrieve objects using the various
    retrieve* methods.
    """

    # TODO:  Some of these are in Enums (use the Enum values)
    # TODO:  For the others..? Maybe create another class...

    __ACTION = 'action'
    __ACTIONS = 'actions'
    __WHEN = 'when'
    __WHENS = 'whens'
    __QA_CHECK_RULE = 'rule'
    __QA_CHECK_RULES = 'rules'

    __NAME = "name"
    __VALUE = "value"
    __TYPE = "type"
    __SCOPE = "scope"
    __FILTER = "filter"
    __LEVEL = "level"
    __MESSAGE = "message"

    __TEXT_MATCH = 'textMatch'
    __NO_TEXT_MATCH = 'noTextMatch'
    __PATTERN_MATCH = 'patternMatch'
    __NO_PATTERN_MATCH = 'noPatternMatch'
    __HAS_CR_NUMBER = 'containsCrNumber'
    __HAS_TERADATA_KEYWORDS = 'containsTeradataKeywords'



    # TODO:  Remove the default value
    def __init__(self, ruleFile, parentNode="assembledTeradataPackageChecks"):
        """
        Constructor. Everything happens in the Constructor. The rule file is read and the objects are created.

        :param ruleFile: The relative (project root) path to the directory containing the rule file.
        :param parentNode: The name of the XML node that the whens/actions/rules are under.
        :returns
        """

        # Initialize Logging
        self.logger = cba.teds.utils.Logger.getLogger()

        # Always Log (Debug) Constructors, Destructors and Public Methods
        self.logger.debug("Create: RuleReader(%s, %s)", ruleFile, parentNode)

        self.__ruleFile = ruleFile
        self.__ASSEMBLED_TERADATA_PACKAGE_CHECKS = parentNode

        self.__whens = {}
        self.__actions = {}
        self.__rules = []

        self._readRules()

    # PUBLIC METHODS #

    def retrieveListOfWhenConditions(self):
        # Always Log (Debug) Constructors, Destructors and Public Methods
        self.logger.debug("RuleReader.retrieveListOfWhenConditions()")
        return self.__whens

    def retrieveListOfActions(self):
        # Always Log (Debug) Constructors, Destructors and Public Methods
        self.logger.debug("RuleReader.retrieveListOfActions()")
        return self.__actions

    def retrieveListOfRules(self):
        # Always Log (Debug) Constructors, Destructors and Public Methods
        self.logger.debug("RuleReader.retrieveListOfRules()")
        return self.__rules

    # PRIVATE METHODS #

    def _readRules(self):
        """
        Read through the rules file and call the appropriate parser for each node.
        """

        try:
            tree = ET.parse(self.__ruleFile)
            root = tree.getroot()
            for rootChild in root:
                if rootChild.tag == self.__ASSEMBLED_TERADATA_PACKAGE_CHECKS:
                    for child in rootChild.getchildren():
                        if child.tag == self.__WHENS:
                            self._buildWhens(child.getchildren())
                        elif child.tag == self.__ACTIONS:
                            self._buildActions(child.getchildren())
                        elif child.tag == self.__QA_CHECK_RULES:
                            self._buildRules(child.getchildren())

        except Exception as exception:
            self.logger.error("Error in RuleReader.readRules(): %s", exception)

    def _buildWhens(self, listOfWhen):
        """
        Parse a list of WHEN nodes
        """
        for when in listOfWhen:
            self.__whens[when.attrib[self.__NAME]] = When(when.attrib[self.__NAME], when.attrib[self.__VALUE],
                                                          when.attrib[self.__TYPE], when.attrib[self.__SCOPE],
                                                          when.attrib[self.__FILTER])

    def _buildActions(self, listOfActions):
        """
        Parse a list of ACTION nodes
        """
        for action in listOfActions:
            actionType = self.__getActionType(action)
            self.__actions[action.attrib[self.__NAME]] = Action(action.attrib[self.__NAME], actionType,
                                                                action.attrib[actionType])

    def _buildRules(self, listOfRules):
        """
        Parse a list of RULE nodes
        """
        for rule in listOfRules:
            whenName = rule.attrib[self.__WHEN]
            actionName = rule.attrib[self.__ACTION]
            when = self.__whens[whenName]
            action = self.__actions[actionName]
            self.__rules.append(Rule(when, action, rule.attrib[self.__LEVEL], rule.attrib[self.__MESSAGE]))

    def __getActionType(self, node):
        """
        Helper to get the Action Type from the node
        """

        # TODO: Improve the implementation

        typeOfMatch = None

        try:
            node.attrib[self.__TEXT_MATCH]
            return self.__TEXT_MATCH
        except KeyError:
            pass

        try:
            node.attrib[self.__NO_TEXT_MATCH]
            return self.__NO_TEXT_MATCH
        except KeyError:
            pass

        try:
            node.attrib[self.__PATTERN_MATCH]
            return self.__PATTERN_MATCH
        except KeyError:
            pass

        try:
            node.attrib[self.__NO_PATTERN_MATCH]
            return self.__NO_PATTERN_MATCH
        except KeyError:
            pass

        try:
            node.attrib[self.__HAS_CR_NUMBER]
            return self.__HAS_CR_NUMBER
        except KeyError:
            pass

        try:
            node.attrib[self.__HAS_TERADATA_KEYWORDS]
            return self.__HAS_TERADATA_KEYWORDS
        except KeyError:
            pass

        if typeOfMatch is None:
            self.logger.error("Unknown Action Type in RuleReader.getActionType(%s)", node.attrib)

        return ""
