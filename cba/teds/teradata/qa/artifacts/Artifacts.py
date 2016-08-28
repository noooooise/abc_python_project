import abc


class Artifacts(object):
    """"
        Artifacts is an abstract based class that defines the interfaces to objects that are being processed by the
        Quality Assurance component(s).
    """

    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def name(self):
        """ Returns a Name for the Artifacts. ""
    @abc.abstractmethod
    def runChecks(self):
        """ Run all of the Checks for the Artifacts. """
