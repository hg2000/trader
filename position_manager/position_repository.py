from settings import Settings
from copy import deepcopy
from observer import Observer


class PositionRepository(Observer):

    def __init__(self, local_storage):

        self.db = local_storage

    def update(self, subject, message=None):

        if message == Settings.get('Message').position_opened:
            self.store(subject.position)
        if message == Settings.get('Message').position_closed:
            self.update_db(subject.position)

    def store(self, position):

        p = deepcopy(position)
        cursor = self.db.connection.cursor()
        sql = "INSERT INTO trader_position (id, symbol, timeframe, strategy, direction, size, state, open_price, open_time, close_price, close_time, result, result_pips, trailing_pips, trailing_level, stop_pips, stop_level, setup_item, scaling_factor, reference) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s, %s, %s)"
        val = (
            p.id,
            p.symbol,
            p.timeframe,
            p.strategy,
            p.direction,
            p.size,
            p.state,
            p.open_price,
            p.open_time,
            p.close_price,
            p.close_time,
            p.result,
            p.result_pips,
            p.trailing_pips,
            p.trailing_level,
            p.stop_pips,
            p.stop_level,
            p.setup_item.to_json(),
            p.scaling_factor,
            p.reference
        )

        cursor.execute(sql, val)
        self.db.connection.commit()
        pass

    def update_db(self, position):

        cursor = self.db.connection.cursor()
        sql = "UPDATE trader_position set  close_time = %s, close_price = %s, result = %s,  result_pips = %s, trailing_pips = %s, trailing_level = %s, stop_pips = %s, stop_level = %s  WHERE id = %s"
        val = (position.close_time, position.close_price, position.result, position.result_pips,
               position.trailing_pips, position.trailing_level, position.stop_pips, position.stop_level, position.id)
        cursor.execute(sql, val)
        self.db.connection.commit()

    def find_open_positions(self):

        cursor = self.db.connection.cursor()
        sql = "SELECT * FROM trader_position  where open_time IS NOT NULL and close_time IS NULL ORDER BY open_time DESC"
        cursor.execute(sql)

        rows = cursor.fetchall()
        positions = []

        for row in rows:

            position = Settings.get('Position')()
            position = self.row_to_position(row)
            positions.append(position)

        return positions

    def find_open_position_by_id(self, deal_id):

        cursor = self.db.connection.cursor()
        sql = "SELECT * FROM trader_position WHERE not open_time = null and not close_time =  null AND id = '" + deal_id + "'"
        cursor.execute(sql)

        row = cursor.fetchone()
        if row:
            return self.row_to_position(row)

        return None

    def row_to_position(self, row):

        position = Settings.get('Position')()
        position.id = row[0]
        position.symbol = row[1]
        position.timeframe = row[2]
        position.strategy_name = row[3]
        position.direction = row[4]
        position.size = row[5]
        position.state = row[6]
        position.open_price = row[7]
        position.open_time = row[8]
        position.close_price = row[9]
        position.close_time = row[10]
        position.result = row[11]
        position.result_pips = row[12]
        position.trailing_pips = row[13]
        position.trailing_level = row[14]
        position.stop_pips = row[15]
        position.stop_level = row[16]
        position.setup_item = Settings.get('SetupItem')().from_json(row[17])
        position.scaling_factor = row[18]
        position.reference = row[19]

        return position
