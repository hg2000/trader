from datetime import datetime
import os
import traceback
from settings import Settings


class Loglevel:

    NOTICE = 0
    INFO = 1
    WARNING = 2
    ERROR = 3


class FileWriter():

    error_log_file = ''
    info_log_file = ''
    max_file_size = 100000

    def __init__(self, level):

        path = os.getcwd()
        self.error_log_file = path + "/livetrader/log/error.txt"
        self.info_log_file = path + "/livetrader/log/info.txt"
        self.level = level

    def now(self):
        return str(datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'))

    def notice(self, message, item=None):

        file = open(self.error_log_file, 'a+')
        file.write(str(self.now() + ': ' + str(message) + "\n"))
        file.close()
        self.cleanup()

    def error(self, message, item=None):

        if self.level >= Loglevel.ERROR:
            return

        file = open(self.error_log_file, 'a+')
        file.write(str(self.now() + ': ' + str(message) + "\n"))
        file.close()
        self.cleanup()

    def info(self, message, item=None):

        if self.level < Loglevel.INFO:
            return

        file = open(self.info_log_file, 'a+')
        file.write(str(self.now() + ': ' + message + "\n"))
        file.close()
        self.cleanup()

    def cleanup(self):

        try:
            size = os.path.getsize(self.error_log_file)
            if size > self.max_file_size:
                self.delete_file(self.error_log_file)
            size = os.path.getsize(self.info_log_file)
            if size > self.max_file_size:
                self.delete_file(self.info_log_file)
        except:
            pass

    def delete_file(self, file):

        try:
            os.remove(file + '_bak')
        except BaseException:
            pass
        os.rename(file, file + '_bak')


class ConsoleWriter():

    def __init__(self, level):

        self.level = level

    def error(self, message, item=None):

        if self.level < Loglevel.ERROR:
            return

        print(str(message))
        print(traceback.format_exc())

    def info(self, message, item=None):

        if self.level < Loglevel.INFO:
            return

        print(str(message))

    def notice(self, message, item=None):

        print(str(message))


class CsvWriter():

    max_file_size = 800000
    
    def __init__(self, level):

        self.level = level
        path = os.getcwd()
        self.notice_log_file = path + "/livetrader/log/notice.csv"

    def error(self, message, item=None):
        pass

    def info(self, mesage, item=None):
        pass

    def notice(self, message, item=None):

        file = open(self.notice_log_file, 'a+')
        file.write( str(message) + "\n")
        file.close() 

        self.cleanup()  


    def now(self):
            return str(datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'))

    def cleanup(self):

        try:
            size = os.path.getsize(self.notice_log_file)
            if size > self.max_file_size:
                self.delete_file(self.notice_log_file)
            size = os.path.getsize(self.notice_log_file)
            if size > self.max_file_size:
                self.delete_file(self.notice_log_file)
        except:
            pass

    def delete_file(self, file):

        try:
            os.remove(file + '_bak')
        except BaseException:
            pass
        os.rename(file, file + '_bak')

class Logger():

    instance = None

    class __Logger:

        loggers = []
        last_error_message = ''
        last_info_message = ''

        def __init__(self):

            self.loggers.append(FileWriter(Loglevel.INFO))
            self.loggers.append(ConsoleWriter(Loglevel.INFO))
            self.loggers.append(CsvWriter(Loglevel.NOTICE))

        def error(self, message, item=None):

            if message == self.last_error_message:
                return False

            for logger in self.loggers:
                if logger.level <= Loglevel.ERROR:
                    logger.error(str(message), item)
                
            self.last_error_message = message

        def info(self, message, item=None):

            if message == self.last_info_message:
                return False
            
            for logger in self.loggers:
                if logger.level <=Loglevel.INFO:
                    logger.info(str(message), item)
    
            self.last_info_message = message

        def notice(self, message, item=None):

            if message == self.last_info_message and item == self.last_item:
                return False
            
            for logger in self.loggers:
              
                if logger.level <= Loglevel.NOTICE:
                    logger.notice(str(message), item)

            self.last_info_message = message
            self.last_item = item

    def __init__(self):
        if not Logger.instance:
            Logger.instance = Logger.__Logger()

    def __getattr__(self, name):
        return getattr(self.instance, name)
