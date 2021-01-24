class TestMarket():



    def __init__(self): 

        self.market = {}
        self._scaling_factor = 10000
    
    def get(self, symbol):

        return []

    def scaling_factor(self, symbol):

        if symbol == 'USDJPY':
            return 100

        if symbol == 'EURJPY':
            return 100

        if symbol == 'BTCEUR':
            return 1
            
        return 10000


