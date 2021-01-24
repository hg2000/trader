from observer import Observer, Subject
from settings import Settings

class BrokerLocal(Observer, Subject):

    def update(self, subject, message):

        if message == Settings.get('Message').position_opened:
            self.push_open_position(subject.position)

        if message == Settings.get('Message').position_closed:
            self.push_close_position(subject.position)

    def push_open_position(self, position):

        self.notify(Settings.get('Message').open_position_pushed, Settings.get('Domain').position)
        return position

    def push_close_position(self, position):
        self.notify(Settings.get('Message').close_position_pushed, Settings.get('Domain').position)
        return position

    def fetch_external_closed_positions_by_id(self, id):
        return None

    def fetch_external_closed_positions(self):
        return None
        
    def fetch_open_positions(self):
        return None

    def convert_broker_symbol_to_local(self, name):
        '''
            Converts an IG Markets Epic to Symbol

        '''

        if name == 'CS.D.BITCOIN.CFE.IP':
            return 'BTCEUR'

        parts = name.split('.')
        symbol = parts[2]

        return symbol
