from core.states.helpers._common_imports import *

def parseChapterStatic(data, logger):
    source = data['source']
    response = data['response']

    # read title
    title = response.xpath(source['content_title']).xpath('.//text()')
    if len(title) > 0:
        title = title.extract()[0]
    else:
        title = 'Chapter %d' % (data['id'])

    # read content
    content = []
    if data['type'] == TYPE.NOVEL:
        if 'content_concat' not in source:
            source['content_concat'] = ''
        for chapter_content in response.xpath(source['content']):
            text = chapter_content.xpath('.//text()').extract()
            if len(text) > 0:
                #content.append('\n'.join(text))
                content.append(source['content_concat'].join(text))
    elif data['type'] == TYPE.COMIC:
        # TODO: Verify this
        for chapter_content in response.xpath(source['content']):
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

    return data
