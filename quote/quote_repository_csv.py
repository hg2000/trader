import os
import csv
from settings import Settings
from observer import Observer
from file_read_backwards import FileReadBackwards

class QuoteRepository(Observer):



    def __init__(self):

        self.last_quote = {}
        self.base_dir = os.path.dirname(os.path.abspath(__file__)) + '/..'
        self.storage_folder = 'resources/prices/'
        self.cache = {}
 

    def _add_to_cache(self, quote):

        if not quote.symbol in self.cache:
            self.cache[quote.symbol][quote.timeframe] = []

        # reduce list size if its more than 200
        if self.cache[quote.symbol][quote.timeframe] > 300:
            self.cache[quote.symbol][quote.timeframe] = self.cache[quote.symbol][quote.timeframe][-200]
        self.cache[quote.symbol][quote.timeframe].append(quote)

    def update(self, subject, message=None):

        if message == Settings.get('Message').push_tick:
            pass
            
        if message == Settings.get('Message').push_quote:
            self.store(subject.quote)
            pass
            
    def store(self, quote):

        if not quote.timeframe:
            raise BaseException('No timeframe set.')
            
        self._add_to_cache(quote)

        with open(self.filepath(quote.symbol, quote.timeframe), 'a') as csvfile:
            w = csv.writer(csvfile, delimiter=',', quotechar='"',
                           quoting=csv.QUOTE_MINIMAL)
            w.writerow([quote.date.strftime('%Y-%m-%d %H:%M:%S'), quote.symbol, str(quote.offer_open), str(quote.offer_high), str(
                quote.offer_low), str(quote.offer_close), str(quote.bid_open), str(quote.bid_high), str(quote.bid_low), str(quote.bid_close),str(quote.volume)])

    def filepath(self, asset, timeframe):

        return self.storage_folder + asset + '-' + timeframe + '.csv'

    def get_latest_by_symbol(self, symbol, limit, timeframe=None):

        if not timeframe:
            timeframe = Settings.get('Interval').m5

        quotes = Settings.get('Quotes')()
        with open(self.filepath(symbol, timeframe)) as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reversed(list(reader)):
                print(row['first_name'], row['last_name'])

     
