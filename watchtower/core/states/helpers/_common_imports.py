from utils.items import GenericItem
from utils.source_type import TYPE
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
# firefox stuff
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver import FirefoxProfile
from selenium.webdriver.firefox.options import Options
# other
import sys
import logging
logging.getLogger('WDM').setLevel(logging.ERROR)
logging.getLogger('urllib3.connectionpool').setLevel(logging.ERROR)
logging.getLogger('selenium.webdriver.remote.remote_connection').setLevel(logging.ERROR)
from time import sleep
from scrapy import Selector
from urllib.parse import urljoin
from multiprocessing import Lock
