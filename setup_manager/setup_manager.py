from settings import Settings
from copy import deepcopy
import os
import json


class SetupManager():

    def __init__(self):

        self.path_setup_unoptimized = '/setup/strategies'
        self.path_setup_optimized = '/setup/optimized/opt.json'
        self.path_setup_live = '/setup/live'
        self.path_result = '/setup/results/'
        self.file_service = Settings.get('FileService')()

    def load_optimized_setup_items(self):

        json_items = self.file_service.load_json(self.path_setup_optimized)
        setup_items = []

        for item in json_items:
            setup_items.append(Settings.get('SetupItem')().from_json(item))
        return setup_items

    def load_live_setups(self):

        files = self.file_service.get_files_in_folder(self.path_setup_live)
        setup_items =  []
        for file in files:
            item =self.file_service.load_string(file, False)
            setup_items.append(Settings.get('SetupItem')().from_json(item))
       
        return setup_items

    def load_result_setup_items(self):

        from os import listdir
        from os.path import isfile, join
        files = self.file_service.get_files_in_folder('/setup/results')
        result = {}
        for f in files:
            name = f.split('/').pop()
            name = name.replace('.json', '')
            json_items = self.file_service.load_json(f, False)
            setup_items = []

            for item in json_items:
                setup_items.append(Settings.get('SetupItem')().from_json(item))
            
            result[name] = setup_items
        return result

    

    def load_unexpanded_setup(self):
        '''
            Loads the raw setup files without which will be the input
            for the optimization process
        '''

        files = self.file_service.get_files_in_folder(
            self.path_setup_unoptimized)

        setup_items = []
        for file_path in files:
            setup_json_item = self.file_service.load_json(
                file_path=file_path, is_path_relative=False)
            setup_item = Settings.get('SetupItem')()
            setup_item.init_with_json_object(setup_json_item)
            setup_items.append(setup_item)

        return setup_items

    def group_setup_items_by_strategy(self, setup_items):

        groups = {}
        for item in setup_items:
            strategy_name = item.strategy_name

            if not strategy_name in groups:
                groups[strategy_name] = []

            groups[strategy_name].append(item)
        return groups

    def extract_symbols_from_setup_items(self, setup_items):

        unique_symbols = []
        for item in setup_items:
            for symbol in item.symbols:
                if not symbol in unique_symbols:
                    unique_symbols.append(symbol)

        return unique_symbols

    def extract_timeframes_from_setup_items(self, setup_items):

        unique_timeframes = []
        for item in setup_items:
            timeframe = item.parameters.timeframe
            if not timeframe in unique_timeframes:
                    unique_timeframes.append(timeframe)

        return unique_timeframes

    def expand_setup_items(self, setup_items):
        '''
            Walks throgh the setup items, if an item contains variants
            expand it to single setup items
        '''

        expanded_setup_items = []
        for item in setup_items:
            expanded_items = self.expand_item(item)
            for expanded_item in expanded_items:
                expanded_setup_items.append(expanded_item)

        if not expanded_setup_items:
            # we only have one item without any optimization instructions
            setup_item = setup_items[0]
            for symbol in setup_item.symbols:
                cloned = deepcopy(setup_item)
                cloned.symbol = symbol
                expanded_setup_items.append(cloned)

        return expanded_setup_items

    def expand_item(self, item):

        parameters_to_optimize = item.get_parameters_to_optimize()
        expanded_items = self._combine(item, parameters_to_optimize)

        result_items = []
        for symbol in item.symbols:
            items_copy = deepcopy(expanded_items)
            for item in items_copy:
                item.symbol = symbol
                result_items.append(item)
        return result_items

    def get_fetch_price_symbols(self):

        return Settings.fetch_price_symbols

    def _combine(self, item, parameters_to_optimize, items=[]):
        '''
            expands the setups which contain variants to a flat data structure
        '''

        if not parameters_to_optimize:
            return items

        parameter_to_optimize = parameters_to_optimize.pop(0)
        values = getattr(item.parameters, parameter_to_optimize)

        if not items:
            for value in values:
                new_item = deepcopy(item)
                setattr(new_item.parameters, parameter_to_optimize, value)
                items.append(new_item)
            return self._combine(item, parameters_to_optimize, items)

        if items:
            items_template = deepcopy(items)
            items = []

            for value in values:
                items_copy = deepcopy(items_template)
                for item_copy in items_copy:
                    setattr(item_copy.parameters, parameter_to_optimize, value)
                    items.append(item_copy)

            return self._combine(item, parameters_to_optimize, items)

    def save_optimized_setup_items(self, setup_items):

        setup_items = deepcopy(setup_items)
        setup_items_json = []
        for setup_item in setup_items:
            setup_items_json.append(setup_item.to_json())

        self.file_service.save_json(
            self.path_setup_optimized, setup_items_json)

    def save_results(self, sessions):

        result = {}
        for session in sessions:
            setup_items_json = []
            sessions_copy = deepcopy(sessions[session])
            for setup_item in sessions_copy:
                setup_items_json.append(setup_item.to_json())
            result[session] = setup_items_json
            

        for session in result:
            self.file_service.save_json(
                self.path_result + session + '.json' , result[session]) 
