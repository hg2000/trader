import os
import sys
import unittest
from unittest.mock import MagicMock
from indicator import Indicator


class TestBase(unittest.TestCase):

    def get_candles(self):

        candles = []
        candles.append([90, 90, 82, 87])
        candles.append([95, 95, 85, 87])
        candles.append([105, 105, 93, 97])
        candles.append([120, 120, 106, 114])
        candles.append([140, 140, 124, 133])
        candles.append([165, 165, 147, 157])
        candles.append([195, 195, 175, 186])
        candles.append([230, 230, 208, 223])
        candles.append([270, 270, 246, 264])
        candles.append([315, 315, 289, 311])
        candles.append([365, 365, 337, 350])
        return candles

    def test_sma(self):

        w = list(range(1, 11))
        indicator = Indicator()
        r = indicator.sma(w, 3, 'sma3')

        self.assertEqual(r, 9)
        self.assertRaises(ValueError, indicator.sma, w, 11)

        r2 = indicator.sma_add('sma3', 11)
        self.assertEqual(r2, 10)
        self.assertRaises(ValueError, indicator.sma_add, 'x', 1)

    def test_ema(self):

        w = list(range(1, 11))
        indicator = Indicator()
        r = indicator.ema(w, 3)
        self.assertEqual(r, 9.25)

    def test_true_range(self):

        h = 95
        l = 85
        cp = 87
        indicator = Indicator()
        r = indicator.tr(h, l, cp)
        self.assertEqual(r, 10)

    def test_dm(self):

        candles = self.get_candles()
        indicator = Indicator()
        dm = indicator.dm(candles[0], candles[1])
        self.assertEqual(dm[0], 5)
        self.assertEqual(dm[1], 0)
        dm = indicator.dm(candles[1], candles[2])
        self.assertEqual(dm[0], 10)
        self.assertEqual(dm[1], 0)
        dm = indicator.dm(candles[2], candles[3])
        self.assertEqual(dm[0], 15)
        self.assertEqual(dm[1], 0)

    def test_smoothed_sma(self):

        w = [5,10,15,20,25,30,35,40,45,50]
        indicator = Indicator()
        r = indicator.smoothed_sma(w, 5)
        self.assertEqual(r.pop(), 166.384)


    def test_direction_index(self):

        candles = self.get_candles()
        indicator = Indicator()
        indicator.adx(candles, 5)




    def test_average_true_range(self):

        candles = []
        opens = range(1, 10)
        highs = range(41, 51)
        lows = range(21, 31)
        closes = range(31, 61)
        candles = list(zip(opens, highs, lows, closes))

        indicator = Indicator()
        r = indicator.atr(candles, 3)
        self.assertEqual(r, 20)

  


    def test_di(self):

        candles = []
        opens = range(101, 130)
        highs = range(301, 430)
        lows = range(1, 30)
        closes = range(201, 230)
        candles = list(zip(opens, highs, lows, closes))

        indicator = Indicator()
        r = indicator.di(candles, 14)
        self.assertEqual(r, (0.3333333333333333, 0))

    def test_adx(self):

        candles = self.get_candles()

        indicator = Indicator()
        r = indicator.adx(candles, 5)
        self.assertEqual(r, 100)

    def test_adx2(self):

        candles = []
        candles.append([107.6265,107.6265,107.599,107.599])
        candles.append([107.6075,107.6275,107.6075,107.627])
        candles.append([ 107.62950000000001,107.6485,107.6295,107.6485])
        candles.append([ 107.64750000000001,107.6655,107.6465,107.6655])
        candles.append([ 107.68,107.7075,107.679,107.7075])
        candles.append([ 107.691,107.695,107.672,107.6725])
        candles.append([ 107.69749999999999,107.706,107.6955,107.7055])
        candles.append([ 107.6885,107.7275,107.6885,107.7275])
        candles.append([ 107.7495,107.7715,107.7415,107.771])
        candles.append([ 107.79849999999999,107.8005,107.735,107.735])
        candles.append([ 107.7475,107.841,107.7475,107.84])
        candles.append([ 107.81649999999999,107.8295,107.804,107.829])
        candles.append([ 107.8265,107.8315,107.8185,107.819])
        candles.append([ 107.8275,107.8275,107.7715,107.7715])
        candles.append([ 107.7915,107.7915,107.7505,107.7645])
        candles.append([ 107.7555,107.7555,107.724,107.724])
        candles.append([ 107.72,107.747,107.72,107.7465])
        candles.append([ 107.765,107.767,107.754,107.767])
        candles.append([ 107.761,107.79,107.761,107.789])
        candles.append([ 107.80000000000001,107.833,107.8,107.805])
        candles.append([ 107.818,107.818,107.783,107.783])
        candles.append([ 107.786,107.7925,107.775,107.7925])
        candles.append([ 107.75999999999999,107.761,107.747,107.748])
        candles.append([ 107.753,107.7615,107.753,107.7615])
        candles.append([ 107.7765,107.7765,107.749,107.7495])
        candles.append([ 107.72749999999999,107.7275,107.718,107.723])
        candles.append([ 107.737,107.7575,107.7265,107.757])
        candles.append([ 107.7505,107.7505,107.723,107.723])
        candles.append([ 107.731,107.731,107.7145,107.715])



        indicator = Indicator()
        r = indicator.adx(candles, 14)
        self.assertEqual(r, 100)


    

if __name__ == '__main__':
    unittest.main()
