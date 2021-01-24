from position_manager.live_position_manager import LivePositionManager


class TestPositionManager(LivePositionManager):
    '''
        Same like LivePositionHanlder but does not communicate
        with any external service
    '''

    def fetch_open_positions(self):

        return []

    def push_open_position(self, position):

        return position

    def push_close_position(self, position):

        return position


