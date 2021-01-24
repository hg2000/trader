import os
import sys
import unittest
sys.path.append(os.getcwd() + '/livetrader')
from unittest.mock import MagicMock
from quote.quote_repository import QuoteRepositoryTest
from engine.engine_factory import EngineFactoryUnittest
from strategy.service.strategy_factory import StrategyFactory
from environment.unittest import UnittestEnvironment
from pprint import pprint
from position_manager.position import Direction, Position
from action import Action
from action import Command


class TestBase(unittest.TestCase):


    def backtest_engine(self):

        environment = UnittestEnvironment(datapoints=30)

        setups = {}
        setups['EURUSD'] = {
            'stop': 9999,
            'timeframe': 'm15',
            'trailing': 9999,
        }

        strategy_name = 'Test'
        symbols = ['EURUSD']
        evaluator = environment.run(symbols, strategy_name, setups)
        results = evaluator.evaluate()

        self.assertEqual(results[0]['result_pips'], -3.0) 
        self.assertEqual(evaluator.price_manager.bid['EURUSD'], 20.0) 

    def test_position_manager(self):

        environment = UnittestEnvironment(datapoints=30)
        position_manager = environment.position_manager

        # position opening
        position_manager.open_position(symbol='EURUSD', bid=10, offer=20, direction=Direction.buy, timeframe='m15', stop_pips=15, trailing_pips=5, scaling_factor=1)
        
        for id in position_manager.open_positions:
            position = position_manager.open_positions[id]

        self.assertEqual(position.open_price, 20)
        self.assertEqual(position.result_pips, -10)

        # Move trailing level and stop level
        position = Position(symbol='EURUSD', epic=None, open_price=10, open_time=1, direction=Direction.buy, strategy='', timeframe='m15')
        position.stop_pips = 10
        position.trailing_pips = 5
        position.scaling_factor = 1

        position.initial_calculations()
        position.update_calculations(bid_price=20, offer_price=15)
        self.assertEqual(position.trailing_level, 15.0)
        self.assertEqual(position.stop_level, 15.0)
        self.assertEqual(position.result_pips, 10)
    


if __name__ == '__main__':
    unittest.main()
