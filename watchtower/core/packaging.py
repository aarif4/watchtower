from abc import abstractclassmethod
import os
import re
import glob
import shutil
import zipfile
from xml.etree import ElementTree

class GenericPackage:
    config = None
    def set_config(self, config):
        self.config = config

    @abstractclassmethod
    def run(self):
        pass

class Novel(GenericPackage):
    # compare the resulting epub here: https://draft2digital.com/book/epubcheck/upload
    publisher = 'ZER0SUM'
    bookid = '48cf70a2-24a6-11ea-978f-2e728ce88125'
    def run(self):
        # for each volume,
        # - create directories and get paths
        # - copy over the illustration photos
        # - find the raw files you will use for this volume
        # - convert them to xhtml raw files (sterilize first)
        # - create title page and illustration page files
        # - create additional epub metadata files
        # - compress this filetree into an epub file
        savepath = '/'.join([self.config['savepath'], self.config['title']])
        rawspath = '/'.join([savepath,'raws'])
        for idx,vol in enumerate(self.config['volumes']):
            idx = idx + 1
            # create build folder to store uncompressed epub data
            vol_name = vol['name']
            if not vol_name:
                vol_name = 'Volume %d' % (idx,)
                vol_id = '%s - %s' % (self.config['title'], vol_name)
            else:
                vol_id = '%s - Volume %d - %s' % (self.config['title'], idx, vol_name)
            vol_folderpath = '/'.join([savepath,'build',vol_id])
            self.create_dirs(vol_folderpath)

            # make metadata files that are required for EPUBs
            metadata_info = self.create_epub_metadata_pages(vol_folderpath)

            # copy over all pictures to the proper directory
            image_info = self.copy_image_files_and_create_pages(
                            vol_folderpath, 
                            vol['photos'])
            
            # look for author rawfile and make a title page
            
            title_info = self.create_title_page(
                            vol_folderpath, 
                            rawspath, 
                            self.config['title'], 
                            vol_name)

            # work on raw files
            raws_info = self.convert_raw_files_to_pages(
                            vol_folderpath, 
                            rawspath, 
                            vol['chapters']['start'], 
                            vol['chapters']['stop'] )
            if not len(raws_info):
                continue # if we don't have any raws to make an epub, don't make it

            # make TOC pages
            self.create_epub_table_of_contents(
                vol_folderpath, 
                rawspath, 
                self.config['title'], 
                vol_id, 
                image_info, 
                title_info, 
                raws_info )


            self.compress_epub(vol_folderpath, savepath, vol_id)

    def create_dirs(self, buildfolderpath):
        # We're making the following directory:
        # ${folderpath}:
        # ├── mimetype (independent of raws)                @create_dirs
        # ├── META-INF/
        # |   └── container.xml (independent of raws)       @create_dirs
        # └── OEBPS/
        #     ├── content.opf                               @create_epub_table_of_contents
        #     ├── toc.ncx                                   @create_epub_table_of_contents
        #     ├── Image/
        #     |   └── *.png ... (images)                    @copy_image_files_and_create_pages
        #     └── Text/
        #         ├── #-***.xhtml ... (raw chapters)        @convert_raw_files_to_pages
        #         ├── cover.xhtml                           @copy_image_files_and_create_pages
        #         └── title_page.xhtml                      @create_title_page

        # Let's first make that filetree using recursive os.makedirs
        os.makedirs('/'.join([buildfolderpath,'META-INF']), exist_ok=True)
        os.makedirs('/'.join([buildfolderpath,'OEBPS','Text']), exist_ok=True)
        os.makedirs('/'.join([buildfolderpath,'OEBPS','Image']), exist_ok=True)

    def create_epub_metadata_pages(self, buildfolderpath):
        # return several list-of-strings for
        # container.xml, mimetype
        content_data = [ \
            '<?xml version="1.0"?>',
            '<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">',
            '<rootfiles>',
            '<rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>',
            '</rootfiles>',
                '</container>' ]
        content_relpath = '/'.join(['META-INF','container.xml'])
        mimetype_data = ['application/epub+zip']
        mimetype_relpath = 'mimetype'

        d = dict()
        d[content_relpath] = content_data
        self.save_file(buildfolderpath, content_relpath, content_data)
        d[mimetype_relpath] = mimetype_data
        self.save_file(buildfolderpath, mimetype_relpath, mimetype_data, True)
        
        dd = []
        for key in d.keys():
            dd.append(dict(relpath=key,title='',key=''))
        return dd
    
    def copy_image_files_and_create_pages(self, buildfolderpath, photo_dict):
        img_titles = []
        img_keys = []
        d = dict()
        for key,val in photo_dict.items():
            if val:
                img_keys.append(key)
                # copy the image over to the proper location
                imgfilepath = '/'.join([buildfolderpath,'OEBPS','Image',os.path.basename(val)])
                # TODO: Verify that this file actually exists....maybe do this in config.py?
                shutil.copyfile(val, imgfilepath)

                # make xhtml files for this image
                key_title = key.replace('_', ' ').title()
                img_titles.append(key_title)
                d_tmp = self.create_image_page(
                        key,
                        key == 'front_cover',
                        key_title,
                        os.path.relpath(imgfilepath, buildfolderpath) )
                for key,val in d_tmp.items():
                    d[key] = val
        
        for key,val in d.items():
            self.save_file(buildfolderpath, key, val)
        
        dd = []
        for idx,relpath in enumerate(d.keys()):
            dd.append(dict(relpath=relpath,title=img_titles[idx],key=img_keys[idx]))
        return dd

    def convert_raw_files_to_pages(self, buildfolderpath, rawfolderpath, start_val, stop_val):
        raw_files = self.find_target_raw_files(rawfolderpath, start_val, stop_val)
        file_data, file_info = self.convert_raw_file_to_xhtml(buildfolderpath, raw_files)
        for key,val in file_data.items():
            self.save_file(buildfolderpath, key, val)
        
        return file_info

    def find_target_raw_files(self, rawfolderpath, start_val, stop_val):
        # find the raw files that fit the targeted start/stop chapter num
        # and return list of paths
        raw_files = []
        # first, find the target filenames you want to use
        for file_num in range(start_val, stop_val+1):
            target_file = '/'.join([rawfolderpath,'%d.txt' % (file_num,)])
            if os.path.isfile(target_file):
                raw_files.append(target_file)

        #for file in os.listdir(rawfolderpath):
        #    val = os.path.basename(file).split('.')[0]
        #    if val != 'authors':
        #        int_val = int(val)
        #        if int_val >= start_val and int_val <= stop_val:
        #            raw_files.append('/'.join([rawfolderpath,file]))
        return raw_files

    def convert_raw_file_to_xhtml(self, buildfolderpath, raw_files):
        # edit the txt file into xhtml file
        # and return it as a list of strings along with their relpath
        d = dict()
        dd = []
        for file in raw_files:
            content = []
            with open(file,'r',encoding='utf-8') as f:
                content = f.readlines()
                content = [data[0:-1] for data in content if data[-1] == '\n']
            title, body = self.sterilize_raw_file_contents(content)
            xhtml_content = [   '<?xml version=\"1.0\" encoding=\"utf-8\"?>',
                            '<!DOCTYPE html PUBLIC \"-//W3C//DTD XHTML 1.1//EN\"',
                            '\"http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd\">',
                            '<html xmlns=\"http://www.w3.org/1999/xhtml\">',
                            '<head><title>%s</title></head>' % (title,)] + \
                        [   '<body>','<h1>%s</h1>' % (title,)] + \
                        [   '<p>'+line+'</p>' for line in body] + \
                        [   '</body>',
                            '</html>']
            filename = os.path.basename(file).split('.')[0]
            #filename = '-'.join([filename, re.sub('[^a-zA-Z0-9]', '', title)])
            relpath = '/'.join(['OEBPS','Text', '%s.xhtml' % (filename,)])
            d[relpath] = xhtml_content
            dd.append(dict(relpath=relpath,title=title,key=filename))
        return d, dd

    def sterilize_raw_file_contents(self, content):
        # clean up text file from symbols
        content = [w.replace('\n', '') for w in content]
        title_content = content[0]
        title_content = re.sub('[^a-zA-Z0-9 ]', '', title_content)
        content = content[1:]
        content = [w.replace('&', '&amp;') for w in content]
        content = [w.replace('<', '&lt;') for w in content]
        content = [w.replace('>', '&gt;') for w in content]

        # TODO: Should look at first two lines and verify that it's not repeating
        # TODO: Perhaps also look for "][" moments and split those into their own lines
        return title_content, content

    def get_author_raw_file_contents(self, rawfolderpath):
        authors_str = ''
        for file in os.listdir(rawfolderpath):
            if file.split('.')[0] == 'authors':
                with open('/'.join([rawfolderpath,file]),'r', encoding='utf-8') as f:
                    authors_str = f.readlines()
                    authors_str = [data[0:-1] for data in authors_str if data[-1] == '\n']
                    break
        
        if isinstance(authors_str, list):
            if len(authors_str) <= 1:
                raise Exception('This should never happen. Author list must always be greater than 1')
            authors_str = authors_str[1:] # skip the first entry
            if len(authors_str) > 1:
                # add the "and" phrase for more than one author
                authors_str[-1] = ' '.join(['and', authors_str[-1]])
            
            authors_str = ', '.join(authors_str)
        return authors_str

    def create_title_page(self, buildfolderpath, rawspath, series_name, vol_title):
        authors_str = self.get_author_raw_file_contents(rawspath)

        # make a title page with the proper setup
        title_content = [ '<?xml version="1.0" encoding="utf-8"?>',
                        '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN"',
                        '"http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">',
                        '<html xmlns="http://www.w3.org/1999/xhtml">',
                        '<head>',
                        '<title>',
                        series_name,
                        '</title>',
                        '</head>',
                        '<body>',
                        '<h1 style="text-align:center">%s</h1>' % (series_name,),
                        '<h2 style="text-align:center">%s</h2>' % (vol_title,),
                        '<h3 style="text-align:center">By %s</h3>' % (authors_str),
                        '</body>',
                        '</html>' ]
        title_key = 'title_page'
        title_relpath = '/'.join(['OEBPS','Text','%s.xhtml' % (title_key,)])

        d = dict()
        d[title_relpath] = title_content

        for key,val in d.items():
            self.save_file(buildfolderpath, key, val)

        dd = [dict(relpath=title_relpath,title=series_name,key=title_key)]
        return dd

    def create_image_page(self, title_key, is_front_page, title, raw_img_path):
        imagepath = '/'.join(['OEBPS','Text','%s.xhtml' % (title_key,)])
        raw_img_path = os.path.relpath(raw_img_path,'OEBPS').replace('\\','/')
        # make page for images
        image_content = [
                '<?xml version="1.0" encoding="utf-8"?>',
                '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN"',
                '  "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">',
                '<html xmlns="http://www.w3.org/1999/xhtml">',
                '<head>',
                '<title>%s</title>' % (title,),
                '</head>',
                '<body>']
        if is_front_page:
            image_content.extend([
                '<div style="text-align: center; padding: 0pt; margin: 0pt; ">',
                '<svg xmlns="http://www.w3.org/2000/svg" height="100%" preserveAspectRatio="xMidYMid meet" version="1.1" viewBox="0 0 394 576" width="100%" xmlns:xlink="http://www.w3.org/1999/xlink" style="background-color: #000000;">',
                '<image width="100%%" height="560" xlink:href="..%s%s" style="background-position: center top; background-repeat: no-repeat; background-size: cover;"/>' % ('/', raw_img_path),
                '</svg>',
                '</div>' ])
        else:
            image_content.extend([
                '<div style="text-align: center; page-break-after: always; page-break-inside: avoid; clear: both; padding: 0px; margin: 0em auto; height: 95%;">',
		        '<img alt="%s Photo" src="..%s%s"/>' % (title, '/', raw_img_path),
	            '</div>' ])
        image_content.extend(['</body>', '</html>'])

        d = dict()
        d[imagepath] = image_content

        return d

    def create_epub_table_of_contents(self, buildfolderpath, rawspath, series_name, vol_id, image_info, title_info, raws_info): # TODO
        # get toc.ncx file content
        toc_info = self.create_toc_ncx_page(
                        buildfolderpath, 
                        series_name, 
                        vol_id, 
                        title_info, 
                        raws_info )
        
        # now get content.opf file content
        content_info = self.create_content_opf_page(
                            buildfolderpath,
                            rawspath,  
                            series_name, 
                            vol_id, 
                            image_info, 
                            title_info, 
                            raws_info )
        
        return [toc_info, content_info]
        
    def create_toc_ncx_page(self, buildfolderpath, series_name, vol_id, title_info, raws_info): # TODO
        d = dict()
        vol_id = vol_id.replace('-', ' - ', 1)
        toc_relpath = '/'.join(['OEBPS', 'toc.ncx'])
        toc_content = [ '<?xml version="1.0" encoding="UTF-8"?>',
                        '<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1">',
                        '<head>',
                        '<meta name="dtb:uid" content="%s"/>' % (self.bookid,),
                        '<meta name="dtb:depth" content="1"/>',
                        '<meta name="dtb:totalPageCount" content="0"/>',
                        '<meta name="dtb:maxPageNumber" content="0"/>',
                        '</head>',
                        '<docTitle>',
                        '<text>%s - Volume %s</text>' % (series_name, vol_id),
                        '</docTitle>',
                        '<navMap>']
        cnt = 0
        title_data = []
        for info in title_info:
            #content_tree = ElementTree.ElementTree(ElementTree.fromstringlist(file_content))
            #name = content_tree.find('title').text
            #name_id = re.sub(r'[^A-Za-z0-9]', '', name)
            name_id = re.sub(r'[^A-Za-z0-9]', '', info['key'])
            #file_relpath = os.path.relpath(filepath, start=buildfolderpath)
            title_data.append(dict(id=name_id, playOrder=cnt, name=info['title'], src=info['relpath']))
            toc_content.extend([ '<navPoint id="%s" playOrder="%d">' % (name_id, cnt),
                        '<navLabel>',
                        '<text>%s</text>' % (info['title'],),
                        '</navLabel>',
                        '<content src="%s"/>' % (os.path.relpath(info['relpath'],'OEBPS').replace('\\','/'),),
                        '</navPoint>'])
            cnt = cnt + 1
        raw_data = []
        for info in raws_info:
            #content_tree = ElementTree.ElementTree(ElementTree.fromstringlist(file_content))
            #name = content_tree.find('title').text
            name_id = re.sub(r'[^A-Za-z0-9]', '', info['key'])
            #file_relpath = os.path.relpath(filepath, start=buildfolderpath)
            raw_data.append(dict(id=name_id, playOrder=cnt, name=info['title'], src=info['relpath']))
            toc_content.extend([ '<navPoint id="%s" playOrder="%d">' % (name_id, cnt),
                        '<navLabel>',
                        '<text>%s</text>' % (info['title'],),
                        '</navLabel>',
                        '<content src="%s"/>' % (os.path.relpath(info['relpath'],'OEBPS').replace('\\','/'),),
                        '</navPoint>'])
            cnt = cnt + 1
        
        toc_content.extend(['</navMap>', '</ncx>'])
        d[toc_relpath] = toc_content

        for key,val in d.items():
            self.save_file(buildfolderpath, key, val)
        
        dd = [dict(relpath=toc_relpath,title='',key='toc')]
        return dd

    def create_content_opf_page(self, buildfolderpath, rawspath, series_name, vol_id, image_info, title_info, raws_info): # TODO
        # each "*_info" var is a dict with fields: relpath, title, key
        images_relpath = os.sep.join(['OEBPS','Image'])
        images_path = '/'.join([buildfolderpath, images_relpath])
        d = dict()
        content_relpath = '/'.join(['OEBPS', 'content.opf'])
        content_content = [
            '<?xml version="1.0"?>',
            '<package version="2.0" xmlns="http://www.idpf.org/2007/opf" unique-identifier="BookId">',
            '<metadata xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:opf="http://www.idpf.org/2007/opf">',
            '<dc:title>%s - Volume %s</dc:title>' % (series_name, vol_id),
            '<dc:creator opf:role="aut">%s</dc:creator>' % (self.get_author_raw_file_contents(rawspath)),
            '<dc:language>en-US</dc:language>',
            '<dc:rights>Public Domain</dc:rights>',
            '<dc:publisher>%s</dc:publisher>' % (self.publisher,),
            '<dc:identifier id="BookId">%s</dc:identifier>' % (self.bookid,),
            '</metadata>']
        
        # first start with title, then raws, then images and their xhtml images
        manifest_content = ['<manifest>']
        for info in title_info:
            manifest_content.append('<item id="%s" href="%s" media-type="application/xhtml+xml" />' % (info['key'], os.path.relpath(info['relpath'],'OEBPS').replace('\\','/')))
        manifest_content.append('<item id="ncx" href="toc.ncx" media-type="application/x-dtbncx+xml"/>')
        for info in raws_info:
            manifest_content.append('<item id="%s" href="%s" media-type="application/xhtml+xml" />' % (info['key'], os.path.relpath(info['relpath'],'OEBPS').replace('\\','/')))
        for image in os.listdir(images_path):
            # key can be: 'front_cover', 'illustration', 
            key_id = re.sub(r"[^A-Za-z0-9]", "", image.split('.')[0])
            relpath = os.path.relpath('/'.join([images_relpath, image]),'OEBPS').replace('\\','/')
            ext = image.split('.')[1]
            if ext == 'png':
                media_type = 'image/png'
            elif ext == 'jpg' or ext == 'jpeg':
                media_type = 'image/jpeg'
            elif ext ==  'gif':
                media_type = 'image/gif'
            elif ext == 'svg':
                media_type = 'image/svg+xml'
            else:
                raise Exception("INVALID IMAGE FILE TYPE")
            manifest_content.append('<item id="%s" href="%s" media-type="%s" />' % (key_id, relpath, media_type))
        for info in image_info:
            manifest_content.append('<item id="%s" href="%s" media-type="application/xhtml+xml" />' % (info['key'], os.path.relpath(info['relpath'],'OEBPS').replace('\\','/')))
        manifest_content.append('</manifest>')

        # TODO: then make the spine starting with xhtml images, title, then raws, then back_cover
        spine_content = ['<spine toc="ncx">']
        for info in image_info:
            if info['key'] == 'front_cover':
                spine_content.append('<itemref idref="%s"/>' % (info['key'],))
        for info in title_info:
            spine_content.append('<itemref idref="%s"/>' % (info['key'],))
        for info in image_info:
            if info['key'] != 'front_cover':
                spine_content.append('<itemref idref="%s"/>' % (info['key'],))
        for info in raws_info:
            spine_content.append('<itemref idref="%s"/>' % (info['key'],))
        spine_content.append('</spine>')

        # Finally, put everything into content_content
        content_content.extend(manifest_content)
        content_content.extend(spine_content)
        content_content.append('</package>')
        
        d[content_relpath] = content_content
        for key,val in d.items():
            self.save_file(buildfolderpath, key, val)
        
        dd = [dict(relpath=content_relpath,title='',key='content')]
        return d

    def save_file(self, buildfolderpath, file_relpath, file_content, no_newline=False):
        # save list-of-string to the proper location
        filepath = '/'.join([buildfolderpath, file_relpath])
        with open(filepath,'w+', encoding='utf-8') as f:
            nl = '\n'
            if no_newline:
                nl = ''
            f.writelines([val + nl for val in file_content])

    def compress_epub(self, buildfolderpath, savepath, vol_id):
        # compress files to make epub file
        epub_path = '%s%s%s.epub' % (savepath, '/', vol_id)
        zipf = zipfile.ZipFile(epub_path, 'w', zipfile.ZIP_STORED)
        for root, _, files in os.walk(buildfolderpath):
            for File in files:
                filepath = os.path.join(root, File)
                relpath = os.path.relpath(filepath,start=buildfolderpath)
                zipf.write(filepath, relpath)
        zipf.close()

class Comic(GenericPackage):
    def run(self):
        raise Exception('Comic packaging is not ready yet')

class Video(GenericPackage):
    def run(self):
        raise Exception('Video packaging is not ready yet')
