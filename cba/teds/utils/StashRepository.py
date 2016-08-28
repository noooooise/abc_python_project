"""
StashRepository Module.
"""

import logging
import base64

# This (or something like it) may be required to get the script to run on the TeamCity Agent
# import sys
# import os
# print(sys.path)
# sys.path.append(os.path.realpath('./tedstools/TedsToolsPython/'))
# sys.path.append(os.path.realpath('.'))
# print(sys.path)

import stashy

from enum import Enum


class MergeResult(Enum):
    Merged = "Merged"
    Unnecessary = "is already up-to-date with branch"
    Conflicts = "The pull request has conflicts and cannot be merged"
    Existing = "Only one pull request may be open for a given source and target branch"
    Unknown = "Unknown"


class StashRepository(object):
    """
    The StashRepository class provide a repository-level interface to the Stash REST API.
    
    It's a relatively thin wrapper around a bunch of stuff in the Stashy Package.
    """

    def __init__(self, user, password, project, repository):
        """
        Constructor.
        """

        # Initialize Logging
        self.logger = logging.getLogger("cba")

        self.logger.debug("Create: StashRepository(%s, %s, %s, %s)", user, "?", project, repository)

        self.stashUrl = "https://stash.odp.cba"
        self._stashUser = user
        self._stashPassword = password
        # self._stashUser = "VGVyYWRhdGEtY2k="
        # self._stashPassword = "UGFzc3cwcmQh"

        # TODO:  Handle Connection Problems (e.g. bad credentials)...
        self._stash = stashy.connect(self.stashUrl, self.__getUserName(), self.__getPassword())

        self.project = project
        self.repository = repository


    def __getUserName(self):
        return self._stashUser
        # return base64.b64decode(self._stashUser).decode('UTF-8')


    def __getPassword(self):
        return self._stashPassword
        # return base64.b64decode(self._stashPassword).decode('UTF-8')


    def getBranchNames(self):
        """
        Returns a list (of Strings) of Branch Names.    
        """

        self.logger.debug("Call: getBranches(%s)", "")

        branchNames = []
        branches = list(self._stash.projects[self.project].repos[self.repository].branches())
        for branch in branches:
            branchNames.append(branch["displayId"])

        return branchNames


    def forkRepository(self, forkName):
        """
        Forks the current Repository.
        
        :param forkName: The name (as a String) for the forked Repository 
        """

        self.logger.debug("Call: forkRepository(forkName=%s)", forkName)

        self._stash.projects[self.project].repos[self.repository].fork(forkName)


    def deleteRepository(self):
        """
        Deletes the current Repository.        
        """

        self.logger.debug("Call: deleteRepository()")

        self._stash.projects[self.project].repos[self.repository].delete()


    def mergeBranches(self, source, target):
        """
        Merges the specified source (Branch) in to the specified target (Branch).
        
        :param source: The name (as a String) of the source branch 
        :param target: The name (as a String) of the target branch
        :returns: MergeResult (Enum) 
        """

        self.logger.debug("Call: mergeBranches(source=%s, target=%s)", source, target)

        mergeResult = MergeResult.Unknown

        # TODO:  It doesn't work if multiple items are returned e.g. PRVN_38.1, PRVN_38.11, PRVN_38.12

        sourceBranches = list(self._stash.projects[self.project].repos[self.repository].branches(source))
        targetBranches = list(self._stash.projects[self.project].repos[self.repository].branches(target))

        if (len(sourceBranches) != 1):
            raise ValueError("No Branch Called %s" % source)
        sourceBranch = sourceBranches[0]

        if (len(targetBranches) != 1):
            raise ValueError("No Branch Called %s" % target)
        targetBranch = targetBranches[0]

        mergeTitle = "Automated Merge from the " + source + " branch to the " + target + " branch"
        mergeDescription = ""

        try:
            self.logger.info("Creating: %s", mergeTitle)

            # NOTE: This is a customized implementation of "create" that takes branch objects. 
            # NOTE: The packaged version didn't work and I couldn't work what it was meant to be doing. 
            mergeRequest = self._stash.projects[self.project].repos[self.repository].pull_requests.create(mergeTitle,
                                                                                                          sourceBranch,
                                                                                                          targetBranch,
                                                                                                          mergeDescription)
            mergeRequestId = mergeRequest["id"];
            self.logger.info("  Merging (Pull Request #%s)...", mergeRequestId)

            try:
                mergeResult = self._stash.projects[self.project].repos[self.repository].pull_requests[
                    mergeRequestId].merge(0)
                self.logger.info("  Merge Result: %s", mergeResult['state'])
                mergeResult = MergeResult.Merged
            except Exception as e:
                self.logger.debug("Caught Exception: %s", str(e))
                self.logger.info("  Merge Result: %s", e.data['errors'][0]['message'])
                if (MergeResult.Conflicts.value in e.data['errors'][0]['message']):
                    mergeResult = MergeResult.Conflicts

        except Exception as e:
            self.logger.debug("Caught Exception: %s", str(e))
            self.logger.info("  Merge Result: %s", e.data['errors'][0]['message'])
            if (MergeResult.Unnecessary.value in e.data['errors'][0]['message']):
                mergeResult = MergeResult.Unnecessary
            if (MergeResult.Existing.value in e.data['errors'][0]['message']):
                mergeResult = MergeResult.Existing

        return mergeResult
