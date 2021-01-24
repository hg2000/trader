from settings import Settings
from observer import Subject, Observer


class StreamAdapterLocal(Subject, Observer):

    def __init__(self, symbols, broker, quote_repository, datapoints, load_latest_quotes):

        self.symbols = symbols
        self.broker = broker
        self.log = Settings.get('Logger')()
        self.last_chart_price_items = {}
        self.quote_repository = quote_repository
        self.datapoints = datapoints
        self.universe = {}
        self.n = {}
        self.max_n = {}
        self.is_load_latest_quotes = load_latest_quotes
        self.quote = None

    def update(self, subject, message):

        if message == Settings.get('Message').start_backtest:
            self.init()

    def init(self):

        if self.load_latest_quotes:
            self.create_universe(self.symbols, self.datapoints)

    def create_universe(self, symbols, limit=100):
        '''
            loads the data in which the backtest will operate
        '''

        for symbol in symbols:
            self.universe[symbol] = Settings.get('Quotes')()
            rows = self.quote_repository.get_latest_by_symbol(symbol, limit)
            self.n[symbol] = 0
            self.max_n[symbol] = len(rows)-1

            for row in reversed(rows):
                self.universe[symbol].add_quote(
                    self._convert_row_to_quote(row))

        if self.is_load_latest_quotes:
            self.load_latest_quotes()

    def load_latest_quotes(self):

        for symbol in self.symbols:
            while self.n[symbol] < 200:
                self.quote = self._fetch_next_quote(symbol)
                self.notify(Settings.get(
                    'Message').update_quote_preload, Settings.get('Domain').price)

    def run(self):

        n = None
        for symbol in self.max_n:
            if not n:
                n = self.max_n[symbol]
            if n < self.max_n[symbol]:
                n = self.max_n[symbol]
        i = 0
        while i < n:
            for symbol in self.symbols:
                quote = self._fetch_next_quote(symbol)
                if not quote:
                    break

                self.quote = quote
                self.notify(Settings.get('Message').update_quote,
                            Settings.get('Domain').price)
            i += 1

    def _fetch_next_quote(self, symbol):

        if self.n[symbol] > self.max_n[symbol]:
            return None
        quote = self.universe[symbol].df[self.n[symbol]]
        self.n[symbol] += 1
        return quote

    def _convert_row_to_quote(self, row):

        return Settings.get('Quote')(
            timestamp=row[2].toordinal(),
            date=row[2], offer_open=row[3], offer_high=row[4], offer_low=row[5], offer_close=row[6], bid_open=row[7],
            bid_high=row[8], bid_low=row[9], bid_close=row[10], volume=row[11], is_end_of_timeframe=False, symbol=row[1]
        )
