from settings import Settings
from observer import Observer, Subject
import linecache
import sys


class TradingEngine(Observer, Subject):
    ''' 
        Recieves Actions and data about price and position updates and delegates them to the
        corresponding modules
    '''

    def __init__(self, symbols, setup_items, position_manager):

        self.symbols = symbols
        self.setup_items = setup_items
        self.position_manager = position_manager

        self.log = Settings.get('Logger')()
        self.datetime = None
        self.current_timeframes = []
        self.position = None
        self.is_chart_update = False
        self.last_quotes = {}
        self.tick = None
        self.quote = None

        self.strategies = {}
        for item in setup_items:
            symbol = item.symbol
            timeframe = item.parameters.timeframe
            name = item.strategy_name
            if not name in self.strategies:
                self.strategies[name] = {}
            if not symbol in self.strategies[name]:
                self.strategies[name][symbol] = {}
            if not timeframe in self.strategies[name][symbol]:
                self.strategies[name][symbol][timeframe] = {}

            self.strategies[name][symbol][timeframe] = Settings.get(
                'Strategy_' + name)(item)
            self.attach(self.strategies[name][symbol]
                        [timeframe], Settings.get('Domain').position)

    def update(self, subject, message) -> None:

        if message == Settings.get('Message').update_tick:
            self.update_tick(subject.tick)

        if message == Settings.get('Message').update_quote:
            self.update_quote(subject.quote)

    def update_tick(self, tick):

        self.tick = tick
        self.bid = tick.bid_close
        self.offer = tick.offer_close
        self.symbol = tick.symbol
        self.datetime = tick.date

        self.position_manager.update_open_position_calculations(
            self.bid, self.offer, self.symbol, self.datetime)

        try:
            for name in self.strategies:
                if self.symbol in self.strategies[name]:
                    for strategy_timeframe in self.strategies[name][self.symbol]:
                        strategy = self.strategies[name][self.symbol][strategy_timeframe]
                        self.position = self.position_manager.get_open_position_by_strategy(
                            self.symbol, strategy)

                        self.strategies[name][self.symbol][strategy_timeframe].prepare(
                            self.tick, self.bid, self.offer, self.datetime, self.quote, self.position)

                        self.strategies[name][self.symbol][strategy_timeframe].on_update_price(
                        )

        except Settings.get('MissingDataException') as e:
            return False
        except BaseException as e:
            self._log_exception(e)
            return False

    def update_quote(self, quote):

        self.quote = quote
        self.bid = quote.bid_close
        self.offer = quote.offer_close
        self.symbol = quote.symbol
        self.datetime = quote.date

        self.position_manager.update_open_position_calculations(
            self.bid, self.offer, self.symbol, self.datetime)

        try:
            for name in self.strategies:
                if self.symbol in self.strategies[name]:
                    for strategy_timeframe in self.strategies[name][self.symbol]:
                        strategy = self.strategies[name][self.symbol][strategy_timeframe]
                        if strategy.timeframe == quote.timeframe:
                            self.position = self.position_manager.get_open_position_by_strategy(
                                self.symbol, strategy)

                            self.strategies[name][self.symbol][strategy_timeframe].prepare(
                                self.tick, self.bid, self.offer, self.datetime, self.quote, self.position)

                            self.strategies[name][self.symbol][strategy_timeframe].on_update_chart(
                            )

        except Settings.get('MissingDataException') as e:
            return False
        except BaseException as e:
            self._log_exception(e)
            return False

    def _log_exception(self, e):

        exc_type, exc_obj, tb = sys.exc_info()
        f = tb.tb_frame
        lineno = tb.tb_lineno
        filename = f.f_code.co_filename
        linecache.checkcache(filename)

        m = '{}, FILE: {}, LINE: {}'.format(exc_obj, filename, lineno)

        self.log.error(m)
        self.log.info(m)
        return False
