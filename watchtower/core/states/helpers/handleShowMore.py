from core.states.helpers._common_imports import *

def handleShowMore(driver, show_more_expr):
    # handles any "Show More" buttons that pop up when you're looking
    # for a complete list of chapters
    # (mostly happens initally)
    if show_more_expr:
        elet = driver.find_element_by_xpath(show_more_expr)
        if elet:
            elet.click()
            sleep(3)
    
    return driver
