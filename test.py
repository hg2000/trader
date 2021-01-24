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

    def test_price_repository(self):

        price_repository = Settings.get('PriceRepository')()
        rows = price_repository.get_last_quotes('EURUSD', 'm15', 3)
        pass

    def test_enigne(self):

        self._init_environment()
        date =  datetime(2020,1,1,17,2).replace(tzinfo=pytz.UTC)
        quote = Settings.get('Quote')(date,5, 10, 2, 4)
        quote.symbol = 'EURUSD'
        quote.timeframe = 'm15'
        self.environment.engine.update_quote(quote)

    def price_update(self):

        self._init_environment()
        stream = StreamAdapterIG(self.environment.symbols, self.environment.broker, self.environment.quote_repository, False, False)

        stream.all_timeframes = ['m5', 'm15', 'h1', 'h4']
        price_item = {
            'name': 'CHART:CS.D.AUDUSD.MINI.IP:5MINUTE',
            'values':
            {'BID_CLOSE': '0.68463', 'BID_HIGH': '0.68485', 'BID_LOW': '0.68459', 'BID_OPEN': '0.68472', 'CONS_END': '1', 'CONS_TICK_COUNT': '191',
                'LTV': '191', 'OFR_CLOSE': '0.68886', 'OFR_HIGH': '0.68889', 'OFR_LOW': '0.68858', 'OFR_OPEN': '0.68866', 'TTV': None, 'UTM': '1593162300000'}
        }
        price_item['values']['UTM'] = datetime(2020,6,30,14,25).replace(tzinfo=pytz.UTC).timestamp() * 1000
        stream.on_prices_update(price_item)

        price_item = {
            'name': 'CHART:CS.D.AUDUSD.MINI.IP:5MINUTE',
            'values':
            {'BID_CLOSE': '0.68469', 'BID_HIGH': '0.68485', 'BID_LOW': '0.68459', 'BID_OPEN': '0.68474', 'CONS_END': '1', 'CONS_TICK_COUNT': '191',
                'LTV': '191', 'OFR_CLOSE': '0.68886', 'OFR_HIGH': '0.68889', 'OFR_LOW': '0.68858', 'OFR_OPEN': '0.68866', 'TTV': None, 'UTM': '1593162300000'}
        }
        price_item['values']['UTM'] = datetime(2020,6,30,14,30).replace(tzinfo=pytz.UTC).timestamp() * 1000
        stream.on_prices_update(price_item)

        price_item = {
            'name': 'CHART:CS.D.AUDUSD.MINI.IP:5MINUTE',
            'values':
            {'BID_CLOSE': '0.68507', 'BID_HIGH': '0.68512', 'BID_LOW': '0.68459', 'BID_OPEN': '0.68468', 'CONS_END': '1', 'CONS_TICK_COUNT': '191',
                'LTV': '191', 'OFR_CLOSE': '0.68886', 'OFR_HIGH': '0.68889', 'OFR_LOW': '0.68858', 'OFR_OPEN': '0.68866', 'TTV': None, 'UTM': '1593162300000'}
        }
        
        price_item['values']['UTM'] = datetime(2020,6,30,14,35).replace(tzinfo=pytz.UTC).timestamp() * 1000
        stream.on_prices_update(price_item)
        
        price_item = {
            'name': 'CHART:CS.D.AUDUSD.MINI.IP:5MINUTE',
            'values':
            {'BID_CLOSE': '0.68534', 'BID_HIGH': '0.68535', 'BID_LOW': '0.68500', 'BID_OPEN': '0.68506', 'CONS_END': '1', 'CONS_TICK_COUNT': '191',
                'LTV': '191', 'OFR_CLOSE': '0.68886', 'OFR_HIGH': '0.68889', 'OFR_LOW': '0.68858', 'OFR_OPEN': '0.68866', 'TTV': None, 'UTM': '1593162300000'}
        }
        price_item['values']['UTM'] = datetime(2020,6,30,14,40).replace(tzinfo=pytz.UTC).timestamp() * 1000
        stream.on_prices_update(price_item)
        
        price_item = {
            'name': 'CHART:CS.D.AUDUSD.MINI.IP:5MINUTE',
            'values':
            {'BID_CLOSE': '0.68577', 'BID_HIGH': '0.68582', 'BID_LOW': '0.68531', 'BID_OPEN': '0.68536', 'CONS_END': '1', 'CONS_TICK_COUNT': '191',
                'LTV': '191', 'OFR_CLOSE': '0.68886', 'OFR_HIGH': '0.68889', 'OFR_LOW': '0.68858', 'OFR_OPEN': '0.68866', 'TTV': None, 'UTM': '1593162300000'}
        }
        price_item['values']['UTM'] = datetime(2020,6,30,14,45).replace(tzinfo=pytz.UTC).timestamp() * 1000

        stream.on_prices_update(price_item)
        
        price_item = {
            'name': 'CHART:CS.D.AUDUSD.MINI.IP:5MINUTE',
            'values':
            {'BID_CLOSE': '0.68577', 'BID_HIGH': '0.68582', 'BID_LOW': '0.68531', 'BID_OPEN': '0.68536', 'CONS_END': '1', 'CONS_TICK_COUNT': '191',
                'LTV': '191', 'OFR_CLOSE': '0.68886', 'OFR_HIGH': '0.68889', 'OFR_LOW': '0.68858', 'OFR_OPEN': '0.68866', 'TTV': None, 'UTM': '1593162300000'}
        }
        price_item['values']['UTM'] = datetime(2020,6,30,14,50).replace(tzinfo=pytz.UTC).timestamp() * 1000

        stream.on_prices_update(price_item)

        price_item = {
            'name': 'CHART:CS.D.AUDUSD.MINI.IP:5MINUTE',
            'values':
            {'BID_CLOSE': '0.68577', 'BID_HIGH': '0.68582', 'BID_LOW': '0.68531', 'BID_OPEN': '0.68536', 'CONS_END': '1', 'CONS_TICK_COUNT': '191',
                'LTV': '191', 'OFR_CLOSE': '0.68886', 'OFR_HIGH': '0.68889', 'OFR_LOW': '0.68858', 'OFR_OPEN': '0.68866', 'TTV': None, 'UTM': '1593162300000'}
        }
        price_item['values']['UTM'] = datetime(2020,6,30,14,55).replace(tzinfo=pytz.UTC).timestamp() * 1000

        stream.on_prices_update(price_item)

        price_item = {
            'name': 'CHART:CS.D.AUDUSD.MINI.IP:5MINUTE',
            'values':
            {'BID_CLOSE': '0.68577', 'BID_HIGH': '0.68582', 'BID_LOW': '0.68531', 'BID_OPEN': '0.68536', 'CONS_END': '1', 'CONS_TICK_COUNT': '191',
                'LTV': '191', 'OFR_CLOSE': '0.68886', 'OFR_HIGH': '0.68889', 'OFR_LOW': '0.68858', 'OFR_OPEN': '0.68866', 'TTV': None, 'UTM': '1593162300000'}
        }
        price_item['values']['UTM'] = datetime(2020,6,30,15,00).replace(tzinfo=pytz.UTC).timestamp() * 1000

        stream.on_prices_update(price_item)

        price_item = {
            'name': 'CHART:QuoteCS.D.AUDUSD.MINI.IP:5MINUTE',
            'values':
            {'BID_CLOSE': '0.68577', 'BID_HIGH': '0.68582', 'BID_LOW': '0.68531', 'BID_OPEN': '0.68536', 'CONS_END': '1', 'CONS_TICK_COUNT': '191',
                'LTV': '191', 'OFR_CLOSE': '0.68886', 'OFR_HIGH': '0.68889', 'OFR_LOW': '0.68858', 'OFR_OPEN': '0.68866', 'TTV': None, 'UTM': '1593162300000'}
        }
        price_item['values']['UTM'] = datetime(2020,6,30,15,5).replace(tzinfo=pytz.UTC).timestamp() * 1000

        stream.on_prices_update(price_item)


    def test_stream_adapter_ig(self):

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


    def calculate_timeframes(self):
        ''' 
            tests if ticks are correctly summarized into higher timeframes
        '''

        self._init_environment()
        symbol = 'EURUSD'
        timeframe = 'm15'

        price_manager = self.environment.price_manager
        date = datetime(year=2020, month=5, day=29, hour=11, minute=45)
        tickm1 = Settings.get('Quote')(date=date, symbol=symbol, offer_open=1.11303, offer_high=1.11316, offer_low=1.11267,
                                       offer_close=1.11285, bid_open=1.11294, bid_high=1.11308, bid_low=1.11260, bid_close=1.11276, volume=1)
        price_manager.add_tick(tickm1)

        date = datetime(year=2020, month=5, day=29, hour=11, minute=50)
        tick1 = Settings.get('Quote')(date=date, symbol=symbol, offer_open=1.11286, offer_high=1.11296, offer_low=1.11262,
                                      offer_close=1.11269, bid_open=1.11280, bid_high=1.11290, bid_low=1.11255, bid_close=1.11263, volume=1)
        price_manager.add_tick(tick1)

        date = datetime(year=2020, month=5, day=29, hour=11, minute=55)
        tick2 = Settings.get('Quote')(date=date, symbol=symbol, offer_open=1.11272, offer_high=1.11368, offer_low=1.11272,
                                      offer_close=1.11331, bid_open=1.11266, bid_high=1.11361, bid_low=1.11266, bid_close=1.11325, volume=1)
        price_manager.add_tick(tick2)

        date = datetime(year=2020, month=5, day=29, hour=12, minute=0)
        tick3 = Settings.get('Quote')(date=date, symbol=symbol, offer_open=1.11330, offer_high=1.11349, offer_low=1.11310,
                                      offer_close=1.11339, bid_open=1.11324, bid_high=1.11340, bid_low=1.11301, bid_close=1.11330, volume=1)
        price_manager.add_tick(tick3)

        date = datetime(year=2020, month=5, day=29, hour=12, minute=5)
        tick4 = Settings.get('Quote')(date=date, symbol=symbol, offer_open=1.11338, offer_high=1.11398, offer_low=1.11334,
                                      offer_close=1.11378, bid_open=1.11329, bid_high=1.11392, bid_low=1.11327, bid_close=1.11372, volume=1)
        price_manager.add_tick(tick4)

        date = datetime(year=2020, month=5, day=29, hour=12, minute=10)
        tick5 = Settings.get('Quote')(date=date, symbol=symbol, offer_open=1.11380, offer_high=1.11380, offer_low=1.11316,
                                      offer_close=1.11319, bid_open=1.11371, bid_high=1.11371, bid_low=1.11307, bid_close=1.11310, volume=1)
        price_manager.add_tick(tick5)

        date = datetime(year=2020, month=5, day=29, hour=12, minute=15)
        tick6 = Settings.get('Quote')(date=date, symbol=symbol, offer_open=1.11320, offer_high=1.11362, offer_low=1.11308,
                                      offer_close=1.11310, bid_open=1.11313, bid_high=1.11355, bid_low=1.11300, bid_close=1.11303, volume=1)
        price_manager.add_tick(tick6)

        quotes = price_manager.get_last_quotes(symbol, 2, timeframe)

        q1 = quotes[0]
        self.assertEqual(45, q1.date.minute)
        self.assertEqual(1.11294, q1.bid_open)
        self.assertEqual(1.11361, q1.bid_high)
        self.assertEqual(1.11255, q1.bid_low)
        self.assertEqual(1.11325, q1.bid_close)

        self.assertEqual(1.11303, q1.offer_open)
        self.assertEqual(1.11368, q1.offer_high)
        self.assertEqual(1.11262, q1.offer_low)
        self.assertEqual(1.11331, q1.offer_close)
        self.assertEqual(3, q1.volume)

        q2 = quotes[1]
        self.assertEqual(0, q2.date.minute)
        self.assertEqual(1.11324, q2.bid_open)
        self.assertEqual(1.11392, q2.bid_high)
        self.assertEqual(1.11301, q2.bid_low)
        self.assertEqual(1.11310, q2.bid_close)

        self.assertEqual(1.11330, q2.offer_open)
        self.assertEqual(1.11398, q2.offer_high)
        self.assertEqual(1.11310, q2.offer_low)
        self.assertEqual(1.11319, q2.offer_close)
        self.assertEqual(3, q2.volume)

    def trading_engine(self):

        self._init_environment()
        symbol = 'EURUSD'
        timeframe = 'm15'

        price_manager = self.environment.price_manager
        date = datetime(year=2020, month=5, day=29, hour=11, minute=45)
        tickm1 = Settings.get('Quote')(date=date, symbol=symbol, offer_open=1.11303, offer_high=1.11316, offer_low=1.11267,
                                       offer_close=1.11285, bid_open=1.11294, bid_high=1.11308, bid_low=1.11260, bid_close=1.11276, volume=1)
        price_manager.add_tick(tickm1)

        date = datetime(year=2020, month=5, day=29, hour=11, minute=50)
        tick1 = Settings.get('Quote')(date=date, symbol=symbol, offer_open=1.11286, offer_high=1.11296, offer_low=1.11262,
                                      offer_close=1.11269, bid_open=1.11280, bid_high=1.11290, bid_low=1.11255, bid_close=1.11263, volume=1)
        price_manager.add_tick(tick1)

        date = datetime(year=2020, month=5, day=29, hour=11, minute=55)
        tick2 = Settings.get('Quote')(date=date, symbol=symbol, offer_open=1.11272, offer_high=1.11368, offer_low=1.11272,
                                      offer_close=1.11331, bid_open=1.11266, bid_high=1.11361, bid_low=1.11266, bid_close=1.11325, volume=1)
        price_manager.add_tick(tick2)

        date = datetime(year=2020, month=5, day=29, hour=12, minute=0)
        tick3 = Settings.get('Quote')(date=date, symbol=symbol, offer_open=1.11330, offer_high=1.11349, offer_low=1.11310,
                                      offer_close=1.11339, bid_open=1.11324, bid_high=1.11340, bid_low=1.11301, bid_close=1.11330, volume=1)
        price_manager.add_tick(tick3)

        date = datetime(year=2020, month=5, day=29, hour=12, minute=5)
        tick4 = Settings.get('Quote')(date=date, symbol=symbol, offer_open=1.11338, offer_high=1.11398, offer_low=1.11334,
                                      offer_close=1.11378, bid_open=1.11329, bid_high=1.11392, bid_low=1.11327, bid_close=1.11372, volume=1)
        price_manager.add_tick(tick4)

        date = datetime(year=2020, month=5, day=29, hour=12, minute=10)
        tick5 = Settings.get('Quote')(date=date, symbol=symbol, offer_open=1.11380, offer_high=1.11380, offer_low=1.11316,
                                      offer_close=1.11319, bid_open=1.11371, bid_high=1.11371, bid_low=1.11307, bid_close=1.11310, volume=1)
        price_manager.add_tick(tick5)

        date = datetime(year=2020, month=5, day=29, hour=12, minute=15)
        tick6 = Settings.get('Quote')(date=date, symbol=symbol, offer_open=1.11320, offer_high=1.11362, offer_low=1.11308,
                                      offer_close=1.11310, bid_open=1.11313, bid_high=1.11355, bid_low=1.11300, bid_close=1.11303, volume=1)

        engine = self.environment.engine
        engine.update_price(tick6)


if __name__ == '__main__':
    unittest.main()
