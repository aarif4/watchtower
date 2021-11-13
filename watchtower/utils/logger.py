import os
import logging
from termcolor import colored



class Logger:
    log = None
    ch = None
    fp = None

    USE_PRINTF = True
    DEBUG = colored('DEBUG','cyan')
    INFO = colored('INFO ','green')
    WARN = colored('WARN ','yellow')
    ERROR = colored('ERROR','red')
    FATAL = colored('FATAL','magenta')

    def __init__(self, log_name, filename=''):
        if self.USE_PRINTF:
            self.log = log_name
        else:
            # R,G,B,Y,M,C,W
            # "DEBUG" C
            # "INFO " G
            # "WARN " Y
            # "ERROR" R
            # "FATAL" M
            logging.addLevelName(logging.DEBUG,colored('DEBUG','cyan'))
            logging.addLevelName(logging.INFO,colored('INFO ','green'))
            logging.addLevelName(logging.WARNING,colored('WARN ','yellow'))
            logging.addLevelName(logging.ERROR,colored('ERROR','red'))
            logging.addLevelName(logging.FATAL,colored('FATAL','magenta'))
            
            log_lvl = logging.DEBUG
            self.log = logging.getLogger(log_name)
            self.log.setLevel(level=log_lvl)

            fmt = logging.Formatter('[%(asctime)s] [%(name)s] [%(levelname)s]: %(message)s','%Y-%m-%d %H:%M:%S')
            self.ch = logging.StreamHandler()
            self.ch.setLevel(level=log_lvl)
            self.ch.setFormatter(fmt)
            self.log.addHandler(self.ch)

            #if filename:
            #    self.fp = logging.FileHandler(filename=filename)
            #    self.fp.setLevel(level=log_lvl)
            #    self.fp.setFormatter(fmt)
            #    self.log.addHandler(self.fp)
    
    def __del__(self):
        if not self.USE_PRINTF:
            if self.log:
                if self.ch:
                    self.log.removeHandler(self.ch)
                    del self.ch
                if self.fp:
                    self.log.removeHandler(self.fp)
                    del self.fp
                del self.log
    
    def debug(self, string):
        if self.USE_PRINTF:
            self.log.debug(string)
        else:
            print('[%s] [%s]: %s' % (self.log, self.DEBUG, string))
    
    def info(self, string):
        if not self.USE_PRINTF:
            self.log.info(string)
        else:
            print('[%s] [%s]: %s' % (self.log, self.INFO, string))
    
    def warning(self, string):
        if not self.USE_PRINTF:
            self.log.warning(string)
        else:
            print('[%s] [%s]: %s' % (self.log, self.WARN, string))
    
    def error(self, string):
        if not self.USE_PRINTF:
            self.log.error(string)
        else:
            print('[%s] [%s]: %s' % (self.log, self.ERROR, string))
    
    def fatal(self, string):
        if not self.USE_PRINTF:
            self.log.fatal(string)
        else:
            print('[%s] [%s]: %s' % (self.log, self.FATAL, string))
