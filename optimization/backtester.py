from settings import Settings


class Backtester():

    show_chart = None    
    def __init__(self):

        self.setup_manager = Settings.get('SetupManager')()
        self.show_chart = True
        self.fileservice = Settings.get('FileService')()

    def backtest(self, strategy, datapoints, symbols=None):

        setup_items = self.setup_manager.load_unexpanded_setup()
        for setup_item in setup_items:
            if setup_item.strategy_name == strategy:
                break

        if symbols:
            setup_item.symbols = symbols

        expanded_setup_items = self.setup_manager.expand_setup_items(setup_items)
        environment = Settings.get('EnvironmentBacktest')(datapoints, True, expanded_setup_items)
        environment.run()

        for setup_item in expanded_setup_items:
            evaluator = Settings.get('EvaluatorBacktest')(environment.position_manager, environment.price_manager, setup_item)
            evaluator.show_chart = self.show_chart
            setup_item = evaluator.evaluate()
            j = setup_item.to_json()
            filename = setup_item.strategy_name + '-' + setup_item.parameters['timeframe'] + '-' + setup_item.symbol + '.json'
            self.fileservice.save_string('/setup/backtested/' + filename, j)
            pass