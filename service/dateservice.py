from datetime import datetime
import os, time
import pytz  

class Format():

    IG = '%Y-%m-%dT%H:%M:%S.%f'
    IG2 = '%Y/%m/%d %H:%M:%S:%f'
    IG3 = '%Y-%m-%dT%H:%M:%S'
    YMDHM = '%Y-%m-%d %H:%M'

class Dateservice(): 

    @staticmethod
    def now():
        '''
            returns current datetime in UTC
        '''

        return datetime.utcnow()

    @staticmethod
    def local_now():
        os.environ['TZ'] = 'Europe/Berlin'
        time.tzset()

        return datetime.now()

    @staticmethod
    def str_to_datetime(item, format):
        return datetime.strptime(item, format).replace(tzinfo=pytz.UTC)

    @staticmethod
    def datetime_to_str(item, format = Format.IG3):
        return datetime.strftime(item, format)

    @staticmethod
    def datetime_to_timestamp(dt):
        return dt.timestamp()

    @staticmethod
    def timestamp_to_datetime(timestamp):
        dt = datetime.fromtimestamp(timestamp).astimezone(pytz.UTC)
        return dt
  
