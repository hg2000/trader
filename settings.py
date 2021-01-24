import importlib
from dotenv import load_dotenv
import os

class Settings():

    load_dotenv()

    # Credentials
    broker_username = os.getenv("BROKER_USERNAME")
    broker_password = os.getenv("BROKER_PASSWORD")
    broker_api_key = os.getenv("BROKER_API_KEY")
    broker_account_type = os.getenv("BROKER_ACC_TYPE")
    broker_account_number =os.getenv("BROKER_ACCNUMBER")

    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")
    db_host = os.getenv("DB_HOST")
    db_host = os.getenv("DB_HOST")
    db_database = os.getenv("DB_DATABASE")

    min_time_frame = 'm5'
    #min_time_frame = 'SECOND'

    # Apllication settings
    fetch_price_symbols = [
        'BTCEUR',
        'EURUSD',
        'USDJPY',
        'AUDUSD',
        'USDCAD',
        'EURCHF',
        'GBPEUR',
        'NZDUSD',
        'GBPJPY',
        'EURAUD',
        'GBPUSD',
        'USDJPY',
        'EURGBP',
        'EURJPY',
        'USDCHF',
        'USDZAR',
        'USDSGD',
        'AUDJPY',
        'NZDUSD',
        'NZDJPY',
        'NOKJPY',
        'EURSEK',
        'EURTRY',
        'MXNJPY',
        'EURMXN',
        'CHFHUF',
        'USDRUB',
        'GOLD',
    ]

    #fetch_price_symbols = ['EURAUD']

    load_latest_quotes = True if os.getenv("LOAD_LATEST_QUOTES") == 'true' else False
    fetch_daily_quotes = True if os.getenv("FETCH_DAILY_QUOTES") == 'true' else False

    all_timeframes = [  'm5', 'm15', 'h1', 'h4', 'd1']

    # Classes
    Action = 'action.Action'

    BacktestEngine = 'engine.backtest.BacktestEngine'
    
    BacktestAdapter = 'connections.backtest_adapter.BacktestAdapter'

    Backtester = 'optimization.backtester.Backtester'
    
    Broker = 'connections.broker.Broker'
    
    BrokerLocal = 'connections.broker_local.BrokerLocal'
    
    Command = 'action.Command'
    
    DateService = 'service.dateservice.Dateservice'

    DateFormat = 'service.dateservice.Format'
    
    Direction = 'position_manager.position.Direction'

    Domain = 'observer.Domain'

    Engine = 'engine.trading_engine.TradingEngine'

    EnvironmentBacktest  = 'environment.backtest.EnvironmentBacktest'

    EvaluatorBacktest = 'evaluation.evaluator_backtest.Evaluator'

    EventManager = 'event_manager.EventManager'

    FileService = 'service.fileservice.FileService'

    Indicator = 'indicators.indicator.Indicator'
    
    Interval = 'interval.Interval'

    MarketLocal = 'market.test_market.TestMarket'

    MissingDataException = 'exceptions.exceptions.MissingDataException'
    
    LiveEvaluator = 'evaluation.evaluator_live.EvaluatorLive'

    LiveEnvironment = 'environment.live.LiveEnvironment'    
    
    LiveMarket = 'market.live_market.LiveMarket'

    LocalStorage = 'connections.db.Db'
    
    Logger = 'service.logger.Logger'

    Message = 'observer.Message'

    Mode = 'setup_manager.setup.Mode'

    Optimizer  = 'optimization.optimizer.Optimizer'

    Observer = 'observer.Observer'

    Parameters = 'setup_manager.setup.Parameters'

    ParametersJsonEncoder = 'setup_manager.setup.ParametersJsonEncoder'
    
    Position = 'position_manager.position.Position'

    PositionManager = 'position_manager.position_manager.PositionManager'
    
    PositionRepository = 'position_manager.position_repository.PositionRepository'

    PriceRepository = 'price.price_repository.PriceRepositoryCsv'

    Processor = 'engine.processor.Processor'

    ProcessorBacktest = 'engine.processor_backtest.ProcessorBacktest'
    
    Quote = 'quote.quote.Quote'

    Quotes = 'quote.quotes.Quotes'

    Result = 'setup_manager.setup.Result'

    Subject = 'oberserver.Subject'

    QuoteRepositoryTest = 'quote.quote_repository.QuoteRepositoryTest'
    
    QuoteRepository = 'quote.quote_repository_csv.QuoteRepository'
    
    SetupItem = 'setup_manager.setup.SetupItem'
    
    SetupManager = 'setup_manager.setup_manager.SetupManager'

    Strategy_Breakout = 'strategy.breakout.Breakout'

    StreamAdapter = 'connections.stream_adapter.StreamAdapterIG'

    StreamAdapterLocal = 'connections.stream_adapter_local.StreamAdapterLocal'

    StreamAction =  'engine.processor.StreamAction'

    TestPositionManager = 'position_manager.test_position_manager.TestPositionManager'

    UnittestEnvironment = 'environment.unittest.UnittestEnvironment'


    @staticmethod
    def get(name):
        '''
            Returns class ready to be initialized
        '''

        path = getattr(Settings, name)
        modulename_list = path.split('.')
        classname = modulename_list.pop()   
        modulname = '.'.join(modulename_list)

        module = importlib.import_module(modulname)
        class_item = getattr(module, classname)
        return class_item

