from core.states.helpers._common_imports import *

def handleNextPage(driver, next_page_expr):
    # handles any "next page" buttons that exist while
    # getting a comprehensive list of chapter links
    # TODO: Should have a timeout while we wait for the site to load
    worked = False
    if next_page_expr:
        elet = driver.find_elements_by_xpath(next_page_expr)
        if elet:
            elet.click()
            sleep(3)
            worked = True
    
    return worked, driver
