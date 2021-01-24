from random import randrange
import numpy as np
from quote import Quote


class RandomWalkSource():
    '''
        Provides price data based on a random walk
    '''

    def __init__(self):

        self.steps = []
        self.p = []
        self.start = 0
        self.scaling_factor = 0
        self.it = 0
        self.steps.append(0)
        self.p = [0.5, 0.5]
        self.start = 100
        self.scaling_factor = 100000

    def tick(self):
        '''
            Creates the next tick
        '''
        step = self._walk()
        tick = self._price_to_candle(self._step_to_price(step), self.it)
        self.it += 1
        return tick

    def _walk(self):
        ''' 
            makes a further random step
        '''
        w = randrange(1, 10)
        c = np.random.choice([-1, 1], p=self.p)
        n = self.steps[-1]
        step = n + (w * c)
        self.steps.append(step)
        return step

    def _step_to_price(self, step):
        '''
            transforms a step into a price value
        '''
        return (step + self.start) / self.scaling_factor

    def _price_to_candle(self, price, time):
        '''
            Creates a candle from a single price
        '''
        return Quote(date=time, offer_open=price,
                     offer_high=price, offer_low=price, offer_close=price, volume=1)
