
import cba.teds.utils.Logger

"""
This file defines the object model to support the Quality Assurance Rules metadata.

The rules (XML) files are parsed using RuleReader and Rule/When/Action objects are created. If you take a look at an
XML file (e.g. resources\teradataQualityCheckRules.xml) it should all make sense.
"""

from enum import Enum
import re


class RuleLevel(Enum):
    """
    RuleLevel defines the possible values for the Level property of a Rule object.

    The Level of a Rule defines how it is displayed in the Quality Assurance Report and it"s impact on the build status
    in TeamCity.

    Error = identifies a Rule that should fail a build (i.e. do not deploy the package)
    Warning = identifies a Rule that might fail a build (i.e. only deploy the package with supporting documentation)
    Information = identifies a Rule that provides information in the report but doesn"t impact the build status
    """

    Error = "error"
    Warning = "warning"
    Information = "information"


class WhenFilter(Enum):
    """
    WhenFilter defines the possible values for the Filter property of a When Object.

    It is used to specify a subset of artifacts (the implementation of which lives in RuleRunner).

    All = Every Artifact
    CreateTable = Only Artifacts that Create Tables
    CreateView = Only Artifacts that Create Views
    CreateComment = Only Artifacts that Create Comments
    """

    All = "ALL"
    CreateTable = "CREATE_TABLE"
    CreateView = "CREATE_VIEW"
    CreateComment = "CREATE_COMMENT"
    CreateBackupTable = "CREATE_BACKUP_TABLE"
    CreateBackupView = "CREATE_BACKUP_VIEW"

class WhenScope(Enum):
    """
    WhenScope defines the possible values for the Scope property of a When Object.

    It is used to specify how the artifacts are searched (the implementation of which lives in RuleRunner).

    Line = Search each line of each artifact separately
    Script = Search each artifact as a single entity
    FileName = Search the artifact file path
    """

    Line = "LINE"
    Script = "SCRIPT"
    FilePath = "FILE_PATH"


class WhenType(Enum):
    """
    WhenType defines the possible values for the Type property of a When Object.

    It is used to specify the type of search (the implementation of which lives in RuleRunner).

    Contains = Does the Filtered Scope contain the Value
    BeginsWith = Does the Filtered Scope begin with the Value
    MatchesPatter = Does the Filtered Scope include the pattern specified in the Value
    """

    Contains = "CONTAINS"
    BeginsWith = "BEGINS_WITH"
    MatchesPattern = "MATCHES_PATTERN"


class ActionType(Enum):
    """
    ActionType defines the possible values for the actionType property of a Action Object.

    It is used to specify how the action type will be checked.

    TextMatch = Search for text match
    PatternMatch = Search using regular expresion
    NoTextMatch = Search for no text match
    """
    TextMatch = "textMatch"
    PatternMatch = "patternMatch"
    NoTextMatch = "noTextMatch"
    ContainsCrNumber = "containsCrNumber"
    ContainsTeradataKeywords = "containsTeradataKeywords"


class Rule(object):
    """
    A Rule object defines a quality assurance check.

    when = an object that defines a specific set of artifact components (e.g. Create Table Statements)
    action = an object that defines an action to perform on the When object (e.g. Check for Multiset Statement)
    level = a RuleLevel enum that is used to group Rule objects
    message = a message (String) that should be displayed if dictated by the action
    """

    def __init__(self, when, action, level, message):
        """
        Rule Constructor.

        :param when: A When object
        :param action: An Action object
        :param level: Rule Level (RuleLevel Enum)
        :param message: A message (String) to be included in the report (if dictated by the action). The message can
        include a special character sequence (e.g. "[[n]]" where n is an integer) that will be transformed into a URL
        in the generated report.
        """
        self.when = when
        self.action = action
        self.level = level
        self.message = message

    def __str__(self):
        return "Rule: {when: (%s), action: (%s), level: (%s), message: (%s)}" % (self.when.name, self.action.name,
                                                                                 self.level, self.message)


