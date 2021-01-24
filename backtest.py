from settings import Settings

if __name__ == '__main__':

    datapoints = 5000
    backtester = Settings.get('Backtester')()
    backtester.show_chart = False
    backtester.backtest('Breakout', datapoints )