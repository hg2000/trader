from settings import Settings


class Const:

    columns = ['date', 'symbol', 'bid_open', 'bid_high', 'bid_low', 'bid_close',
               'offer_open', 'offer_high', 'offer_low', 'offer_close', 'volume', 'timestamp', 'open_long', 'close_long', 'open_short', 'close_short']


class Quote:

    date: None
    offer_open: float
    offer_high: float
    offer_low: float
    offer_close: float
    bid_open: float
    bid_high: float
    bid_low: float
    bid_close: float
    volume: float
    is_end_of_timeframe: bool
    symbol: str
    timestamp: None
    open_long: None
    close_long: None
    open_short: None
    close_short: None
    timeframes: []
    timeframe: None

    def __init__(self, date, offer_open=None, offer_high=None, offer_low=None, offer_close=None, bid_open=None, bid_high=None, bid_low=None, bid_close=None, volume=None, is_end_of_timeframe=False, symbol='', timestamp=None):

        if not bid_open:
            bid_open = offer_open
        if not bid_high:
            bid_high = offer_high
        if not bid_low:
            bid_low = offer_low
        if not bid_close:
            bid_close = offer_close

        self.date = date
        self.offer_open = None
        if offer_open:
            self.offer_open = float(offer_open)
        self.offer_high = None
        if offer_high:
            self.offer_high = float(offer_high)
        self.offer_low = None
        if offer_low:
            self.offer_low = float(offer_low)
        self.offer_close = None
        if offer_close:
            self.offer_close = float(offer_close)
        self.bid_open = None
        if bid_open:
            self.bid_open = float(bid_open)
        self.bid_high = None
        if bid_high:
            self.bid_high = float(bid_high)
        self.bid_low = None
        if bid_low:
            self.bid_low = float(bid_low)
        self.bid_close = None
        if bid_close:
            self.bid_close = float(bid_close)
        self.volume = None
        if volume:
            self.volume = float(volume)
        else:
            self.volume = 0

        self.is_end_of_timeframe = is_end_of_timeframe

        self.symbol = symbol
        self.timestamp = timestamp
        self.timeframes = []

        self.open_long = None
        self.close_long = None
        self.open_short = None
        self.close_short = None
        self.highlow = {}
        self.lines = {}
        self.indicators = {}
        self.calculate_timeframes()
        self.timeframe = Settings.min_time_frame

    def to_dict(self):
        return {
            'date': self.date,
            'symbol': self.symbol,
            'offer_open': self.offer_open,
            'offer_high': self.offer_high,
            'offer_low': self.offer_low,
            'offer_close': self.offer_close,
            'bid_open': self.bid_open,
            'bid_high': self.bid_high,
            'bid_low': self.bid_low,
            'bid_close': self.bid_close,
            'volume': self.volume,
            'is_end_of_timeframe': self.is_end_of_timeframe,
            'timestamp': self.timestamp,
            'open_long': self.open_long,
            'close_long': self.close_long,
            'open_short': self.open_short,
            'close_short': self.close_short
        }

    def to_df(self):

        d = self.to_dict()
        series = pd.Series(d)
        return series

    def from_df(self, df):

        self.offer_open = df['offer_open']
        self.offer_high = df['offer_high']
        self.offer_low = df['offer_low']
        self.offer_close = df['offer_close']
        self.bid_open = df['bid_open']
        self.bid_high = df['bid_high']
        self.bid_low = df['bid_low']
        self.bid_close = df['bid_close']
        self.volume = df['volume']
        self.timestamp = df['timestamp']
        self.is_end_of_timeframe = True

    def calculate_timeframes(self):
        '''Extracts timeframes from the date
        '''

        self.timeframes = []
        #if self.date.second < 10:
        #    self.timeframes.append(Settings.get('Interval').m1)
        if self.date.minute < 1:
            self.timeframes.append(Settings.get('Interval').h1)

        if self.date.minute % 5 == 0:
            self.timeframes.append(Settings.get('Interval').m5)
        if self.date.minute % 15 == 0:
            self.timeframes.append(Settings.get('Interval').m15)
        if self.date.hour % 4 == 0 and self.date.minute < 1:
            self.timeframes.append(Settings.get('Interval').h4)

        if self.date.minute == 0 and self.date.hour == 0:
            self.timeframes.append(Settings.get('Interval').d1)
