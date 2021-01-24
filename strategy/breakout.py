from strategy.base import BaseStrategy


class Breakout(BaseStrategy):

    def on_update_price(self):
        pass

  

    def on_update_chart(self):

        return

        adx = self.ADX(14)
        self.set_line('ADX', adx)

        ema20 = self.EMA(25)
        self.set_line('ema20', ema20)

        atr = (self.ATR(20) * 2)
        
        upper = ema20 + atr
        self.set_line('upper', upper)
        lower = ema20 - atr
        self.set_line('lower', lower)

        if (adx > 35) and (self.offer > ema20) and (self.offer < upper):
            self.open('long')

        if (adx > 35) and (self.bid < ema20) and (self.bid > lower):
            self.open('short')

        if self.has_open_position() and (adx < 25) and self.position.result_pips and self.position.result_pips > 1:
            self.log.info('Exit Trade condition reached. Result: ' +
                          str(self.position.result_pips))
            self.close()
