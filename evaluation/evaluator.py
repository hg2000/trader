
from quote.quote import Quote
from quote.quotes import Quotes
from position_manager.position import Direction, Position
from service.logger import Logger
from setup_manager.setup import Result
from pandas import pandas as pd
import matplotlib.pyplot as plt
from mpl_finance import candlestick_ohlc
from settings import Settings
import matplotlib.dates as dates
from observer import Observer

import plotly.graph_objects as go
import plotly.express as px


class Evaluator(Observer):

    def __init__(self, position_manager, price_manager):

        self.strategies = {}
        self.position_manager = position_manager
        self.price_manager = price_manager
        self.log = Logger()

    def update(self, subject, message=None):

        if message=='opened position':
            a=1

    def add_strategy(self, setup_item):

        item_hash = hash(setup_item)
        if not item_hash in self.strategies:
            self.strategies[item_hash] = {}
            self.strategies[item_hash]['quotes'] = Quotes()
            self.strategies[item_hash]['positions'] = []
            self.strategies[item_hash]['setup_item'] = setup_item

    def add_quote(self, quote, setup_item):

        hash_value = hash(setup_item)
        self.strategies[hash_value]['quotes'].add_quote(quote)

    def get_time_period(self, setup_item):

        item_hash = hash(setup_item)
        length = self.strategies[item_hash]['quotes'].length()
        start = None
        end = None
        if self.strategies[item_hash]['quotes'].df:
            start = self.strategies[item_hash]['quotes'].df[0].date
            end = self.strategies[item_hash]['quotes'].df[length-1].date
        return (start, end)

    def add_open_position(self, position):

        hash_value = hash(position.setup_item)
        position.hash = hash_value
        index = self.strategies[hash_value]['quotes'].length()-1
        if position.direction == Direction.sell:
            self.strategies[hash_value]['quotes'].df[index].open_short = position.open_price

        if position.direction == Direction.buy:
            self.strategies[hash_value]['quotes'].df[index].open_long = position.open_price

        self.log.info('Open position %s ' % position.symbol)

    def add_close_position(self, position):

        hash_value = hash(position.setup_item)
        index = self.strategies[hash_value]['quotes'].length()-1
        if position.direction == Direction.sell:
            self.strategies[hash_value]['quotes'].df[index].close_short = position.close_price

        if position.direction == Direction.buy:
            self.strategies[hash_value]['quotes'].df[index].close_long = position.close_price

        self.strategies[hash_value]['positions'].append(position)
        self.log.info('Close position %s, result: %s' %
                      (position.symbol, position.result_pips))


    def evaluate(self, setup_items):

        positions = self.position_manager.closed_positions
        results = []
        
        for setup_item in setup_items:
            filtered_positions = self.filter_positions_by_setup_item(positions, setup_item)
            if filtered_positions:
                results.append(self._calculate(filtered_positions, setup_item))

        return results
    def filter_positions_by_setup_item(self, positions, setup_item):
        filtered_positions = []
    
        for id in positions:
            if setup_item == positions[id].setup_item:
                filtered_positions.append(positions[id])
        return filtered_positions
        
    def evaluate2(self):

        results = {}

        sessions = self.order_positions_by_sessions()
        from copy import deepcopy

        for session in sessions:
            if not session in results:
                results[session] = []

            for hash_value in sessions[session]:
                ps = sessions[session][hash_value]['positions']
                ss =sessions[session][hash_value]['setup_item']
                setup_item = self._calculate(
                    positions=ps,
                    setup_item=ss
                )
                results[session].append(deepcopy(setup_item))

        self.print_chart()
        return results

    def order_positions_by_sessions(self):

        sessions = {
            'sydney': {},
            'tokyo': {},
            'london': {},
            'newyork': {}
        }

        for hash_value in self.strategies:
        setup_item.result = result_item
            for session in sessions:
                if not hash_value in sessions[session]:
                    sessions[session][hash_value] = {
                        'positions': [],
                        'quotes': self.strategies[hash_value]['quotes'],
                        'setup_item': self.strategies[hash_value]['setup_item'],
                    }
            for position in self.strategies[hash_value]['positions']:
                hour = position.open_time.hour
                if hour >= 12 and hour < 21:
                    sessions['newyork'][hash_value]['positions'].append(
                        position)

                if hour >= 23 or hour < 8:
                    sessions['tokyo'][hash_value]['positions'].append(position)

                if hour >= 21 or hour < 6:
                    sessions['sydney'][hash_value]['positions'].append(
                        position)

                if hour >= 7 and hour < 16:
                    sessions['london'][hash_value]['positions'].append(
                        position)

        return sessions

    def _calculate(self, positions, setup_item):

        amount_trades = 0
        wins = 0
        losses = 0
        result_pips = 0
        drawdown = 0
        result_per_trade = 0

        for position in positions:
            amount_trades += 1
            result_pips += position.result_pips
            if position.result_pips > 0:
                wins += 1
            else:
                losses += 1
                if result_pips < drawdown:
                    drawdown = result_pips

        if amount_trades > 0:
            result_per_trade = result_pips / amount_trades

        #period = self.get_time_period(setup_item)

        result_item = Result()
        #result_item.start_time = period[0]
        #result_item.end_time = period[1]
        result_item.amount_trades = amount_trades
        result_item.wins = wins
        result_item.losses = losses
        result_item.result_pips = result_pips
        result_item.drawdown = drawdown
        result_item.result_per_trade = result_per_trade

        return setup_item

    def print(self):

        a = 1

    def print_chart(self):

        symbol = 'EURUSD'
        timeframe = 'm15'
        strategy_name = 'Breakout'

        positions = []
        annotations = []
        shapes = []
        
        for key in self.position_manager.closed_positions:
            position = self.position_manager.closed_positions[key]
            if position.symbol == symbol and position.setup_item.parameters.timeframe == timeframe:

                shape = dict(
                    x0=Settings.get('DateService').datetime_to_str(
                        position.open_time, Settings.get('DateFormat').YMDHM),
                    x1=Settings.get('DateService').datetime_to_str(
                        position.close_time, Settings.get('DateFormat').YMDHM),
                    y0=0,
                    y1=1,
                    xref='x',
                    yref='paper',
                    line_width=2)

                annotation = dict(
                    x=Settings.get('DateService').datetime_to_str(
                        position.open_time, Settings.get('DateFormat').YMDHM),
                    y=0.05,
                    xref='x',
                    yref='paper',
                    showarrow=False,
                    xanchor='left',
                    text="OPEN: " + str(position.open_price) + " CLOSE: " + str(position.close_price) +
                    " " + position.direction + ', Result Pips: ' +
                    str(int(position.result_pips))
                )
                shapes.append(shape)
                annotations.append(annotation)

        n = self.price_manager.get_amount_quotes(symbol)
        quotes = self.price_manager.get_last_quotes(symbol,n, timeframe)
        rows = []
        i = 1

        lines = {}
        for quote in quotes:
            for key in quote.lines:
                if not key in lines:
                    lines[key] = []
                lines[key].append([quote.date, quote.lines[key]])

            row = tuple([quote.date, quote.bid_open,
                         quote.bid_high, quote.bid_low, quote.bid_close])
            rows.append(row)
            i += 1

        from pprint import pprint

        df = pd.DataFrame(
            rows, columns=['date', 'open', 'high', 'low', 'close'])

        fig = go.Figure(
            data=[go.Candlestick(x=df['date'],
                                 open=df['open'],
                                 high=df['high'],
                                 low=df['low'],
                                 close=df['close'])],
            layout={"title": {"text": symbol + " / " + timeframe}}
        )

        for key in lines:
            dfline = pd.DataFrame(lines[key], columns=["date", key])
            fig.add_trace(
                go.Scatter(x=dfline['date'], y=dfline[key], name=key)
            )
        '''
        dfema25 = pd.DataFrame(ema25, columns=["date", "ema"])
        fig.add_trace(
            go.Scatter(x=dfema25['date'], y=dfema25['ema'], name="EMA")
            )

        '''

        fig.update_layout(
            title=strategy_name,
            yaxis_title=symbol + ' / ' + timeframe,
            shapes=shapes,
            annotations=annotations
        )

        fig.show()

        pass
