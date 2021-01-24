from settings import Settings

class BrokerTest():



    def convert_local_to_broker_symbol(self, symbol):

        if symbol == 'BTCEUR':
            return 'CS.D.BITCOIN.CFE.IP'

        return "CS.D." + symbol + ".MINI.IP"

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
