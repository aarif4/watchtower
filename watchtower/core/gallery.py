from scrapy.utils.project import get_project_settings
from scrapy.crawler import CrawlerProcess
from core.spider import Taratect
from utils import settings 
from utils.logger import Logger


class gallery:
    user_cfg = None
    logger = None

    def __init__(self, cfg):
        self.user_cfg = cfg
        self.logger = Logger('gallery')

    def run(self):
        # get scrapy settings
        settings = self.get_settings()
        
        # open a web crawler for each request
        process = CrawlerProcess(settings)
        for i in range(len(self.user_cfg['series'])):
            self.logger.info("Added a Taratect to parse series %s" % (self.user_cfg['series'][i]['title'],))
            process.crawl(Taratect, config=self.user_cfg['series'][i], sources=self.user_cfg['sources'], executable=self.user_cfg['executable'])
        process.start()

    def get_settings(self):
        # load default settings
        my_settings = get_project_settings()
        
        # apply user's configuration settings        
        variable_names = [v for v in dir(settings) if not v.startswith('_')]
        settings_dict = {}
        for var_name in variable_names:
            settings_dict[var_name] = eval('settings' + '.' + var_name)
        my_settings.update(settings_dict)
        
        return my_settings
