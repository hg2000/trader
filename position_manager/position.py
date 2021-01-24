from settings import Settings
import random
from datetime import timedelta


class Direction():

    buy = 'BUY'
    sell = 'SELL'


class Position():

    def __init__(self, setup_item=None, size=1, open_price=None, open_time=None, direction=None,  state=None):

        self.setup_item = setup_item
        self.open_price = open_price
        self.open_time = open_time
        self.direction = direction
        self.state = state
        self.close_time = None
        self.close_price = None
        self.result = None
        self.result_pips = None
        self.trailing_level = None
        self.stop_level = None
        self.size = size
        self.id = self._create_random_id()
        self.log = Settings.get('Logger')()
        self.limit_pips = None
        self.limit_level = None
        self.scaling_factor = None
        self.trailing_pips = None
        self.reference = None

        if setup_item:
            self.symbol = setup_item.symbol

            if setup_item.parameters.trailing:
                self.trailing_pips = int(setup_item.parameters.trailing)
            if setup_item.parameters.limit:
                self.limit_pips = int(setup_item.parameters.limit)
            self.stop_pips = int(setup_item.parameters.stop)
            self.timeframe = setup_item.parameters.timeframe
            self.strategy = setup_item.strategy_name

    def is_closed(self):

        if self.close_time:
            return True
        return False

    def is_open(self):

        if self.open_time and not self.close_time:
            return True
        return False

    def close(self):

        self.close_time = Settings.get('DateService').now()

    def is_closed_recently(self, now=None):

        if not now:
            now = Settings.get('DateService').now()

        treshold = now - timedelta(minutes=15)
        if self.close_time >= treshold:
            return True

        return False

    def initial_calculations(self):

        if self.direction == Settings.get('Direction').buy:

            self.stop_level = self.close_price - \
                (self.stop_pips / self.scaling_factor)
            if self.limit_pips:
                self.limit_level = self.close_price + \
                    (self.limit_pips / self.scaling_factor)
            if self.trailing_pips:
                self.trailing_level = self.close_price - \
                    (self.trailing_pips / self.scaling_factor)

        if self.direction == Settings.get('Direction').sell:
            self.stop_level = self.close_price + \
                (self.stop_pips / self.scaling_factor)
            if self.limit_pips:
                self.limit_level = self.close_price - \
                    (self.limit_pips / self.scaling_factor)
            if self.trailing_pips:
                self.trailing_level = self.close_price + \
                    (self.trailing_pips / self.scaling_factor)

    def update_calculations(self, bid_price, offer_price):
        '''
            Set the close price to the current price
            then calculate and update trailing level, stop level and result
        '''

        if self.direction == Settings.get('Direction').buy:
            self.close_price = bid_price
            self.result_pips = (
                self.close_price - self.open_price) * self.scaling_factor

            if self.trailing_pips:
                trailing_level = self.close_price - \
                    (self.trailing_pips / self.scaling_factor)
                if (trailing_level > self.trailing_level) and (self.result_pips > (self.trailing_pips + 1)):
                    self.trailing_level = trailing_level

        if self.direction == Settings.get('Direction').sell:
            self.close_price = offer_price
            self.result_pips = (
                self.open_price - self.close_price) * self.scaling_factor

            if self.trailing_pips:
                trailing_level = self.close_price + \
                    (self.trailing_pips / self.scaling_factor)
                if (trailing_level < self.trailing_level) and (self.result_pips > (self.trailing_pips + 1)):
                    self.trailing_level = trailing_level

        self.log.info(self.symbol + ', ' + self.direction + ', Result Pips: ' + str(self.result_pips) + ', Trailing Level: ' + str(self.trailing_level) + ' Stop Level: ' + str(self.stop_level))

    def _create_random_id(self):

        x = random.randint(1000, 9999)
        deal_id = hash(x)
        return deal_id

    def validate(self, bid, offer, symbol):
        '''
            Checks if some actions need to be taken.
            E.g. when buy position price is below stop level => close the position
        '''

        if not symbol == self.symbol:
            return None

        self.update_calculations(bid, offer)

        if self.direction == Settings.get('Direction').buy:
            if offer <= self.stop_level:
                self.log.info('Stop level reached for long position. Symbol: %s, Level: %s, bid: %s' % (
                    symbol, self.stop_level, offer))
                return Settings.get('Message').close_position

            if self.trailing_level and offer <= self.trailing_level and self.result_pips > (self.trailing_pips + 1):
                self.log.info('Trailing Stop level reached for long . Symbol: %s, Level: %s, bid: %s' % (
                    symbol, self.stop_level, offer))
                return Settings.get('Message').close_position

            if self.limit_level and offer >= self.limit_level:
                self.log.info('Limit level reached for long position. Symbol: %s, Level: %s, bid: %s' % (
                    symbol, self.limit_level, offer))
                return Settings.get('Message').close_position

        if self.direction == Settings.get('Direction').sell:
            if offer >= self.stop_level:
                self.log.info('Stop level reached for short position. Symbol: %s, Level: %s, offer: %s' % (
                    symbol, self.stop_level, bid))
                return Settings.get('Message').close_position

            if self.trailing_level and bid >= self.trailing_level and self.result_pips > (self.trailing_pips + 1):
                self.log.info('Trailing Stop level reached for short position. Symbol: %s, Level: %s, offer: %s' % (
                    symbol, self.stop_level, bid))
                return Settings.get('Message').close_position

            if self.limit_level:
                if bid <= self.limit_level:
                    self.log.info('Limit level reached for short position. Symbol: %s, Level: %s, bid: %s' % (
                        symbol, self.limit_level, bid))
                    return Settings.get('Message').close_position
        return None

    def __hash__(self):

        hash_string = self.symbol + \
            str(self.timeframe) + str(self.strategy) + hash(self.setup_item)
        return hash(hash_string)

    def is_equal(self, position):

        hash1 = str(hash(self.setup_item.parameters)) + \
            self.setup_item.strategy_name + self.setup_item.symbol
        hash2 = str(hash(position.setup_item.parameters)) + \
            position.setup_item.strategy_name + position.setup_item.symbol

        return hash1 == hash2
