from settings import Settings
from trading_ig.lightstreamer import Subscription
import json
from observer import Observer, Subject
from copy import copy
from datetime import timedelta


class StreamAdapterIG(Subject):
    '''
        Translates the stream received from IG Markets source to a generic local format
    '''

    def __init__(self, symbols, broker, quote_repository, fetch_daily_quotes, load_latest_quotes):

        self.symbols = symbols
        self.broker = broker
        self.log = Settings.get('Logger')()
        self.last_chart_price_items = {}
        self.last_tick_price_items = {}
        self.last_tick = {}
        self.temp_last_tick = {}
        self.quote_repository = quote_repository
        self.is_fetch_daily_quotes = fetch_daily_quotes
        self.is_load_latest_quotes = load_latest_quotes
        self.deal_id = None
        self.deal_reference = None
        self.min_timeframe = Settings.min_time_frame
        self.all_timeframes = Settings.all_timeframes
        self.ticks = {}

    def update(self, subject, message):

        if message == Settings.get('Message').start_live_trading:
            self.init()

    def init(self):

        if self.is_fetch_daily_quotes:
            try:
                self.fetch_daily_quotes()
                pass
            except BaseException as e:
                self.log.error(
                    'Could not update prices from today. Error: %s ' % e)

        if self.is_load_latest_quotes:
            self.load_latest_quotes()

    def load_latest_quotes(self):

        limit = 200
        for symbol in self.symbols:
            rows = self.quote_repository.get_latest_by_symbol(symbol, limit)
            for row in reversed(rows):
                self.quote = self._convert_row_to_quote(row)
                self.notify(Settings.get(
                    'Message').update_quote_preload, Settings.get('Domain').price)

    def run(self):

        try:
            # Ensure configured account is selected
            accounts = self.broker.session[u'accounts']
            for account in accounts:
                if account[u'accountId'] == Settings.broker_account_number:
                    accountId = account[u'accountId']
                    break
                else:
                    print('Account not found: {0}'.format(
                        Settings.broker_account_number))
                    accountId = None
            self.broker.stream_service.connect(accountId)
            self.subscribe_prices(self.symbols)
            self.subscripe_open_position_updates(accountId)

            input("{0:-^80}\n".format("HIT CR TO UNSUBSCRIBE AND DISCONNECT FROM \
                LIGHTSTREAMER"))
        except BaseException as e:
            self.log.error(e)
            self.broker.service.disconnect()
            self.run()

        # Disconnecting
        self.broker.service.disconnect()

    def subscripe_open_position_updates(self, account_id):

        subscription = Subscription(
            mode="DISTINCT",
            items=['TRADE:' + str(account_id)],
            fields=["OPU"]
        )
        subscription.addlistener(self.on_position_update)
        sub_key_account = self.broker.stream_service.ls_client.subscribe(
            subscription
        )

    def subscribe_prices(self, symbols):
        '''
            Subsribes to prices with min timeframe 5min
        '''

        self.log.info("subscribe prices")

        items = []
        charttimeframe = 'SECOND'
        if self.min_timeframe == Settings.get('Interval').m5:
            charttimeframe = '5MINUTE'
        if self.min_timeframe == Settings.get('Interval').m1:
            charttimeframe = '1MINUTE'

        for symbol in symbols:
            epic = self.broker.convert_local_to_broker_symbol(symbol)

            item = 'CHART:' + epic + ':' + charttimeframe 
            items.append(item)

        subscription_prices = Subscription(
            mode="MERGE",
            items=items,
            fields=["UTM", "OFR_OPEN", "OFR_HIGH", "OFR_LOW", "OFR_CLOSE",
                    "BID_OPEN", "BID_HIGH", "BID_LOW", "BID_CLOSE", "CONS_END",  "LTV", "TTV", "CONS_TICK_COUNT", "CONS_END"],
        )
        subscription_prices.addlistener(self.on_prices_update)
        sub_key_account = self.broker.stream_service.ls_client.subscribe(
            subscription_prices
        )

    def convert_price_item_to_quote(self, price_item):

        if not self.is_item_valid(price_item):
            return None

        name = price_item['name']
        epic = name.split(':')[1]
        symbol = self.broker.convert_broker_symbol_to_local(epic)

        datetime = Settings.get('DateService').timestamp_to_datetime(
            int(price_item['values']['UTM']) / 1000)

        quote = Settings.get('Quote')(

            date=datetime,
            offer_open=price_item['values']['OFR_OPEN'],
            offer_high=price_item['values']['OFR_HIGH'],
            offer_low=price_item['values']['OFR_LOW'],
            offer_close=price_item['values']['OFR_CLOSE'],
            bid_open=price_item['values']['BID_OPEN'],
            bid_high=price_item['values']['BID_HIGH'],
            bid_low=price_item['values']['BID_LOW'],
            bid_close=price_item['values']['BID_CLOSE'],
            volume=price_item['values']['CONS_TICK_COUNT'],
            symbol=symbol,
            timestamp=price_item['values']['UTM']
        )

        if price_item['values']['CONS_END'] == '0':
            quote.is_end_of_timeframe == 0
            quote.timeframes = []
            return quote

        quote = self._get_timeframes(quote)
        quote.timeframe = self.min_timeframe

        return quote

    def on_prices_update(self, price_item):

        if price_item['values']['CONS_END'] == '0':
            return

        if not self.is_new_item(price_item):
            return

        tick = self.convert_price_item_to_quote(price_item)
        if not tick:
            return False

        self.tick = tick

        self.add_tick(tick)
        
        if not tick.is_end_of_timeframe:
            self.notify(Settings.get('Message').push_tick, Settings.get('Domain').price)

        if tick.is_end_of_timeframe:

            for timeframe in tick.timeframes:
                if timeframe == self.min_timeframe:
                    self.quote = tick
                    self.timeframe = timeframe
                    self.notify(Settings.get('Message').push_quote, Settings.get('Domain').price)
                    self.notify(Settings.get('Message').update_tick, Settings.get('Domain').price)
                else:
                    quote = self.substitude(tick, timeframe)
                    if quote:
                        self.quote = quote
                        self.timeframe = quote.timeframe
                        self.notify(Settings.get('Message').push_quote, Settings.get('Domain').price)
                        self.notify(Settings.get('Message').update_quote, Settings.get('Domain').price)


    def add_tick(self, tick):
        
        if not tick.symbol in self.ticks:
            self.ticks[tick.symbol] = []

        self.ticks[tick.symbol].append(tick)

    def substitude(self, quote, timeframe):

        if not quote.symbol in self.ticks:
            return False
        
        min_time = None
        result = None
        factor = Settings.get('Interval').get_minutes(timeframe)
        for tick in reversed(self.ticks[quote.symbol]):
            if tick.date == quote.date:
                continue
        
            if not min_time:
                min_time = copy(quote.date) - timedelta(minutes=factor)
            if min_time:
                if tick.date >= min_time and tick.date < quote.date:
                    if not result:
                        result = copy(tick)
                        result.timeframe = timeframe
                        result.timeframes = quote.timeframes
                        result.is_end_of_timeframe = True
                        result.symbol = quote.symbol
                        result.date = min_time
                    else:
                        if tick.offer_high > result.offer_high:
                            result.offer_high = tick.offer_high
                        if tick.offer_low < result.offer_low:
                            result.offer_low = tick.offer_low
                        if tick.bid_high > result.bid_high:
                            result.bid_high = tick.bid_high
                        if tick.bid_low < result.bid_low:
                            result.bid_low = tick.bid_low

                        result.offer_open = tick.offer_open
                        result.bid_open = tick.bid_open
                        result.volume += tick.volume
                else:
                    if result:
                        
                        return result
        return False



    def on_position_update(self, item):

        if item['values']['OPU'] == None:
            return False

        opu = json.loads(item['values']['OPU'])
        epic = opu['epic']
        symbol = self.broker.convert_broker_symbol_to_local(epic)

        if not opu['dealStatus'] == 'ACCEPTED':
            raise BaseException(
                'Could not update position for epic %s' % opu['epic'])

        # TODO: Implement update position
        # if opu['status'] == 'UPDATED':
        #    self.processor.process(Settings.get(
        #        'StreamAction').update_position, opu['dealId'])

        if opu['status'] == 'DELETED':
            self.deal_id = opu['dealId']
            self.deal_reference = opu['dealReference']
            self.bid = self.last_tick_price_items[symbol].bid_close
            self.offer = self.last_tick_price_items[symbol].offer_close
            self.datetime = self.last_tick_price_items[symbol].date
            self.notify(Settings.get('Message').position_deleted_externaly,
                    Settings.get('Domain').position)


    def is_new_item(self, price_item):
        '''
            checks if same item has been sent twice
        '''

        name = price_item['name']

        if not name in self.last_tick_price_items:
            self.last_tick_price_items[name] = price_item['values']['UTM']
            return True
        else:
            last_date = self.last_tick_price_items[name]
            date = price_item['values']['UTM']
            if last_date == date:
                return False
            self.last_tick_price_items[name] = price_item['values']['UTM']
        return True

    def is_item_valid(self, item):

        try:
            if item['values']['OFR_CLOSE'] == '' or item['values']['BID_CLOSE'] == '':
                raise Exception('Item invalid.')
            if item['values']['UTM'] == '':
                raise Exception('No date set.')
            bid = float(item['values']['BID_CLOSE'])
            offer = float(item['values']['OFR_CLOSE'])

        except BaseException as e:
            return False
        return True

    def _get_timeframes(self, tick):

        day = tick.date.day
        hour = tick.date.hour
        minute = tick.date.minute
        timeframes = []

        for timeframe in self.all_timeframes:

            if timeframe == Settings.get('Interval').m1:
                    timeframes.append(Settings.get('Interval').m1)

            if timeframe == Settings.get('Interval').m5:
                if minute % 5 == 0:
                    timeframes.append(Settings.get('Interval').m5)

            if timeframe == Settings.get('Interval').m15:
                if minute % 15 == 0:
                    timeframes.append(Settings.get('Interval').m15)

            if timeframe == Settings.get('Interval').h1:
                if minute == 0:
                    timeframes.append(Settings.get('Interval').h1)

            if timeframe == Settings.get('Interval').h4:
                if minute == 0 and hour % 4 == 0:
                    timeframes.append(Settings.get('Interval').h4)

            if timeframe == Settings.get('Interval').d1:
                if minute == 0 and hour == 0:
                    timeframes.append(Settings.get('Interval').d1)

        tick.timeframes = timeframes

        if not tick.symbol in self.last_tick:
            self.last_tick[tick.symbol] = None

        if not timeframes:
            tick.is_end_of_timeframe = False
            return tick

        last_tick = self.last_tick[tick.symbol]
        if not last_tick:
            tick.is_end_of_timeframe = True
            self.last_tick[tick.symbol] = tick
            return tick

        if last_tick.date.day == day and last_tick.date.hour == hour and last_tick.date.minute == minute:
            tick.timeframes = []
            tick.is_end_of_timeframe = False
            self.last_tick[tick.symbol] = tick
            return tick

        tick.is_end_of_timeframe = True
        tick.timeframes = timeframes
        self.last_tick[tick.symbol] = tick
        return tick

    def fetch_daily_quotes(self):

        results = self.broker.fetch_daily_quotes(self.symbols)
        for result in results:
            for r in result['prices']:
                date = Settings.get('DateService').str_to_datetime(
                    r['snapshotTimeUTC'], Settings.get('DateFormat').IG3)
                quote = Settings.get('Quote')(date=date, offer_open=r['openPrice']['ask'], offer_high=r['highPrice']['ask'], offer_low=r['lowPrice']['ask'], offer_close=r['closePrice']['ask'], bid_open=r['openPrice']['bid'],
                                              bid_high=r['highPrice']['bid'], bid_low=r['lowPrice']['bid'], bid_close=r['closePrice']['bid'], volume=r['lastTradedVolume'], is_end_of_timeframe=True, symbol=result['symbol'], timestamp=date.toordinal)

                self.quote_repository.store(quote)

    def _convert_row_to_quote(self, row):

        return Settings.get('Quote')(
            timestamp=row[2].toordinal(),
            date=row[2], offer_open=row[3], offer_high=row[4], offer_low=row[5], offer_close=row[6], bid_open=row[7],
            bid_high=row[8], bid_low=row[9], bid_close=row[10], volume=row[11], is_end_of_timeframe=False, symbol=row[1]
        )
