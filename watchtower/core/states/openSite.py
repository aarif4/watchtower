# helper funcs
from core.states.helpers._common_imports import *
from core.states.helpers.getDriver import getDriver
from core.states.helpers.handleSearchBar import handleSearchBar

# next state
from core.states.getChapterListDynamic import getChapterListDynamic
from core.states.getChapterListStatic import getChapterListStatic

def openSite(data, logger):
    # first state that opens a site on a webdriver
    # and navigates to the right series
    # returns using link found in <head> of HTML (same in most places)
    
    source = data['source']

    want_js = source['site_type'] < 3
    logger.info('Opening site, want_js=%s' % (want_js))
    driver = getDriver(want_js, data['executable'])
    logger.info('Site opened')
    driver.maximize_window()
    #driver.minimize_window()
    sleep(3)
    logger.info('Going to URL : %s' % (source['url'],))
    driver.get(source['url'])
    logger.info('Searching for series %s' % (data['series']['title'],))
    driver, series_url = handleSearchBar(\
        driver, source['search_bar'], data['series']['title'], source['search_meta'], data['series']['meta'], source['search_next_page'], source['target_series'], logger)
    
    logger.info('packaging request')
    if want_js:
        state = getChapterListDynamic.__name__
    else:
        state = getChapterListStatic.__name__
    data['requests'] = [ dict( \
                            driver=driver, \
                            lock=None, \
                            url=series_url, \
                            state=state, \
                            priority=1 ) ]
    
    return data
