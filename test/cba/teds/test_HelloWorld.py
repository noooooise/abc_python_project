
import unittest

from cba.teds.HelloWorld import helloWorld 
from cba.teds.utils.WorkingDirectory import forceWorkingDirectory


class testHelloWorld(unittest.TestCase):
    """
    Unit Tests for HelloWorld Script.
    """

    @classmethod
    def setUpClass(self):
        forceWorkingDirectory()


    def test_helloTEDS(self):
        """
        Tests that Hello World "works" (i.e. doesn't throw an exception) with "TEDS Team".
        """
        
        try:                        
            args = "-n TEDS Team".split()                        
            helloWorld(args)

        except Exception as e:
            self.fail("HelloWorld.py threw an exception (%s)." % (e))
                
    def test_helloCBA(self):
        """
        Tests that Hello World "works" (i.e. doesn't throw an exception) with "CBA".
        """
        
        try:                        
            args = "-n CBA".split()                        
            helloWorld(args)            

        except Exception as e:
            self.fail("HelloWorld.py threw an exception (%s)." % (e))

    # def test_failExample(self):
    #     """
    #     Fail...
    #     """
    #
    #     self.fail("Unit Test Failed")

if __name__ == "__main__":
    unittest.main()