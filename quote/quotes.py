from settings import Settings
from copy import copy


class Quotes:

    df: None
    tick_df: None
    last_added_tick: None

    def __init__(self):

        self.df = []
        self.tick_df = []
        self.last_added_tick = None
        self.last_minute = None

    def add(self, date, symbol='', offer_open=None, offer_high=None, offer_low=None, offer_close=None, bid_open=None, bid_high=None, bid_low=None, bid_close=None, volume=None, is_end_of_timeframe=None, timestamp=None):

        quote = Quote(date=date, symbol=symbol, offer_open=offer_open, offer_high=offer_high, offer_low=offer_low,
                      offer_close=offer_close, bid_open=bid_open, bid_high=bid_high, bid_low=bid_low, bid_close=bid_close, volume=volume, is_end_of_timeframe=is_end_of_timeframe, timestamp=timestamp)

        self.add_quote(quote)

    def add_quote(self, quote):
        '''
            adds a quote to the  collection.
            ignore the try of adding quotes of same dates
        '''

        last_quote = self.get_last_quote()
        if last_quote and last_quote.date == quote.date:
            return False

        self.df.append(quote)
        return True

    def timeframe_match(self, date, timeframe):

        timeframe = self.timeframe
        is_first = False

        if not self.last_minute:
            is_first = True
            self.last_minute = date.minute
            self.last_second = date.second
            self.last_hour = date.hour
            

        result = False

        if timeframe == Settings.get('Interval').m1:

            if is_first:
                return True

            if not date.minute == self.last_minute:
                self._set_last_date(date)
                return True

        if timeframe == Settings.get('Interval').m5 and date.minute % 5 == 0:

            if is_first:
                return True
       
            if not date.minute == self.last_minute:
                self._set_last_date(date)
                return True
           

        if timeframe == Settings.get('Interval').m15 and date.minute % 15 == 0:

            if is_first:
                return True

            if not date.minute == self.last_minute:
                self._set_last_date(date)
                return True

        if timeframe == Settings.get('Interval').h1 and date.minute == 0:

            if is_first:
                return True
                
            if not date.minute == self.last_minute and not date.hour == self.last_hour:
                self._set_last_date(date)
                return True

        if timeframe == Settings.get('Interval').h4 and date.hour % 4 == 0:
            if is_first:
                return True
            
            if date.minute == 0 and not date.minute == self.last_minute and not date.hour == self.last_hour:
                self._set_last_date(date)
                return True


        return result

    def _set_last_date(self, date):
        self.last_minute = date.minute
        self.last_second = date.second
        self.last_hour = date.hour


    def get_last_quotes(self, n, timeframe):

        quote = None
        quotes = []
        i = 0
        last_date = None
        self.timeframe = timeframe

        for tick in reversed(self.tick_df):

            # We traverse through ticks reversed, so open price will be in the last tick
            if self.timeframe_match(tick.date, timeframe):
                if quote:
                    if not quote.offer_high:
                        quote.offer_high = tick.offer_high
                    if tick.offer_high > quote.offer_high:
                        quote.offer_high = tick.offer_high
                    
                    if not quote.offer_low:
                        quote.offer_low = tick.offer_low
                    if tick.offer_low < quote.offer_low:
                        quote.offer_low = tick.offer_low

                    if not quote.bid_high:
                        quote.bid_high = tick.bid_high    
                    if tick.bid_high > quote.bid_high:
                        quote.bid_high = tick.bid_high

                    if not quote.bid_low:
                        quote.bid_low = tick.bid_low    
                    if tick.bid_low < quote.bid_low:
                        quote.bid_low = tick.bid_low

                    if not quote.volume:
                        quote.volume = tick.volume
                    else:
                        quote.volume += tick.volume
                    quote.offer_open = tick.offer_open
                    quote.bid_open = tick.bid_open
                    quote.date = tick.date
                    quote.timeframes = [timeframe]
                    quotes.append(quote)
                    i += 1
         
                quote = Settings.get('Quote')(tick.date)
                quote.symbol = tick.symbol
                continue
                
            if not quote:
                last_date = tick.date
                continue

            if not quote.offer_open:
                quote.offer_open = tick.offer_open
            if not quote.offer_high:
                quote.offer_high = tick.offer_high
            if not quote.offer_low:
                quote.offer_low = tick.offer_low
            if not quote.offer_close:
                quote.offer_close = tick.offer_close                

            if not quote.bid_open:
                quote.bid_open = tick.bid_open
            if not quote.bid_high:
                quote.bid_high = tick.bid_high
            if not quote.bid_low:
                quote.bid_low = tick.bid_low
            if not quote.bid_close:
                quote.bid_close = tick.bid_close
                
                
            if tick.offer_high > quote.offer_high:
                quote.offer_high = tick.offer_high
            if tick.offer_low < quote.offer_low:
                quote.offer_low = tick.offer_low
            if tick.bid_high > quote.bid_high:
                quote.bid_high = tick.bid_high
            if tick.bid_low < quote.bid_low:
                quote.bid_low = tick.bid_low
            quote.volume += tick.volume
            
            last_date = tick.date
            if i == n:
                break
            
        if not quotes:
            raise BaseException('Not enough tick data to calculate quote')
        quotes.reverse()
        return quotes

    def length(self):
        return len(self.df)

    def get_last_tick(self):

        length = len(self.tick_df)
        if length == 0:
            return None
        return self.tick_df[length - 1]

    def add_tick(self, tick):

        self.last_added_tick = tick
        self.tick_df.append(tick)
        return True

    def drop(self, max_size, drop_amount=50):
        '''
            if array is larger than max_size, drop first drop_amount rows
        '''

        if len(self.df) > max_size:
            self.df = self.df[drop_amount:]

    def get_last_quote(self):

        length = len(self.df)
        if length == 0:
            return None

        return self.df[length - 1]
