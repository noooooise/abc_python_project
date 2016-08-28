
import abc

from cba.teds.teradata.qa.artifacts.Artifacts import Artifacts


class TeradataArtifacts(Artifacts):
    """"
        TeradataArtifacts is an abstract based class that defines the interfaces to Teradata objects that are being
        processed by the Quality Assurance component(s).
    """

    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def retrieveAssembledPackageFilesList(self):
        """
        Returns a list of File Names.
        """

    @abc.abstractmethod
    def retrieveChangeRequestNumber(self):
        """
        Returns the Change request Number.
        """

    @abc.abstractmethod
    def retrieveCreatedObjects(self):
        """
        Returns a list of Object Names (String) for all created objects.
        """

    @abc.abstractmethod
    def retrieveRolledBackObjects(self):
        """
        Returns a list of Object Names (String) for all rolled-back objects.
        """

    @abc.abstractmethod
    def retrieveDeletedObjects(self):
        """
        Returns a list of Object Names (String) for all rolled-back objects.
        """
