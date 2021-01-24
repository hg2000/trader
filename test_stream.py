import unittest
from unittest.mock import MagicMock
from settings import Settings
from datetime import datetime
from connections.stream_adapter import StreamAdapterIG
import os, time
import pytz  

class Test(unittest.TestCase):
    '''
        Test the live engine. Take care that a test account is used!
    '''

    def _init_environment(self):

        parameters = Settings.get('Parameters')()
        parameters.timeframe = 'm15'
        parameters.stop = 15
        parameters.trailing = 15

        setup_item = Settings.get('SetupItem')()
        setup_item.strategy_name = 'Breakout'
        setup_item.symbols = ['EURUSD']
        setup_item.symbol = 'EURUSD'
        setup_item.parameters = parameters
        setup_items = [setup_item]

        self.environment = Settings.get('EnvironmentBacktest')(
            500, False, setup_items)


    def test_price_update(self):

        self._init_environment()
        stream = StreamAdapterIG(self.environment.symbols, self.environment.broker, self.environment.quote_repository, False, False)

        stream.all_timeframes = ['m5', 'm15', 'h1', 'h4']
        price_item = {
            'name': 'CHART:CS.D.EURUSD.MINI.IP:5MINUTE',
            'values':
            {'BID_CLOSE': '0.68877', 'BID_HIGH': '0.68880', 'BID_LOW': '0.68852', 'BID_OPEN': '0.68860', 'CONS_END': '1', 'CONS_TICK_COUNT': '191',
                'LTV': '191', 'OFR_CLOSE': '0.68886', 'OFR_HIGH': '0.68889', 'OFR_LOW': '0.68858', 'OFR_OPEN': '0.68866', 'TTV': None, 'UTM': '1593162300000'}
        }
        price_item['values']['UTM'] = datetime(2020,1,1,16,55).replace(tzinfo=pytz.UTC).timestamp() * 1000
        stream.on_prices_update(price_item)
        price_item['values']['UTM'] = datetime(2020,1,1,17,0).replace(tzinfo=pytz.UTC).timestamp() * 1000
        stream.on_prices_update(price_item)
        price_item['values']['UTM'] = datetime(2020,1,1,17,5).replace(tzinfo=pytz.UTC).timestamp() * 1000
        stream.on_prices_update(price_item)
        price_item['values']['UTM'] = datetime(2020,1,1,17,10).replace(tzinfo=pytz.UTC).timestamp() * 1000
        stream.on_prices_update(price_item)
        price_item['values']['UTM'] = datetime(2020,1,1,17,15).replace(tzinfo=pytz.UTC).timestamp() * 1000
        stream.on_prices_update(price_item)


    def stream_adapter_ig(self):

        self._init_environment()
        stream = StreamAdapterIG(self.environment.symbols, self.environment.broker, self.environment.quote_repository, False, False)

        stream.all_timeframes = ['m5', 'm15', 'h1', 'h4']
        price_item = {
            'name': 'CHART:CS.D.AUDUSD.MINI.IP:5MINUTE',
            'values':
            {'BID_CLOSE': '0.68877', 'BID_HIGH': '0.68880', 'BID_LOW': '0.68852', 'BID_OPEN': '0.68860', 'CONS_END': '1', 'CONS_TICK_COUNT': '191',
                'LTV': '191', 'OFR_CLOSE': '0.68886', 'OFR_HIGH': '0.68889', 'OFR_LOW': '0.68858', 'OFR_OPEN': '0.68866', 'TTV': None, 'UTM': '1593162300000'}
        }

        price_item['values']['UTM'] = datetime(2020,1,1,17,2).replace(tzinfo=pytz.UTC).timestamp() * 1000
        quote = stream.convert_price_item_to_quote(price_item)
        self.assertEqual([], quote.timeframes)

        price_item['values']['UTM'] = datetime(2020,1,1,17,5,1).replace(tzinfo=pytz.UTC).timestamp() * 1000
        quote = stream.convert_price_item_to_quote(price_item)
        self.assertEqual(['m5'], quote.timeframes)

        price_item['values']['UTM'] = datetime(2020,1,1,17,5,2).replace(tzinfo=pytz.UTC).timestamp() * 1000
        quote = stream.convert_price_item_to_quote(price_item)
        self.assertEqual([], quote.timeframes)

        price_item['values']['UTM'] = datetime(2020,1,1,17,15).replace(tzinfo=pytz.UTC).timestamp() * 1000
        quote = stream.convert_price_item_to_quote(price_item)
        self.assertEqual(['m5', 'm15'], quote.timeframes)

        price_item['values']['UTM'] = datetime(2020,1,1,17,30).replace(tzinfo=pytz.UTC).timestamp() * 1000
        quote = stream.convert_price_item_to_quote(price_item)
        self.assertEqual(['m5', 'm15'], quote.timeframes)

        price_item['values']['UTM'] = datetime(2020,1,1,18,00).replace(tzinfo=pytz.UTC).timestamp() * 1000
        quote = stream.convert_price_item_to_quote(price_item)
        self.assertEqual(['m5', 'm15', 'h1'], quote.timeframes)

        price_item['values']['UTM'] = datetime(2020,1,1,20,00,1).replace(tzinfo=pytz.UTC).timestamp() * 1000
        quote = stream.convert_price_item_to_quote(price_item)
        self.assertEqual(['m5', 'm15', 'h1', 'h4'], quote.timeframes)

        price_item['values']['UTM'] = datetime(2020,1,1,20,00,45).replace(tzinfo=pytz.UTC).timestamp() * 1000
        quote = stream.convert_price_item_to_quote(price_item)
        self.assertEqual([], quote.timeframes)


        self.assertTrue(stream.is_new_item(price_item))
        self.assertFalse(stream.is_new_item(price_item))


if __name__ == '__main__':
    unittest.main()
