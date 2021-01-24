from settings import Settings
import os
import csv


class PriceRepositoryCsv:

    def __init__(self):

        self.base_dir = os.path.dirname(os.path.abspath(
            __file__)) + '/../resources/prices/%s-%s.csv'

    def get_last_quotes(self, symbol, timeframe, amount):

        content = self._get_csv(symbol, timeframe)
        next(content)

        count = 1
        result = []
        for row in reversed(list(content)):
            result.append(row)
            if count == amount:
                break
            count += 1
        return result

    def _get_csv(self, symbol, timeframe):

        path = self.base_dir % (symbol, timeframe)
        if not os.path.isfile(path):
            raise 'File % does not exist' % path
        csv_file = open(path)
        resource = csv.reader(csv_file, delimiter=',')
        return resource
