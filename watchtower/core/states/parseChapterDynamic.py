from core.states.helpers._common_imports import *

def parseChapterDynamic(data, logger):
    # parses content
    data['lock'].acquire()
    
    source = data['source']
    driver = data['driver']
    driver.get(data['url'])

    # TODO: handle captchas

    # read title
    title = driver.find_element_by_xpath(source['content_title']).text

    # read content
    content = []
    if data['type'] == TYPE.NOVEL:
        for chapter_content in driver.find_elements_by_xpath(source['content']):
            text = chapter_content.text
            if len(text) > 0:
                content.append(''.join(text))
    elif data['type'] == TYPE.COMIC:
        raise Exception('Incomplete image parsing functionality') # TODO: Get URLs
        for chapter_content in driver.find_elements_by_xpath(source['content']):
            text = chapter_content.xpath('./@src').extract()
            content.append(text)
    elif data['type'] == TYPE.VIDEO:
        raise Exception('Incomplete video parsing functionality') # TODO: Get URLs

    # package item
    data['items'] = [ \
                        dict( \
                            chapter_name=title, \
                            chapter_id=data['id'], \
                            chapter_content=content ) ]

    data['lock'].release()
    
    return data
