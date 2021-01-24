from settings import Settings
from observer import Subject


class LiveEnvironment(Subject):
    '''
     Initiates all classes needed for running backtests
    '''
    lates_quotes_limit = 2000
    '''
        Amount of quotes per symbol which will be loaded from local storage initially
    '''

    def __init__(self):

        fetch_daily_quotes = Settings.fetch_daily_quotes
        load_latest_quotes = Settings.load_latest_quotes

        self.local_storage = Settings.get('LocalStorage')()
        self.quote_repository = Settings.get(
            'QuoteRepository')()

        self.position_repository = Settings.get(
            'PositionRepository')(self.local_storage)

        self.setup_manager = Settings.get('SetupManager')()
        self.symbols = self.setup_manager.get_fetch_price_symbols()
        self.broker = Settings.get('Broker')(self.symbols)
        self.market = Settings.get('LiveMarket')(self.broker)
        self.evaluator = Settings.get('LiveEvaluator')()
        self.log = Settings.get('Logger')()

        self.position_manager = Settings.get('PositionManager')(
            self.market, self.broker, self.position_repository)

        self.setup_items = self.setup_manager.load_live_setups()
        self.engine = Settings.get('Engine')(
            self.symbols, self.setup_items, self.position_manager)
        self.stream_adapter = Settings.get('StreamAdapter')(
            self.symbols, self.broker, self.quote_repository, fetch_daily_quotes, load_latest_quotes)

        self.engine.attach(self.position_manager,
                           Settings.get('Domain').position)
        self.position_manager.attach(self.broker,
                                     Settings.get('Domain').position)
        self.attach(self.stream_adapter, Settings.get('Domain').misc)
        self.attach(self.position_manager, Settings.get('Domain').misc)
        self.attach(self.position_repository, Settings.get('Domain').position)

        self.stream_adapter.attach(
            self.quote_repository, Settings.get('Domain').price)
        self.stream_adapter.attach(self.engine, Settings.get('Domain').price)

    def run(self, fetch_daily_quotes=True, load_lates_quotes=True):

        self.notify(Settings.get('Message').start_live_trading,
                    Settings.get('Domain').misc)

        self.stream_adapter.run()
