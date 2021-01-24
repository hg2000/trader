from settings import Settings


class BacktestAdapter():

    def __init__(self, price_manager, setup_items, evaluator, position_manager, processor):

        self.price_manager = price_manager
        self.setup_items = setup_items
        self.evaluator = evaluator
        self.position_manager = position_manager
        self.processor = processor

    def run(self):

        while self.price_manager.has_unfetched_ticks():
            for setup_item in self.setup_items:
                self.process_loop(
                    setup_item
                )
            self.price_manager.move_timestep()

        self.evaluator.position_manager = self.position_manager
        self.evaluator.price_manager = self.price_manager

        return self.evaluator

    def process_loop(self, setup_item):

        tick = self.price_manager.fetch_tick(symbol=setup_item.symbol)
        if not tick:
            return None
        self.current_time = tick.date

        self.processor.price_update(tick)
