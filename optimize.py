from settings import Settings

if __name__ == '__main__':

    datapoints = 5000
    optimizer = Settings.get('Optimizer')()
    optimizer.optimize(datapoints, load_lates_quotes=Settings.load_latest_quotes)