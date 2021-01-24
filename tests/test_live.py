import os
import sys
import unittest
sys.path.append(os.getcwd() + '/livetrader')
from unittest.mock import MagicMock
from engine.engine_factory import EngineFactory



class TestLive(unittest.TestCase):
    '''
        Test the live engine. Take care that a test account is used!
    '''

    def test_open(self):

        engine = EngineFactory.get_instance()

        pass

if __name__ == '__main__':
    unittest.main()