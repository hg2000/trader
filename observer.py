
from typing import List
from abc import ABC, abstractmethod
from settings import Settings



class Domain:

    price = 'PRICE'
    position = 'POSITION'
    misc = 'MISC'

class Message:

    push_tick = 'PUSH TICK'
    ''' a new tick has arrived and needs to be stored localy
    '''

    push_quote = 'PUSH QUOTE'
    ''' a new quote has arrived and needs to be stored localy
    '''

    update_tick = 'UPDATE TICK'
    ''' a new price is ready to process. Check the strategies if they have to start some action
    '''

    update_quote = 'UPDATE QUOTE'
    ''' a new price with end of timeframe is ready to process. Check the strategies if they have to start some action
    '''

    update_quote_preload = 'UPDATE QUOTE PRELOAD'
    open_position = 'OPEN POSITION'
    close_position = 'CLOSE POSITION'
    uppdate_position = 'UPDATE POSITION'
    position_opened = 'POSITION OPENED'
    position_closed = 'POSITION CLOSED'
    position_updated = 'POSITION UPDATED'
    position_deleted = 'POSITION DELETED'
    position_deleted_externaly = 'POSITION DELETED EXTERNALLY'
    pushed_open_position = 'PUSHED OPEN POSITION'
    pushed_close_position = 'PUSHED CLOSE POSITION'
    update_chart = 'UPDATE CHART'
    
    update_position = 'UPDATE POSITION'
    
    open_position_pushed = 'OPEN POSITION PUSHED'
    close_position_pushed = 'CLOSE POSITION PUSHED'
    start_backtest = 'START BACKTEST'
    start_live_trading = 'START LIVE TRADING'
     
class Subject():

    _observers: dict = {}

    def attach(self, observer, domain) -> None:
        if not domain in self._observers:
            self._observers[domain] = []
        self._observers[domain].append(observer)

    def detach(self, observer, domain) -> None:
        self._observers[domain].remove(observer)

    """
    The subscription management methods.
    """

    def notify(self, message, domain) -> None:
        """
        Trigger an update in each subscriber.
        """

        self.log = Settings.get('Logger')()

        for observer in self._observers[domain]:
            self.logger(self, message)
            observer.update(self, message)

    def logger(self, subject, message):

        if message == 'UPDATE QUOTE':
            return

        if message == 'PUSH PRICE':
            return
        if message == 'PUSH QUOTE':
            return

        if message == 'POSITION UPDATED':
            return
        
        self.log.info(message)

        pass



            
class Observer():

    def update(self, subject, message, domain) -> None:
        pass