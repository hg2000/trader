from settings import Settings


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

    def __init__(self, position_manager, price_manager, setup_item):

        self.strategies = {}
        self.position_manager = position_manager
        self.price_manager = price_manager
        self.setup_item = setup_item
        self.log = Logger()
        self.start_date = None
        self.end_date = None
        self.show_chart = True

    def evaluate(self):

        setup_item = self._calculate(
            self.position_manager.closed_positions, self.setup_item)

        if self.show_chart:
            self.print_chart(setup_item)

        self.show_result(setup_item)

        return setup_item

    def show_result(self, setup_item):

        from pprint import pprint
        pprint(setup_item.symbol)
        pprint(setup_item.result.start_time + ' - ' + setup_item.result.end_time)
        pprint(setup_item.result)

        pprint('----------')


    def print_chart(self, setup_item):

        symbol = setup_item.symbol
        timeframe = setup_item.parameters.timeframe
        strategy_name = setup_item.strategy_name

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
        quotes = self.price_manager.get_last_quotes(symbol, n, timeframe)
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

        '''
        for key in lines:
            dfline = pd.DataFrame(lines[key], columns=["date", key])
            fig.add_trace(
                go.Scatter(x=dfline['date'], y=dfline[key], name=key)
            )
        '''

        fig.update_layout(
            title=strategy_name,
            yaxis_title=symbol + ' / ' + timeframe,
            shapes=shapes,
            annotations=annotations
        )

        fig.show()


    def _calculate(self, positions, setup_item):

        amount_trades = 0
        wins = 0
        losses = 0
        result_pips = 0
        drawdown = 0
        result_per_trade = 0

        for id in positions:
            position = positions[id]
            if not position.setup_item == setup_item:
                continue
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

        result_item = Result()
        result_item.start_time = self.price_manager.quotes[setup_item.symbol].tick_df[0].date.strftime('%y-%m-%d %H:%M')
        result_item.end_time = self.price_manager.quotes[setup_item.symbol].tick_df[-1].date.strftime('%y-%m-%d %H:%M')
        result_item.amount_trades = amount_trades
        result_item.wins = wins
        result_item.losses = losses
        result_item.result_pips = result_pips
        result_item.drawdown = drawdown
        result_item.result_per_trade = result_per_trade
        setup_item.result = result_item

        return setup_item
