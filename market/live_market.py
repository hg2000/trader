
from settings import Settings

class LiveMarket():

    def __init__(self, broker):

        self.market = {}
        self.broker = broker

    def get(self, symbol):

        if not symbol in self.market:
            self.market[symbol] = self.broker.fetch_market_by_symbol(symbol)
        return self.market[symbol]

    def scaling_factor(self, symbol):

        market = self.get(symbol)
        return market['snapshot']['scalingFactor']

    def get_min_stop(self, symbol):

        return float(self.get(symbol)['dealingRules']['minNormalStopOrLimitDistance']['value'])

    def get_currency_code(self, symbol):

        return self.get(symbol)['instrument']['currencies'][0]['name']
        
