# helper fcns
from core.states.helpers._common_imports import *

# next state
from core.states.parseChapterStatic import parseChapterStatic


def getChapterListStatic(data, logger): # TODO
    # tries to get each chapter's link from xpath magic
    driver = data['driver']
    source = data['source']
    state = parseChapterStatic.__name__

    driver.get(data['url'])

    author_str = []
    if not source['content_author']:
        author_str = data['series']['authors']
    else:
        for elet in driver.find_elements_by_xpath(source['content_author']):
            author_str.append(elet.text)
    # if it's nonempty, return it in an item to save to file
    # TODO: Make the saved filename something that's in a constants.py file
    data['items'] = [ \
                        dict( \
                            chapter_name='authors', \
                            chapter_id='authors', \
                            chapter_content=author_str ) ]

    # TODO: Must work on this. Need to get an example site to handle this option

    return data
