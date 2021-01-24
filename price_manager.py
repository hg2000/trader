
from settings import Settings
from observer import Observer
import datetime

class PriceManagerException(BaseException):
    pass


class PriceManager(Observer):
    '''
        Provides access to quotes
    '''

    quotes = {}

    '''
        Dictonary of symbols with quotes dataframes
    '''

    max_size = 10000
    '''
        Max amount of quotes per symbol stored in RAM
    '''

    source: None
    '''
        Source of price data
    '''

    bid: {}
    '''
        Last bid price
    '''

    offer: {}
    '''
        Last offer price
    '''

    current_chartframes: []

    temp_last_day = 0

    def __init__(self, quote_repository, additional_quote_repository=None):

        self.current_chartframes = []
        self.quote_repository = quote_repository
        self.bid = {}
        self.offer = {}
        self.c = 0
        self.current_chartframes = []
        self.marked_timeframes = {}
        self.all_timeframes = Settings.all_timeframes
        self.additional_quote_repository = additional_quote_repository
        self.quotes = {}
        self.last_tick = {}

    def update(self, subject, message=None):
        pass


    def get_last_quotes(self, symbol, n=1, timeframe=None):
        '''
            returns the last n quotes
        '''
        if not timeframe:
            timeframe = self.timeframe

        if not self._quotes_exist(symbol):
            raise PriceManagerException(
                'No quote exists for symbol %s and timeframe %s ' % (symbol, timeframe))
        
        return self.quotes[symbol].get_last_quotes(n, timeframe)

    def _quotes_exist(self, symbol):
        '''
            Checks if currently quotes are stored for the given symbol
        '''
        if symbol in self.quotes:
            return True

        return False


    def get_last_closes(self, symbol, n=1, timeframe=None):
        '''
            returns the last n close pricesget('Interval').m5
        '''

        w = self.get_last_quotes(symbol, n, timeframe)
        r = []
        for q in w:
            r.append((q.bid_close + q.offer_close) / 2)

        return r

    def get_last_candles(self, symbol, n=1, timeframe=None):
        '''
            returns the last n close prices
        '''

        w = self.get_last_quotes(symbol, n, timeframe)
        r = []
        for q in w:
            r.append([(q.bid_open + q.offer_open) / 2, (q.bid_high + q.offer_high) / 2,
                      (q.bid_low + q.offer_low) / 2, (q.bid_close + q.offer_close) / 2])
        return r

    def get_last_quote(self, symbol, timeframe=None):

        quotes = self.get_last_quotes(symbol, 1, timeframe)
        if quotes:
            return quotes[-1]
        return None

    def get_amount_quotes(self, symbol):

        amount = len(self.quotes[symbol].tick_df)
        return amount

    def add_tick(self, tick):

        symbol = tick.symbol
        if not symbol in self.quotes:
            self.quotes[symbol] = Settings.get('Quotes')()

        self.quotes[symbol].add_tick(tick)






