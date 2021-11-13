# helper fcns
from core.states.helpers._common_imports import *
from core.states.helpers.handleNextPage import handleNextPage
from core.states.helpers.handleShowMore import handleShowMore

# next state
from core.states.parseChapterDynamic import parseChapterDynamic
from core.states.parseChapterStatic import parseChapterStatic


def getChapterListDynamic(data, logger):
    # tries to get each chapter's link on a webdriver
    source = data['source']
    driver = data['driver']
    if source['site_type'] == 1:
        state = parseChapterDynamic.__name__
    else:
        state = parseChapterStatic.__name__

    driver.get(data['url'])
    driver = handleShowMore(driver, source['show_more'])

    author_str = []
    for elet in driver.find_elements_by_xpath(source['content_author']):
        author_str.append(elet.text)
    # if it's nonempty, return it in an item to save to file
    # TODO: Make the saved filename something that's in a constants.py file
    data['items'] = [ \
                        dict( \
                            chapter_name='authors', \
                            chapter_id='authors', \
                            chapter_content=author_str ) ]

    # get urls for each chapter
    #
    # TODO: "THIS SHOULD BE IN getChapterListDynamic()"
    # - in a while loop:
    #   - if we have a content_list,
    #     - use it
    #   - else:
    #     - scrape selenium URL
    #   - if we have a next_page:
    #     - use it
    #
    sleep(5)
    has_next_page = True
    cnt = 0
    found_cnt = 0
    while has_next_page:
        if source['content_list']:
            elets = driver.find_elements_by_xpath(source['content_list'])
            for elet in elets:
                url = elet.get_attribute('href')
                if cnt >= len(elets) or not data['series']['chapters']['scrape_range']: # if it's empty, then we've scraped everything
                    break
                elif cnt < max(data['series']['chapters']['scrape_range']) and cnt in data['series']['chapters']['scrape_range']:
                    data['requests'].append(dict(dict( \
                                                driver=driver, \
                                                lock=data['lock'], \
                                                url=url, \
                                                state=state, \
                                                priority=cnt+1)))
                    found_cnt = found_cnt + 1
                    logger.info('Creating request #%d: %s' % (found_cnt, url))
                    data['series']['chapters']['scrape_range'].pop(data['series']['chapters']['scrape_range'].index(cnt))
                cnt = cnt + 1 # increment counter of chapters read
            else:
                continue
            break
        else:
            url = driver.current_url
            if cnt in data['series']['chapters']['scrape_range']:
                data['requests'].append(dict(dict( \
                                            driver=driver, \
                                            lock=data['lock'], \
                                            url=url, \
                                            state=state, \
                                            priority=cnt+1)))
                found_cnt = found_cnt + 1
                logger.info('Creating request #%d: %s' % (found_cnt, url))
                data['series']['chapters']['scrape_range'].pop(data['series']['chapters']['scrape_range'].index(cnt))
            elif not data['series']['chapters']['scrape_range']:
                break
            cnt = cnt + 1 # increment counter of chapters read
        has_next_page, driver = handleNextPage(driver, source['next_page'])
    
    return data

