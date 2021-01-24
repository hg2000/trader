from settings import Settings
from observer import Subject


class EnvironmentBacktest(Subject):
    '''
     Initiates all classes needed for running backtests
    '''
    lates_quotes_limit = 2000
    '''
        Amount of quotes per symbol which will be loaded from local storage initially
    '''

    def __init__(self, datapoints, load_lates_quotes, setup_items):
        '''Initialize and wire together all classes
        '''

        self.setup_items = setup_items
        self.datapoints = datapoints
        self.load_lates_quotes = load_lates_quotes
        self.local_storage = Settings.get('LocalStorage')()
        self.quote_repository = Settings.get(
            'QuoteRepository')()
        self.position_repository = Settings.get(
            'PositionRepository')(self.local_storage)
        self.broker = Settings.get('BrokerLocal')()
        self.market = Settings.get('MarketLocal')()

        self.log = Settings.get('Logger')()
        self.setup_manager = Settings.get('SetupManager')()

        self.position_manager = Settings.get('PositionManager')(
            self.market, self.broker, self.position_repository)

        self.symbols = self.setup_manager.extract_symbols_from_setup_items(
            setup_items)

        self.engine = Settings.get('Engine')(self.symbols, self.setup_items,
                                             self.position_manager)

        self.stream_adapter = Settings.get('StreamAdapterLocal')(
            self.symbols, self.broker, self.quote_repository, self.datapoints, load_lates_quotes)

        self.stream_adapter.attach(self.engine, Settings.get('Domain').price)

        self.engine.attach(self.position_manager,
                           Settings.get('Domain').position)
        self.position_manager.attach(self.broker,
                                     Settings.get('Domain').position)

        self.attach(self.stream_adapter, Settings.get('Domain').misc)
        self.stream_adapter.attach(self.quote_repository, Settings.get('Domain').price)
        self.stream_adapter.attach(self.engine, Settings.get('Domain').price)

    def run(self):

        self.notify(Settings.get('Message').start_backtest,
                    Settings.get('Domain').misc)
        self.stream_adapter.run()
