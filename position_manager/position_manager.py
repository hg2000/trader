from settings import Settings
from datetime import datetime
from time import time
from copy import copy
from dotenv import load_dotenv
import os
from observer import Observer, Subject


class PositionManagerException(Exception):
    pass


class PositionManager(Observer, Subject):
    '''
        Takes care of position handling local and on external service
    '''

    def __init__(self, market, broker, position_repository):

        self.open_positions = {}
        self.closed_positions = {}
        self.triggered_positions = {}
        self.max_closed_positions = 5000

        self.broker = broker
        self.market = market
        self.position_repository = position_repository

        self.log = Settings.get('Logger')()
        self.setup_manager = Settings.get('SetupManager')()
        self.position = None
        self.bid = None
        self.offer = None
        self.symbol = None
        self.datetime = None

    def update(self, subject, message=None):

        if message == Settings.get('Message').open_position:
            self.open_position(subject.position, subject.offer,
                               subject.bid, subject.datetime)

        if message == Settings.get('Message').close_position:
            self.close_open_position(
                subject.position, subject.offer, subject.bid, subject.datetime)

        if message == Settings.get('Message').start_live_trading:
            self.sync_position_state()

        if message == Settings.get('Message').pushed_open_position:
            self.position_repository.store(subject.position)

        if message == Settings.get('Message').pushed_close_position:
            self.position_repository.update_db(subject.position)

        if message == Settings.get('Message').position_deleted_externaly:
            self.close_open_position_by_id(subject.deal_id, subject.bid, subject.offer, subject.datetime)
            
            

    def sync_position_state(self):

        self.fetch_open_positions()
        externally_closed_positions = self.fetch_external_closed_positions()
        for p in externally_closed_positions:
            p.close()
            self.position_repository.update_db(p)

    def fetch_open_positions(self):
        '''
            fetches open positions from external source
        '''

        self.delete_all_open_positions()

        fetched_positions = self.broker.fetch_open_positions()
        stored_positions = self.position_repository.find_open_positions()

        for f in fetched_positions:
            for stored_position in stored_positions:
                if stored_position.id == f.id:
                    self.add_to_open_positions(stored_position)

        return self.open_positions

    def fetch_external_closed_positions(self):
        '''
            returns all positions which are locally in state open
            but have no corresponding state at the broker, means
            they have been closed externally
        '''

        stored_positions = self.position_repository.find_open_positions()
        fetched_positions = self.broker.fetch_open_positions()

        result = []

        for s in stored_positions:
            match = False
            for f in fetched_positions:
                if s.id == f.id:
                    match = True
            if not match:
                result.append(s)

        if len(result) < len(stored_positions):

            fetched_closed_positions = self.broker.fetch_closed_positions()
            for s in stored_positions:
                for f in fetched_closed_positions:
                    if s.reference == f.reference:
                        result.append(s)
                        continue

        return result

    def fetch_external_closed_positions_by_id(self, id):

        external_closed_positions = self.fetch_external_closed_positions()
        for e in external_closed_positions:
            if e.id == id:
                return e
        return None

    def create_position(self, setup_item):

        position = Settings.get('Position')(setup_item)
        position.symbol = setup_item.symbol
        position.strategy_name = setup_item.strategy_name
        position.timeframe = setup_item.parameters.timeframe
        position.setup_item = setup_item
        position.scaling_factor = self.market.scaling_factor(position.symbol)
        return position

    def delete_all_open_positions(self):
        '''
            Deletes all open positions
        '''

        self.open_positions = {}

    def open_position(self, position, offer, bid, datetime, setup_item=None):
        '''
            Creates a new postion if position not already exists
        '''

        for id in self.open_positions:
            if self.open_positions[id].setup_item == position.setup_item:
                return None

        if position.direction == Settings.get('Direction').buy:
            position.open_price = offer
            position.close_price = bid
        if position.direction == Settings.get('Direction').sell:
            position.open_price = bid
            position.close_price = offer
        if not position.direction:
            raise BaseException('Position has no direction!')

        position.open_time = datetime
        position.scaling_factor = self.market.scaling_factor(position.symbol)
        position.initial_calculations()

        self.add_to_open_positions(position)
        self.position = position
        self.update_open_position_calculations(
            bid, offer, position.symbol, datetime)
        self.notify(Settings.get('Message').position_opened,
                    Settings.get('Domain').position)

        self.log.info('Opened position. ' + position.symbol)
        self.log.notice( position.symbol + ', open position')
        return position

    def close_open_position(self, position_to_close, bid, offer, datetime):
        '''
            Closes an open position
        '''
        position = self.get_open_position(
            position_to_close.symbol, position_to_close.setup_item.strategy_name, position_to_close.timeframe)

        if not position:
            self.log.info(
                'Open position not not found. Check if it was already closed externally')
            import time
            time.sleep(1)

            position = self.fetch_external_closed_positions_by_id(
                position_to_close.id)

        if not position:
            self.log.info('Open position not found. Symbol %s, ID: %s, Reference; %s' %
                          position.symbol, position.id, position.reference)
            self.log.error('Open position not found. Symbol %s, ID: %s, Reference; %s' %
                           position.symbol, position.id, position.reference)
            raise BaseException('Could not find position anywhere')

        if position.direction == Settings.get('Direction').buy:
            position.close_price = bid
        if position.direction == Settings.get('Direction').sell:
            position.close_price = offer
        if not position.close_price:
            raise BaseException(
                'Invalid position diretion: %s ' % position.direction)
        position.close_time = datetime
        position.update_calculations(bid, offer)

        self.add_to_closed_positions(position)
        self.remove_from_open_positions(position)

        self.position = position
        self.notify(Settings.get('Message').position_closed,
                    Settings.get('Domain').position)

        self.log.info('Closed position.' +  position.symbol + ', Result Pips: ' + str(position.result_pips))
        self.log.notice( position.symbol + ', close position, Result Pips, ' + str(position.result_pips))
        return position


    def close_open_position_by_id(self, id, bid, offer, datetime):

        position = self.get_open_position_by_id(id)
        if position:
            self.close_open_position(position, bid, offer, datetime)

    def update_open_positions(self, cmd, bid, offer, date=None):
        '''
            Updates attributes of open positions
        '''
        cmd.position.update_calculations(bid, offer)
        if not cmd.position.id in self.open_positions:
            self.fetch_open_positions()
            if not cmd.position.id in self.open_positions:
                return False
        self.open_positions[cmd.position.id] = cmd.position
        self.position_repository.update(cmd.position)

        return cmd.position

    def update_open_position_calculations(self, bid, offer, symbol, datetime):
        '''
            updates the results of currently open positions for the given symbol
            based on current bid and offer prices
        '''

        for id in self.open_positions:

            position = self.open_positions[id]
            if symbol == position.symbol:
                position.update_calculations(bid, offer)
                self.open_positions[id] = position
                self.position = position
                self.notify(Settings.get('Message').position_updated,
                            Settings.get('Domain').position)
                message = position.validate(bid, offer, symbol)
                self.position = position
                if message:
                    self.bid = bid
                    self.offer = offer
                    self.datetime = datetime
                    self.symbol = symbol
                    self.notify(message, Settings.get('Domain').position)

    def add_to_open_positions(self, position):

        self.open_positions[position.id] = position

    def add_to_closed_positions(self, position):

        self.closed_positions[position.id] = position
        if len(self.closed_positions) > self.max_closed_positions:

            self.closed_positions = {}

    def remove_from_open_positions(self, position):

        for id in self.open_positions:
            if self.open_positions[id].setup_item == position.setup_item:
                break
 
        del(self.open_positions[id])
        pass

    def get_open_positions_by_symbol(self, symbol):

        positions = []
        for id in self.open_positions:
            if self.open_positions[id].symbol == symbol:
                positions.append(self.open_positions[id])

        if positions:
            return positions

        return positions


    def get_open_position(self, symbol, strategy, timeframe):

        for id in self.open_positions:
            position = self.open_positions[id]

            if position.symbol == symbol and position.setup_item.strategy_name == strategy and position.timeframe == timeframe:
                return position

        return None

    def get_open_position_by_strategy(self, symbol, strategy):

        for id in self.open_positions:
            position = self.open_positions[id]
            hash1 = str(position.setup_item.parameters) + position.setup_item.strategy_name + position.setup_item.symbol
            hash2 = str(strategy.setup_item.parameters) + strategy.setup_item.strategy_name + strategy.setup_item.symbol
            if hash1 == hash2:
                return position
           
        return None

    def get_open_position_by_id(self, id):

        for i in self.open_positions:
            if self.open_positions[i].id == id:
                return self.open_positions[i]

        self.fetch_open_positions()

        for i in self.open_positions:
            if self.open_positions[i].id == id:
                return self.open_positions[i]

        return None
