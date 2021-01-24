from settings import Settings
from trading_ig import (IGService, IGStreamService)
from observer import Observer, Subject


class Broker(Subject, Observer):

    def __init__(self, symbols):

        self.service = IGService(
            Settings.broker_username, Settings.broker_password, Settings.broker_api_key, Settings.broker_account_type
        )
        self.symbols = symbols
        self.stream_service = IGStreamService(self.service)
        self.session = self.stream_service.create_session()
        self.log = Settings.get('Logger')()
        self.market = {}

    def update(self, subject, message):

        if message == Settings.get('Message').start_live_trading:
            self.fetch_daily_quotes(self.symbols)

        if message == Settings.get('Message').position_opened:
            self.push_open_position(subject.position)

        if message == Settings.get('Message').position_closed:
            self.push_close_position(subject.position)

    def push_open_position(self, position):

        min_stop = self.get_min_stop(position.symbol)
        currency_code = self.get_currency_code(position.symbol)
        scaling_factor = self.scaling_factor(position.symbol)
        stop_distance = position.stop_pips
        stop_order = position.stop_pips
        if stop_order < min_stop:
            stop_order = min_stop

        epic = self.convert_local_to_broker_symbol(position.symbol)

        if position.direction == Settings.get('Direction').buy:
            direction = 'BUY'
        if position.direction == Settings.get('Direction').sell:
            direction = 'SELL'

        deal = self.service.create_open_position(
            currency_code=currency_code,
            direction=direction,
            epic=epic,
            expiry='-',
            force_open='true',
            guaranteed_stop='false',
            level=None,
            limit_distance=None,
            limit_level=None,
            order_type='MARKET',
            quote_id=None,
            size=position.size,
            stop_distance=stop_order,
            stop_level=None,
            trailing_stop='false',
            trailing_stop_increment=None,
        )

        if deal['dealStatus'] == 'REJECTED':
            raise Exception('Open position. Deal Rejected for' +
                            deal['epic'] + ' Reason: ' + deal['reason'] + '; direction: ' + position.direction)
        position.id = deal['dealId']
        position.reference = deal['dealReference']
        position.open_time = Settings.get('DateService').str_to_datetime(
            deal['date'], Settings.get('DateFormat').IG)

        position.open_price = deal['level']
        self.position = position
        self.notify(Settings.get('Message').pushed_open_position,
                    Settings.get('Domain').position)
        return position

    def _send_close_request(self, position, direction):

        return self.service.close_open_position(
            deal_id=position.id,
            direction=direction,
            epic=None,
            expiry='-',
            level=None,
            order_type='MARKET',
            quote_id=None,
            size=position.size
        )

    def push_close_position(self, position):

        if position.direction == Settings.get('Direction').buy:
            direction = 'SELL'
        if position.direction == Settings.get('Direction').sell:
            direction = 'BUY'

        try:
            result = self._send_close_request(position, direction)
        except BaseException as e:
            if e.args[0] == '{"errorCode":"error.service.marketdata.position.notional.details.null.error"}':
                self.log.info('Position already closed externally')
            else:
                self.log.error(e)

            return False

        if result['dealStatus'] == 'REJECTED':

            if result['reason'] == 'POSITION_ALREADY_EXISTS_IN_OPPOSITE_DIRECTION':
                if direction == 'BUY':
                    direction = 'SELL'
                else:
                    direction = 'BUY'
                try:
                    result = self._send_close_request(position, direction)
                except BaseException as e:
                    self.log.error(e)
                    raise BaseException(str(result['reason']))

        self.log.info('Closed. SYMBOL: ' + position.symbol + ' Position open price: ' + str(
            position.open_price) + ' Position close price: ' + str(position.close_price))
        self.log.info(': ' + str(result['profit']))


        self.position = position
        

        self.notify(Settings.get('Message').pushed_close_position,
                    Settings.get('Domain').position)
        return position

    def fetch_market_by_symbol(self, symbol):

        epic = self.convert_local_to_broker_symbol(symbol)
        return self.service.fetch_market_by_epic(epic)

    def fetch_open_positions(self):
        '''
            Fetches open positions from broker
            you still need to enhance these positions with information about strategy,timeframe etc
        '''

        items = self.service.fetch_open_positions()
        position_items = items['positions']

        positions = []
        for item in position_items:
            position = Settings.get('Position')()
            position.id = item['position']['dealId']
            positions.append(position)
        return positions

    def fetch_closed_positions(self):

        period = 60 * 60 * 24 * 7  # one week
        items = self.service.fetch_transaction_history(
            max_span_seconds=period, page_size=9999999)
        position_items = items['transactions']
        positions = []
        for item in position_items:
            if item['transactionType'] == 'TRADE':
                position = Settings.get('Position')()
                position.reference = item['reference']
                positions.append(position)
        return positions

    def fetch_daily_quotes(self, symbols):

        results = []

        for symbol in symbols:
            epic = self.convert_local_to_broker_symbol(symbol)
            resolution = 'MINUTE_5'
            num_points = 20
            # yyyy-MM-dd HH:mm:ss
            now = Settings.get('DateService').now()
            start = now.strftime('%Y-%m-%d')
            response = self.service.fetch_historical_prices_by_epic(
                epic=epic, resolution=resolution, start_date=start, pagesize=999, numpoints=999)

            results.append({
                'symbol': symbol,
                'prices': response['prices']
            })

        return results

    def convert_broker_symbol_to_local(self, name):
        '''
            Converts an IG Markets Epic to Symbol

        '''

        if name == 'IR.D.BOND100.FWM2.IP':
            return 'TBOND'

        if name == 'CS.D.CFDGOLD.CFDGC.IP':
            return 'GOLD'

        if name == 'CC.D.VIX.UME.IP':
            return 'VIX'

        if name == 'IX.D.SPTRD.IFE.IP':
            return 'SP500'

        if name == 'CS.D.BITCOIN.CFE.IP':
            return 'BTCEUR'

        if name == 'CC.D.LCO.UNC.IP':
            return 'BRENTOIL'

        if name == 'CS.D.COPPER.MINI.IP':
            return 'COPPER'

        parts = name.split('.')
        symbol = parts[2]

        return symbol

    def convert_local_to_broker_symbol(self, symbol):

        if symbol == 'BRENTOIL':
            return 'CC.D.LCO.UNC.IP'

        if symbol == 'TBOND':
            return 'IR.D.BOND100.FWM2.IP'

        if symbol == 'GOLD':
            return 'CS.D.CFDGOLD.CFDGC.IP'

        if symbol == 'VIX':
            return 'CC.D.VIX.UME.IP'

        if symbol == 'SP500':
            return 'IX.D.SPTRD.IFE.IP'

        if symbol == 'BTCEUR':
            return 'CS.D.BITCOIN.CFE.IP'

        if symbol == 'COPPER':
            return 'CS.D.COPPER.MINI.IP'

        return "CS.D." + symbol + ".MINI.IP"

    def get(self, symbol):

        if not symbol in self.market:
            self.market[symbol] = self.fetch_market_by_symbol(symbol)
        return self.market[symbol]

    def scaling_factor(self, symbol):

        market = self.get(symbol)
        return market['snapshot']['scalingFactor']

    def get_currency_code(self, symbol):

        return self.get(symbol)['instrument']['currencies'][0]['name']

    def get_min_stop(self, symbol):

        return float(self.get(symbol)['dealingRules']['minNormalStopOrLimitDistance']['value'])
