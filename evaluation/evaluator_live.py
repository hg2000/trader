from settings import Settings


class EvaluatorLive():

    def __init__(self):

        self.log = Settings.get('Logger')()

    def add_open_position(self, position):

        self.log.info('Open position. Symbol: %s, Timeframe: %s  Strategy: %s ' % (
            position.symbol, position.timeframe, position.strategy_name))

    def add_close_position(self, position):

        self.log.info('Close position. Symbol: %s, Timeframe: %s  Strategy: %s, Result: %s ' % (
            position.symbol, position.timeframe, position.strategy_name, position.result_pips))

    def add_quote(self, quote, setup_item):

        pass
