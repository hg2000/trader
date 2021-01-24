from settings import Settings
from observer import Observer, Subject


class BaseStrategy(Observer, Subject):

    def __init__(self, setup_item):

        self.setup_item = setup_item
        self.parameters = setup_item.parameters
        self.symbol = setup_item.symbol
        self.timeframe = setup_item.parameters.timeframe
        self.bid = None
        self.offer = None
        self.commands = []
        self.high_low = None
        self.indicator = Settings.get('Indicator')()
        self.quote = None
        self.log = Settings.get('Logger')()
        self.position = None
        self.is_end_of_timeframe = False

    def prepare(self, tick, bid, offer, datetime, quote=None, position=None):

        self.tick = tick
        self.bid = bid
        self.offer = offer
        self.datetime = datetime
        if quote:
            self.quote = quote
        self.position = position

    def update(self, subject, message):

        if message == Settings.get('Message').position_opened:
            if subject.position.setup_item == self.setup_item:
                self.position = subject.position

        if message == Settings.get('Message').position_updated:
            if subject.position.setup_item == self.setup_item:
                self.position = subject.position

        if message == Settings.get('Message').position_closed:
            if subject.position.setup_item == self.setup_item:
                self.position = None

    def open(self, direction_str):

        if self.has_open_position():
            return False

        self.position = Settings.get('Position')(setup_item=self.setup_item)

        if direction_str == 'long' or direction_str == 'buy':
            self.position.direction = Settings.get('Direction').buy

        if direction_str == 'short' or direction_str == 'sell':
            self.position.direction = Settings.get('Direction').sell

        self.notify(Settings.get('Message').open_position,
                    Settings.get('Domain').position)

    def close(self):

        self.notify(Settings.get('Message').close_position,
                    Settings.get('Domain').position)

    def has_open_position(self):

        if not self.position:
            return False

        return self.position.is_open()

    @property
    def state(self):
        return self.position.state

    @state.setter
    def state(self, state):

        self.position.state = state
        self.commands.append(
            Settings.get('Command')(action=Settings.get(
                'Action').change_state, position=self.position)
        )

    def reset_state(self):

        self.position.state = None
        self.commands.append(
            Settings.get('Command')(
                action=Settings.get('Action').reset_state, position=self.position)
        )

    def SMA(self, length):

        n = self.price_manager.get_last_closes(
            self.symbol, length+1, self.timeframe)
        try:
            sma = self.indicator.sma(n, length)

            return sma
        except ValueError:
            raise Settings.get('MissingDataException')

    def EMA(self, length):

        n = self.price_manager.get_last_closes(
            self.symbol, length+1, self.timeframe)
        try:
            ema = self.indicator.ema(n, length)

            if not ema in self.quote.indicators:
                self.quote.indicators['ema'] = {}

            if not length in self.quote.indicators['ema']:
                self.quote.indicators['ema'][length] = ema

            return ema
        except ValueError:
            raise Settings.get('MissingDataException')

    def _add_indicator_value(self, key, length, value):

        if not key in self.quote.indicators:
            self.quote.indicators[key] = {}

        if not length in self.quote.indicators[key]:
            self.quote.indicators[key][length] = None

        self.quote.indicators[key][length] = None

    def ATR(self, length):

        try:
            n = self.price_manager.get_last_candles(
                self.symbol, length+1, self.timeframe)
            atr = self.indicator.atr(n, length)
            self._add_indicator_value('atr', length, atr)
            return atr
        except ValueError:
            raise Settings.get('MissingDataException')

    def ADX(self, length):

        try:
            n = self.price_manager.get_last_candles(
                self.symbol, length*2+1, self.timeframe)
                
            adx = self.indicator.adx(n, length)
            self._add_indicator_value('adx', length, adx)
            return adx

        except ValueError:
            raise Settings.get('MissingDataException')


    def test(self, length):
        try:
            n = self.price_manager.get_last_candles(
                self.symbol, length*2+1, self.timeframe)
            test = self.indicator.test(n, length, self.symbol)
            self._add_indicator_value('test', length, 'test')

            return test

        except ValueError:
            raise Settings.get('MissingDataException')

    def start_barcount(self, id):

        key = 'barcount_' + str(hash(self.position.setup_item)) + '_' + id

        if self.ram_storage.has(key):
            value = self.ram_storage.get(key)
            self.ram_storage.set(key, value + 1)
        else:
            self.ram_storage.set(key, 1)

    def stop_barcount(self, id):

        key = 'barcount_' + str(hash(self.position.setup_item)) + '_' + id
        if self.ram_storage.has(key):
            value = self.ram_storage.get(key)
            self.ram_storage.free(key)

    def get_barcount(self, id):

        key = 'barcount_' + str(hash(self.position.setup_item)) + '_' + id
        if self.ram_storage.has(key):
            return self.ram_storage.get(key)

        raise Settings.get('MissingDataException')

    def has_barcount(self, id):

        key = 'barcount_' + str(hash(self.position.setup_item)) + '_' + id
        return self.ram_storage.has(key)

    def barcount(self):
        '''
            Increases active barcount values when the time has come
        '''

        setup_item_hash = str(hash(self.setup_item))
        if self.is_end_of_timeframe:
            for key in self.ram_storage.storage:
                parts = key.split('_')
                if parts[0] == 'barcount' and parts[1] == setup_item_hash:
                    self.ram_storage.storage[key] += 1

    def get_price_maximum(self, window_length):

        if not self.high_low:
            self.high_low = self.price_manager.get_high_low(
                self.symbol, window_length, self.timeframe)

        if not self.high_low:
            return None

        return self.high_low['high']

    def get_price_minimum(self, window_length):

        if not self.high_low:
            self.high_low = self.price_manager.get_high_low(
                self.symbol, window_length, self.timeframe)

        if not self.high_low:
            return None

        return self.high_low['low']

    def set_line(self, key, value):

        if self.quote:
            self.quote.lines[key] = value
