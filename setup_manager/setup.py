from settings import Settings
from json import JSONEncoder
import json
from datetime import datetime


class Mode:

    live = 'LIVE'
    paused = 'PAUSED'


class Result:

    start_time: str
    end_time: str
    amount_trades: int
    wins: int
    losses: int
    result_pips: float
    drawdown: float
    result_per_trade: float

    def __repr__(self):

        result = ''

        #if self.start_time:
        #    result = 'start time: %s, ' % self.start_time
        #if self.end_time:
        #    result += 'end time: %s, ' % self.end_time
        result += 'amount_trades: %s, ' % self.amount_trades
        result += 'wins: %s, ' % self.wins
        result += 'losses: %s, ' % self.losses
        result += 'result_pips: %s, ' % self.result_pips
        result += 'result_per_trade: %s, ' % self.result_per_trade
        return result

    def __str__(self):
        return self.__repr__()

    def from_json(self, json_item):

        for key in json_item:
            self.__setattr__(key, json_item[key])
        return self


class Parameters:

    def __init__(self):

        self.window_breakout: None
        self.timeframe: None
        self.stop: None
        self.trailing: None
        self.limit: None

    def from_json(self, json_item):

        for key in json_item:
            self.__setattr__(key, json_item[key])
        return self


    def __str__(self):

        v = vars(self)
        s = ''
        for key in v:
            s += str(key) + ': ' + str(v) + '. '
        return s

    


class SetupItem:

    strategy_name: str
    mode: Mode
    symbols: []
    symbol: str
    parameters: Parameters
    result: Result

    def init_with_json_object(self, json_object):

        self.strategy_name = json_object['name']
        if json_object['mode'] == 'live':
            self.mode = Mode.live
        if json_object['mode'] == 'paused':
            self.mode = Mode.paused
        self.symbols = json_object['symbols']

        parameters = Parameters()
        parameters.limit = json_object['parameters']['limit']
        parameters.stop = json_object['parameters']['stop']
        parameters.timeframe = json_object['parameters']['timeframe']
        parameters.trailing = json_object['parameters']['trailing']
        parameters.window_breakout = json_object['parameters']['window_breakout']
        self.parameters = parameters

    def get_parameter_keys(self):

        parameters = dir(self.parameters)
        result = []
        for parameter in parameters:
            if not parameter[:2] == '__' and not parameter[-2:] == '__' and not parameter == 'from_json':
                result.append(parameter)
        return result

    def get_parameters_to_optimize(self):

        parameters_to_optimize = []
        parameters = self.get_parameter_keys()

        for parameter_key in parameters:
            p = getattr(self.parameters, parameter_key)
            if isinstance(p, (list)):
                if len(p) > 1:
                    parameters_to_optimize.append(parameter_key)

        return parameters_to_optimize

    def __hash__(self):

        parameters = dir(self.parameters)
        parameter_string = ''
        for key in parameters:
            parameter_string += key
            parameter_string += str(getattr(self.parameters, key))

        parameter_string += self.strategy_name
        parameter_string += self.symbol

        return hash(parameter_string)

    def to_json(self):

        attributes = vars(self)
      
        if 'result' in attributes:
            attributes['result'] = vars(attributes['result'])
            if isinstance(attributes['result']['start_time'], datetime):
                attributes['result']['start_time'] = Settings.get(
                    'DateService').datetime_to_str(attributes['result']['start_time'])
            if isinstance(attributes['result']['end_time'], datetime):
                attributes['result']['end_time'] = Settings.get(
                    'DateService').datetime_to_str(attributes['result']['end_time'])
        if 'parameters' in attributes:
            attributes['parameters'] = vars(attributes['parameters'])
           
            pass

        result = json.dumps(attributes)
        return result

    def from_json(self, json_item):

        json_item = json.loads(json_item)
        if 'parameters' in json_item:
            json_item['parameters'] = Settings.get(
                'Parameters')().from_json(json_item['parameters'])
        if 'result' in json_item:
            json_item['result'] = Settings.get(
                'Result')().from_json(json_item['result'])

        for key in json_item:
            self.__setattr__(key, json_item[key])
        return self
