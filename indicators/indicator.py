from settings import Settings

class Indicator():

    def __init__(self):

        self.storage = {}
        self.log = Settings.get('Logger')()

    def has_key(self, key):

        return key in self.storage

    def sma(self, l: list, w: int, key: str = None):
        """Simple moving average
        https://en.wikipedia.org/wiki/Moving_average

        l: list of values
        w: window length
        key: if set sequence will be stored, for continue later
        """

        if w > len(l):
            raise ValueError('Window length is greater than list.')

        n = l[-w:]
        s = sum(n)
        r = s / w
        if key:
            self.storage[key] = (n, s, w)

        return r

    def sma_add(self, key, v):
        """Add one value to the previously stored simmple moving average
        key: Key of the stored sequence
        v: value to add
        """

        if not self.has_key(key):
            raise ValueError('Key %s not set.' % key)

        n = self.storage[key][0]
        n2 = n[1:]
        n2.append(v)
        s = self.storage[key][1] - n[0] + v
        w = self.storage[key][2]
        r = s / w
        self.storage[key] = (n2, s, w)
        return r

    def smoothed_sma(self, l: list, w: int):

        if w > len(l) * 2:
            raise ValueError(
                'Window length is greater than list. For smoothed sma list must be at least 2 * w')

        n = l[-2*w:]
        t = 0
        a1 = None

        averages = []

        while t < w+1:
            m = n[t:t+w]
            s = sum(m)
            if not a1:
                averages.append(s)
                a1 = s
            else:
                p = n[t+w-1]
                av = a1 - (a1/w) + p
                a1 = av
                averages.append(av)
            t += 1
        return averages

    def ema(self, l: list, w: int, s0=None):
        """Exponential moving average
        https://en.wikipedia.org/wiki/Moving_average

        l: list of values
        w: window length
        key: if set sequence will be stored, for continue later
        s0: Initial value, if not set will be first value if w < 5, and sma of first 5 values if w > 5
        """

        a = 2 / (w + 1)    # degree of weighting decrease
        n = l[-w:]
        m = []
        t = 0
        for y in n:
            if t == 0:
                if not s0:
                    if w < 5:
                        s = y
                    else:
                        s = self.sma(l[0:5], 5)
            else:
                s = a * y + (1-a) * m[t-1]
            m.append(s)
            t += 1

        return m[-1]

    def tr(self, h, l, cp):
        """True Range
        https://en.wikipedia.org/wiki/Average_true_range
        h: high
        l: low
        cp: previous close
        """
        return max([h-l, abs(h - cp), abs(l - cp)])

    def atr(self, candles: list, w):
        """Average True Range
        https://en.wikipedia.org/wiki/Average_true_range
        candles: List of following items: [open, high, low, close]
        w: window length
        """

        if w > len(candles):
            raise ValueError('Window length is greater than list.')

        t = 0
        r = []
        c = candles[-w:]
        for y in c:
            if t > 0:
                x = c[t-1]
                tr = self.tr(y[1], y[2], x[3])
                r.append(tr)
            t += 1

        return self.sma(r, w-1)

    def dm(self, candle_t1: list, candle_t2: list):
        """Directional Movement
        https://en.wikipedia.org/wiki/Average_directional_movement_index,
        https://blog.quantinsti.com/adx-indicator-python/

        candles: List of following items: [open, high, low, close]
        candle_t1: candle of earlier time period
        candle_t2: candle of later time period

        Candle means a list: [open, high, low, close]
        """

        up_move = candle_t2[1] - candle_t1[1]
        down_move = candle_t1[2] - candle_t2[2]

        if up_move > down_move and up_move > 0:
            dm_plus = up_move
        else:
            dm_plus = 0

        if down_move > up_move and down_move > 0:
            dm_minus = down_move
        else:
            dm_minus = 0

        return (dm_plus, dm_minus)

    def di(self, candles: list, w):
        """Directional Index
        https://en.wikipedia.org/wiki/Average_directional_movement_index
        candles: List of following items: [open, high, low, close]
        w: window length
        """

        if w > len(candles):
            raise ValueError('Window length is greater than list.')

        t = 0
        cs = candles[-w-1:]
        dmp = []
        dmm = []

        for c in cs:
            if t > 0:
                r = self.dm(cs[t-1], cs[t])
                dmp.append(r[0])
                dmm.append(r[1])
            t += 1

        atr = self.atr(cs, w)

        dmpe = self.ema(dmp, w)
        dmme = self.ema(dmm, w)

        dip = 100 * dmpe / atr
        dim = 100 * dmme / atr

        return (dip, dim)

    def adx(self, candles: list, w):
        """Average True Range
        https://en.wikipedia.org/wiki/Average_directional_movement_index
        candles: List of following items: [open, high, low, close]
        w: window length
        """

        if w*2 > len(candles) + 1:
            raise ValueError(
                'Window length is greater than list. For average true range window length must be at least 2 * w')

    
        t = 1
        positive_directional_movements = []
        negative_directional_movements = []
        true_ranges = []

        while t < w*2 + 1:
            dm = self.dm(candles[t-1], candles[t])
            positive_directional_movements.append(dm[0])
            negative_directional_movements.append(dm[1])

            true_range = self.tr(candles[t][1], candles[t][2], candles[t-1][3])
            true_ranges.append(true_range)
            t += 1

        smoothed_true_ranges = self.smoothed_sma(true_ranges, w)
        smoothed_positive_directional_movements = self.smoothed_sma(
            positive_directional_movements, w)
        smoothed_negative_directional_movements = self.smoothed_sma(
            negative_directional_movements, w)

        t = 0
        l = len(smoothed_positive_directional_movements)
        positive_directional_indicators = []
        negative_directional_indicators = []
        dxs = []
        while t < l:
            positive_directional_indicators.append(
                100 * smoothed_positive_directional_movements[t] / smoothed_true_ranges[t])
            negative_directional_indicators.append(
                100 * smoothed_negative_directional_movements[t] / smoothed_true_ranges[t])
            dx = 100 * ((smoothed_positive_directional_movements[t] - smoothed_negative_directional_movements[t]) / (
                smoothed_positive_directional_movements[t] + smoothed_negative_directional_movements[t]))
            dxs.append(dx)

            t += 1

        adx = abs(self.sma(dxs, w))
        return adx

