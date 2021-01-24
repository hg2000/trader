from settings import Settings
import json
import copy

class Optimizer():

    def __init__(self):
        
        self.setup_manager = Settings.get('SetupManager')()
        self.start = ''
        self.end = ''

    def optimize(self, datapoints,load_lates_quotes):

        unexpanded_setup_items = self.setup_manager.load_unexpanded_setup()
        setup_items = self.setup_manager.expand_setup_items(unexpanded_setup_items)
        groups = self.setup_manager.group_setup_items_by_strategy(setup_items)
        
        for group_name in groups:
            setup_items_group = groups[group_name]
            setup_items_with_result = self._run(group_name, setup_items_group, datapoints, load_lates_quotes)
            #self.setup_manager.save_results(setup_items_with_result)
            #optimized_setup_items= self.select_optimum(setup_items_with_result)
            #self.setup_manager.save_optimized_setup_items(optimized_setup_items)

            
    def select_optimum(self, setup_items):

        selected = {}
        for i in setup_items:
        
            symbol = i.symbol
            if not symbol in selected:
                selected[symbol] = i

            if i.result.result_pips > selected[symbol].result.result_pips:
                selected[symbol] = i

        list_selected = []
        for symbol in selected:
            if selected[symbol].result.result_pips:
                selected[symbol].mode = Settings.get('Mode').paused
            list_selected.append(selected[symbol])
        return list_selected
        
    def _run(self, strategy_name, setup_items, datapoints, load_lates_quotes):

        environment = Settings.get('EnvironmentBacktest')(datapoints, load_lates_quotes, setup_items)
        environment.run()
        evaluator = environment.evaluator

        
        
        evaluator.strategy_name = strategy_name
        result = evaluator.evaluate(setup_items)
       
        from copy import deepcopy
        result_copy = deepcopy(result)

    
        evaluator.print_chart()

        from pprint import pprint
   
        for r in result_copy:

           
                pprint(r.result)
                print(r.symbol)
                print(r.parameters.timeframe)
                pprint('---')
            
        return result
        
    def extract_symbols_from_setup(self, setup):

        symbols = []
        for asset in setup['assets']:
            if not asset['symbol'] in symbols:
                symbols.append(asset['symbol'])
        return symbols

    def extract_parameters_to_optimize(self, parameters):

        parameters_to_optimize = {}
        for key in parameters:
            if isinstance(parameters[key], (list) ):
                if len(parameters[key]) > 1:
                    parameters_to_optimize[key] = parameters[key]
             
        return parameters_to_optimize


    
