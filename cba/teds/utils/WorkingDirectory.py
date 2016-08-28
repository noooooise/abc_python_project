
import os


# TODO:  Write Unit Tests
def forceWorkingDirectory():
    """
    forceWorkingDirectory() will ensure that the working directory is set to the project root (i.e. python_core).

    There is a discrepancy between TeamCity (which always forces the working directory to be the project root) and IDEs
    (e.g. Eclipse, PyCharm) (which, by default, set the working directory to be the directory containing the script
    being run).
    """
    workingDirectory = os.path.abspath(os.path.curdir)
    if (os.path.exists("output") and os.path.exists("test") and os.path.exists("resources")):
        print("Working Directory is \"" + workingDirectory + "\"")
    else:
        # TODO:  Improve This!

        newWorkingDirectory = None

        if os.path.exists("../test") and os.path.exists("../resources"):
            newWorkingDirectory = os.path.abspath("../")
        elif os.path.exists("../../test") and os.path.exists("../../resources"):
            newWorkingDirectory = os.path.abspath("../../")
        elif os.path.exists("../../../test") and os.path.exists("../../../resources"):
            newWorkingDirectory = os.path.abspath("../../../")
        elif os.path.exists("../../../../test") and os.path.exists("../../../../resources"):
            newWorkingDirectory = os.path.abspath("../../../../")
        elif os.path.exists("../../../../../test") and os.path.exists("../../../../../resources"):
            newWorkingDirectory = os.path.abspath("../../../../../")
        elif os.path.exists("../../../../../../test") and os.path.exists("../../../../../../resources"):
            newWorkingDirectory = os.path.abspath("../../../../../../")

        if newWorkingDirectory is not None:
            os.chdir(newWorkingDirectory)
            print("Changed Working Directory from \"" + workingDirectory + "\" to \"" + newWorkingDirectory + "\"")
        else:
            print("Cannot Change Working Directory from \"" + workingDirectory)