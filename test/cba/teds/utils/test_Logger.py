
import unittest

from cba.teds.utils.Logger import getLogger


class testLogger(unittest.TestCase):
    """
    Unit Tests for the getLogger() Function.
    """

    def test_getLogger(self):
        myLogger = getLogger()
        self.assertIsNotNone(myLogger, "Check My Logger")

    def test_lotsOfLoggers(self):
        aLogger = getLogger()
        anotherLogger = getLogger()
        self.assertIsNotNone(aLogger, "Check A Logger")
        self.assertIsNotNone(anotherLogger, "Check Another Logger")
        self.assertEqual(len(anotherLogger.handlers), 1, "Check Handlers")


if __name__ == "__main__":
    unittest.main()