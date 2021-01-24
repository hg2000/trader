from connector import Connector
from quote import Quotes, Quote
from trading_ig.config import config
from datetime import datetime, timedelta
from service.dateservice import Dateservice
import mysql.connector

class MysqlSource():

    def __init__(self):
        
        self.connection = mysql.connector.connect(user=config.db_user,
                                                  host=config.db_host,
                                                  password=config.db_password,
                                                  database=config.db_database)

    def fetch_quotes(self, symbol, limit=500):

        n=0
        quotes = Quotes()
        cursor = self.connection.cursor()
        sql="SELECT * FROM trader_price WHERE symbol = '%s' ORDER BY datetime DESC LIMIT %i" % (symbol, limit)
        cursor.execute(sql)
        while True:
            row = cursor.fetchone()
            if n==0:
                print('end date: ' + str(row[2]))
            if row == None:
                break
            quotes.add( date=row[2], symbol=row[1], offer_open=row[3], offer_high=row[4], offer_low=row[5], offer_close=row[6], bid_open=row[7], bid_high=row[8], bid_low=row[9], bid_close=row[10], volume=row[11])
            if n==limit-1:
                print('start date: ' + str(row[2])) 
            n+=1
        return quotes


    def store_quote(self, quote: Quote):

        cursor = self.connection.cursor()
        dt = dateservice.timestamp_to_datetime(quote.timestamp)
        sql = "INSERT INTO trader_price (datetime, offer_open, offer_high, offer_low, offer_close, bid_open, bid_high, bid_low, bid_close, symbol, volume) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        val = (dt, quote.offer_open, quote.offer_high, quote.offer_low,
               quote.offer_close, quote.bid_open, quote.bid_high, quote.bid_low, quote.bid_close, quote.symbol, quote.volume)
        
        cursor.execute(sql, val)
        self.connection.commit()