class When(object):
    """
    A When object defines a specific set of artifact components (e.g. Create Table Statements).

    name = a name (String) that describes the condition (e.g. Create Table Statements)
    filter = a filter (WhenFilter) that is used to specify a subset of artifacts
    scope = the scope (WhenScope) that is used to specify how the artifacts are searched
    type = the type (WhenType) that is used to specify the type of search
    value = the value (String) that is searched for (subject to filter, scope and type)
    data = a list of resultant objects (WhenData) that match the criteria
    """

    def __init__(self, name, value, type, scope, filter):
        """
        When Constructor.

        :param name: Name (String)
        :param value: Value (String)
        :param type: Type (WhenType Enum)
        :param scope: Scope (WhenScope) Enum
        :param filter: Filter (WhenFilter) Enum
        """
        self.name = name
        self.value = value
        self.type = type
        self.scope = scope
        self.filter = filter
        self.data = []

    def isConditionMatched(self, data):
        isDataMatched = False
        tmpLine = data.lstrip().rstrip()
        if self.type == WhenType.Contains.value and tmpLine.find(self.value) > -1 :
            isDataMatched = True
        elif self.type == WhenType.BeginsWith.value and tmpLine.startswith(self.value) :
            isDataMatched = True
        elif self.type == WhenType.MatchesPattern.value:
            if re.search(self.value ,tmpLine) : # This is doing the patter match
                isDataMatched = True

        return isDataMatched

    def __str__(self):
        return "When: {name: (%s), value: (%s), type: (%s), scope: (%s), filter: (%s)}" % (self.name, self.value,
                                                                                           self.type, self.scope,
                                                                                           self.filter)


class WhenData(object):
    """
    A WhenData object defines a single artifact that meets the When criteria

    artifactName = a name (String) that identifies the artifact (e.g. file path)
    data = the data (String) in the artifact that matches the criteria
    """

    def __init__(self, artifactName, data):
        """
        WhenData Constructor.

        :param artifactName: Artifact Name (String)
        :param data: Data (String)
        """
        self.artifactName = artifactName
        self.data = data

    def __str__(self):
        return "WhenData: {artifactName: (%s), data: (%s)}" % (self.artifactName, self.data)


class Action(object):
    """
    An Action object defines what to to with an artifact that meets the When criteria

    name = a name (String) that identifies the action (e.g. Check for Multiset Statement)
    actionType = the type of action (ActionType) (e.g. textMatch)
    actionData = the data (String) to support the actionType
    """

    def __init__(self, name, actionType, actionData):
        """
        Action Constructor.

        :param name: Action Name (String)
        :param actionType: Action Type (ActionType Enum)
        :param actionData: Data (String)
        """

        # Initialize Logging
        self.logger = cba.teds.utils.Logger.getLogger()

        self.name = name
        self.actionType = actionType
        self.actionData = actionData

    def __str__(self):
        return "Action: {name: (%s), actionType: (%s), actionData: (%s)}" % (self.name, self.actionType, self.actionData)

    def executeAction(self, data, assembledPackage):
        """
        Execute the Action against the specified Data.

        :param data: The data part of a When Data object (String)
        :param assembledPackage: Our Artifacts object (AssembledPackage)
        :returns isValid: A flag that indicates that ? (Boolean)
        """

        actionRequired = False

        if self.actionType == ActionType.PatternMatch.value:
            # re.search() will return None if the pattern (in actionData) is not present (in data)
            if re.search(self.actionData, data) is None:
                actionRequired = True
        elif self.actionType == ActionType.TextMatch.value:
            # String.find() will return -1 if the text (in actionData) is not present (in data)
            if data.find(self.actionData ) == -1:
                actionRequired = True
        elif self.actionType == ActionType.NoTextMatch.value:
            # String.find() will return -1 if the text (in actionData) is not present (in data)
            if data.find(self.actionData ) != -1:
                actionRequired = True
        elif self.actionType == ActionType.ContainsCrNumber.value:
            # String.find() will return -1 if the Change Record Number (from Assembled Package) is not present (in data)
            crNumber = assembledPackage.retrieveChangeRequestNumber()
            if data.find(crNumber) == -1:
                actionRequired = True
        elif self.actionType == ActionType.ContainsTeradataKeywords.value:
            # this will retrieve String Array (teradataKeywords)
            teradataKeywords = assembledPackage.retrieveTeradataKeywords()
            whenData = data.lstrip()
            for keyword in teradataKeywords:
                # keyword = keyword + ' '   #
                # Action is required if the db line is begin with Teradata Keywords
                if whenData.find(keyword) == 0:
                    # print('data ', data)
                    # print(' - - keyword = %s, FIND = %d' % (keyword, whenData.find(keyword) ) )
                    actionRequired = True
                    break

        else:
            self.logger.warn("Action Type '%s' Not Implemented", self.actionType)

        return actionRequired

