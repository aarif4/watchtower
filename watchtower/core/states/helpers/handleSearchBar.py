from core.states.helpers._common_imports import *

def handleSearchBar(driver, search_expr, search_word, search_meta, meta_str, search_next_page, target_expr, logger):
    # handles searching for series name and looking for a match
    # if it doesn't find a match, we exit with an error
    if not search_expr:
        return driver, driver.current_url
    elet = driver.find_element_by_xpath(search_expr)
    sleep(3)
    elet.send_keys(search_word)
    sleep(3) # TODO: Figure out how to know if the driver is done loading send_keys() isn't blocking long enough
    elet.send_keys(Keys.RETURN)
    sleep(3)
    if not target_expr:
        series_url = driver.current_url
    else:
        if len(search_meta) and len(meta_str):
            tgt_elet = None
            keep_searching = True
            while keep_searching:
                sleep(3) # TODO: Look into why the author list (a = [a.text for a in elets]) isn't being caught when we're doing a fanfic
                elets = driver.find_elements_by_xpath(search_meta)
                for i,elet in enumerate(elets):
                    if elet.text == meta_str:
                        idx = i
                        keep_searching = False
                
                if keep_searching and len(search_next_page) > 0:
                    elet = driver.find_element_by_xpath(search_next_page)
                    if not elet or elet.text.isdigit():
                        logger.error('Reached last page and could not find the target series with requested metadata....exiting')
                    elet.click()
        else:
            idx = 0

        elet = driver.find_elements_by_xpath(target_expr)
        if len(elet) == 1:
            elet = elet[0]
        elif len(elet) > 1:
            elet = elet[idx]
        else:
            raise Exception('Could not find target series')
        # if there's a "search_meta" and a nonempty meta_str,
        #   while I'm looking for a match:
        #       run this to get all the meta: driver.find_elements_by_xpath(search_meta)
        #       then for each element, look at the text and see which one matches meta_str
        #
        #       if we found a match, 
        #           save target elet to "elet" and break
        #       else, 
        #           continue
        #       if we've reached the end and haven't found a match yet,
        #           if there's a nonempty "search_next_page" value
        #               go to the next page
        series_url = elet.get_attribute('href')

    return driver, series_url