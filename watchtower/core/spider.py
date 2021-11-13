import scrapy
from utils.items import GenericItem
from utils.source_type import TYPE
from utils.logger import Logger
from core.state_machine import StateMachine
from selenium.webdriver.remote.command import Command
from core.states._common_states import *
from multiprocessing import Lock
from core import packaging
from core import pipelines
import re


class Taratect(scrapy.Spider):
    handle_httpstatus_list = [403]
    name = 'Taratect'
    spider_id = ''
    executable = ''
    driver = None
    config = None
    source = None
    logger = None
    state_machine = None
    lock=Lock()
    
    def __init__(self, config=None, sources=None, executable=None):
        if not config:
            raise Exception('ConfigError: Missing configuration')
        else:
            self.config = config

        if not sources:
            raise Exception('ConfigError: Missing source info')
        else:
            self.source = sources[self.config['source']]
            self.allowed_domains = [re.split('(http.*://)|(/)',val['url'])[3] for key,val in sources.items()]
        if not executable:
            self.executable = executable
        
        self.spider_id = str(config['type']).split('.')[1].capitalize()
        #target_pipeline = 'pipelines.%s' % (self.spider_id,)
        #self.custom_settings = eval("{'ITEM_PIPELINES': {('%s'):300}}" % (target_pipeline,))
        self.logger = Logger('%s | %s' % (self.name, config['source']))

        # construct the novel site's state machine
        self.state_machine = StateMachine(self.logger)
        self.logger.info('Making state machine...')
        self.state_machine.add_state(openSite.__name__, openSite)
        self.state_machine.set_startState(openSite.__name__)
        self.state_machine.add_state(getChapterListDynamic.__name__, getChapterListDynamic)
        self.state_machine.add_state(getChapterListStatic.__name__, getChapterListStatic)
        self.state_machine.add_state(parseChapterDynamic.__name__, parseChapterDynamic, is_endState=True)
        self.state_machine.add_state(parseChapterStatic.__name__, parseChapterStatic, is_endState=True)
        self.logger.info('Done making state machine')

        if self.config['chapters']['scrape_range']:
            self.urls = [ self.source['url'] ]
            self.logger.info('Set start_url to %s' % (self.urls[0],))
        else:
            self.urls = []
            self.logger.info('All requested chapters for series "%s" has already been scraped, exiting gracefully' % (self.config['title'],))

    def closed(self, reason):
        # TODO: need to find a way to detect an exception and then NOT run the packaging class
        if not self.driver:
            try:
                self.driver.execute(Command.STATUS)
                self.driver.quit()
            except:
                pass
        
        # finally, package the content using one of the packaging classes
        package_class = eval('packaging.%s()' % (self.spider_id,))
        package_class.set_config(self.config)
        package_class.run()

        return

    #headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:48.0) Gecko/20100101 Firefox/48.0'}
    def start_requests(self):
        for url in self.urls:
            #request = scrapy.Request(url=url, callback=self.parse, priority=1, dont_filter=True, headers=self.headers)
            request = scrapy.Request(url=url, callback=self.parse, priority=1, dont_filter=True)
            yield request

    def parse(self, response):
        if response.status == 403:
            if 'state' not in response.meta:
                self.logger.info('got 403 error, still going to push forward and open it in a webdriver')
            else:
                self.logger.info('unknown error reached while parsing series %s. Going to try to push forward. URL is: %s' % (self.config['title'],response.url))
        
        self.logger.info('In parse() function for the following URL: %s' % (response.url,))
        if 'state' not in response.meta:
            response.meta['state'] = openSite.__name__.upper()
            self.logger.info("response doesn't have a 'state' field, using %s instead" % (response.meta['state'],))

        if 'driver' not in response.meta:
            response.meta['driver'] = None
            self.logger.info("response doesn't have a 'driver' field, making it a NoneType")

        data = dict( \
                id=response.request.priority, \
                type=TYPE['NOVEL'], \
                executable=self.executable, \
                series=self.config, \
                source=self.source, \
                driver=response.meta['driver'], \
                lock=self.lock, \
                response=response, \
                url=response.url, \
                state=response.meta['state'], \
                metas=response.meta, \
                items=[], \
                requests=[] )
        self.logger.info('About to run the state %s' % (data['state'],))
        data = self.state_machine.run_state(data['state'], data)
        self.logger.info('Finished running state %s' % (data['state'],))

        for idx,request_data in enumerate(data['requests']):
            self.logger.info('Making request to parse() the following URL: %s' % (request_data['url'],))
            meta = dict( \
                driver=request_data['driver'], \
                lock=request_data['lock'], \
                state=request_data['state'] )
            #request = scrapy.Request(url=request_data['url'], callback=self.parse, meta=meta, priority=request_data['priority'], dont_filter=True, headers=self.headers)
            request = scrapy.Request(url=request_data['url'], callback=self.parse, meta=meta, priority=request_data['priority'], dont_filter=True)
            yield request

        for item_data in data['items']:
            item = GenericItem()
            item['content_type'] = self.spider_id
            item['series_name'] = self.config['title']
            item['savepath'] = self.config['savepath']
            item['chapter_name'] = item_data['chapter_name']
            if isinstance(item_data['chapter_id'],int):
                item['chapter_id'] = str(item_data['chapter_id'] - 1)
            else:
                item['chapter_id'] = item_data['chapter_id']
            item['chapter_content'] = item_data['chapter_content']
            self.logger.info('Yielding following item with ID|Name: %s|%s' % (item['chapter_id'], item['chapter_name'],))
            yield item

        if self.state_machine.reached_endState(data['state']):
            # make sure spider has reference to the driver right now
            self.driver = data['driver']

        self.logger.info('Done with parse() function')
